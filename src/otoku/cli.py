"""python -m otoku <command>（5章）：collect・send・sync・remind・check-sources。"""
from __future__ import annotations

import argparse
import fcntl
import logging
import logging.handlers
import sys
import time
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, TextIO

from .collectors import FetchError, Fetcher, ParseError
from .collectors.check import check_sources
from .collectors.parse import parse_source
from .feedback.reactions import adjust_weights, sync, weekly_report
from .feedback.reminder import remind
from .db import Store
from .models import JST, Config, Env, Source, load_config, load_env, load_sources, utcnow
from .notify.discord import REACTIONS, DiscordClient, DiscordError, LogChannel
from .notify.format import action_message, error_line, log_line, paused_line, stores_of
from .pipeline.dedupe import content_hash, url_hash
from .pipeline.extract import AIUnavailable, Extractor
from .pipeline.group import group_key
from .pipeline.rules import RuleFilter
from .pipeline.score import is_urgent, score
from .pipeline.select import in_slot, is_quiet, jst_day_bounds, make_units, plan
from .pipeline.validate import promote_waiting, validate

ROOT = Path(__file__).resolve().parents[2]
log = logging.getLogger("otoku")


@dataclass
class SourceSummary:
    fetched: int = 0
    new: int = 0
    rule_pass: int = 0
    ai: int = 0
    note: str = ""


@dataclass
class Summary:
    sources: dict[str, SourceSummary] = field(default_factory=dict)
    skipped: Counter = field(default_factory=Counter)
    rule_drops: Counter = field(default_factory=Counter)
    kinds: Counter = field(default_factory=Counter)
    statuses: Counter = field(default_factory=Counter)
    ai_calls: int = 0
    ai_skipped: int = 0
    errors: list[str] = field(default_factory=list)




def run_collect(*, cfg: Config, sources: list[Source], store: Store, fetcher: Fetcher,
                extractor: Optional[Extractor], log_channel: LogChannel, now: Optional[datetime] = None) -> Summary:
    """収集 → 重複排除 → ルール → AI → 検証 → #ログ。extractor が None なら AI判定をしない（dry-run で鍵がないとき）。"""
    now = now or utcnow()
    summary = Summary()
    rules = RuleFilter(cfg.keywords.include, cfg.keywords.exclude)
    tolerance = timedelta(seconds=cfg.collect.interval_tolerance_seconds)
    ai_ok = True

    for status, title, source_id in promote_waiting(store, now):
        log_channel.add(log_line(status, "開始時刻を過ぎたので再評価", title, source_id))
        summary.statuses[f"waiting→{status}"] += 1
    store.commit()

    for src in sources:
        if not src.enabled:
            continue
        state = store.source_state(src.id)
        if state.paused_until and state.paused_until > now:
            summary.skipped["停止中"] += 1
            continue
        if state.last_fetched_at and now + tolerance < state.last_fetched_at + timedelta(minutes=src.min_interval_minutes):
            summary.skipped["間隔待ち"] += 1
            continue

        ss = summary.sources.setdefault(src.id, SourceSummary())
        try:
            res = fetcher.get(src.url, etag=state.etag, last_modified=state.last_modified)
            raws = [] if res.status == 304 else parse_source(src, res, now)
        except (FetchError, ParseError) as e:
            streak = state.fail_streak + 1
            ss.note = f"失敗 {streak}回目: {e}"
            summary.errors.append(f"{src.id}: {e}")
            log.warning("取得失敗 %s（%d回目）: %s", src.id, streak, e)
            if streak >= cfg.collect.fail_pause_after:
                store.pause(src.id, now + timedelta(hours=cfg.collect.pause_hours))
                log_channel.add(paused_line(src.id, streak, cfg.collect.pause_hours))
            else:
                store.set_fail_streak(src.id, streak)
            store.commit()
            continue
        if res.status == 304:
            ss.note = "更新なし（304）"
            store.mark_fetched(src.id, now, res.etag, res.last_modified)
            store.commit()
            continue

        ss.fetched = len(raws)
        if not raws and src.type == "html_diff":
            ss.note = "監視対象のリンク0件"
            log.warning("%s: 監視対象のリンクが0件（実施中がないか、ページの作りが変わった）", src.id)
        complete = True  # この情報源の新着を全部処理できたか。できなければ取得の記録を更新せず、次回取り直す
        for raw in raws:
            h = url_hash(raw.url)
            if store.seen(h):
                continue
            ss.new += 1
            ok, why = rules.check(raw.title, raw.body)
            if not ok:
                summary.rule_drops[why] += 1
                store.add_raw(raw, h, content_hash(raw.title, raw.body), now)
                continue
            ss.rule_pass += 1
            if extractor is None:
                summary.ai_skipped += 1
                store.add_raw(raw, h, content_hash(raw.title, raw.body), now)
                continue
            if not ai_ok:
                complete = False
                continue
            try:
                x = extractor.extract(raw, src, now)
            except AIUnavailable as e:
                ai_ok = complete = False
                summary.errors.append(f"gemini: {e}")
                log_channel.add(error_line("gemini", f"AIを呼べないため、この回の残りは次回に回します（{e}）"))
                continue
            ss.ai += 1
            raw_id = store.add_raw(raw, h, content_hash(raw.title, raw.body), now)
            if x is None:
                store.add_item(raw_id, scope=None, kind="excluded", status="dropped", exclude_reason="AI応答不正",
                               created_at=now)
                summary.kinds["AI応答不正"] += 1
                summary.statuses["dropped"] += 1
                log_channel.add(log_line("dropped", "AI応答不正", raw.title, src.id))
                continue
            v = validate(x, now, min_confidence=cfg.min_confidence, genres_enabled=cfg.genres_enabled)
            item_id = store.add_item(raw_id, scope=v.scope, kind=x.kind, status=v.status, created_at=now, genre=x.genre,
                           product=x.product, organizer=x.organizer, start_at=v.start_at, deadline_at=v.deadline_at,
                           conditions=x.conditions[:60], cost_yen=x.cost_yen, benefit_yen=x.benefit_yen,
                           apply_url=x.apply_url, first_come=x.first_come, confidence=x.confidence,
                           exclude_reason=v.reason if v.status == "dropped" else None)
            key = group_key(v.scope, x.product) if v.status in ("candidate", "waiting") else None
            if key:  # 8.5 グルーピング（同じ商品・同じ企画を1件に）
                store.assign_group(item_id, v.scope, key, x.product, now, src.id)
            summary.kinds[x.kind] += 1
            summary.statuses[v.status] += 1
            log_channel.add(log_line(v.status, v.reason, raw.title, src.id))
        if complete:
            store.mark_fetched(src.id, now, res.etag, res.last_modified)
        else:
            store.reset_fail_streak(src.id)
        store.commit()

    if extractor is not None:
        summary.ai_calls = extractor.calls
    return summary


def format_summary(s: Summary, *, dry_run: bool, now: datetime) -> str:
    def counts(c: Counter) -> str:
        return " / ".join(f"{k} {v}" for k, v in c.most_common()) or "なし"

    fetched = sum(x.fetched for x in s.sources.values())
    new = sum(x.new for x in s.sources.values())
    passed = sum(x.rule_pass for x in s.sources.values())
    judged = sum(x.ai for x in s.sources.values())
    lines = [
        f"=== collect{'（dry-run）' if dry_run else ''} {now.astimezone(JST):%Y-%m-%d %H:%M} JST ===",
        f"情報源: 取得 {len(s.sources)} / スキップ {counts(s.skipped)}",
        f"取得件数 {fetched} / 新規 {new} / ルール通過 {passed} / AI判定 {judged}（呼び出し {s.ai_calls}回）"
        + (f" / AI未実行 {s.ai_skipped}" if s.ai_skipped else ""),
        f"AI判定の内訳: {counts(s.kinds)}",
        f"検証の結果: {counts(s.statuses)}",
        f"送信候補数（candidate）: {s.statuses.get('candidate', 0)}",
        f"ルールで落とした理由: {counts(s.rule_drops)}",
        "情報源別（取得 / 新規 / ルール通過 / AI判定）:",
    ]
    for sid, x in s.sources.items():
        lines.append(f"  {sid}: {x.fetched} / {x.new} / {x.rule_pass} / {x.ai}" + (f"  {x.note}" if x.note else ""))
    if s.errors:
        lines.append("エラー: " + " | ".join(s.errors))
    return "\n".join(lines)


def _setup_logging(dry_run: bool) -> None:
    if log.handlers:
        return
    log.setLevel(logging.INFO)
    stderr = logging.StreamHandler(sys.stderr)
    # 本番は cron から動くので、画面（cron のメール）には重大なものだけ出す。詳細はファイルと #ログ へ
    stderr.setLevel(logging.WARNING if dry_run else logging.ERROR)
    log.addHandler(stderr)
    if not dry_run:  # 12章：ファイルにも出し、14日でローテーション（dry-run はファイルを書かない）
        (ROOT / "data" / "logs").mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.TimedRotatingFileHandler(ROOT / "data" / "logs" / "otoku.log", when="midnight",
                                                       backupCount=14, encoding="utf-8")
        fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        fmt.converter = lambda *_: datetime.now(JST).timetuple()
        fh.setFormatter(fmt)
        log.addHandler(fh)


def _lock(path: Path, wait_seconds: float, sleep=time.sleep):
    """多重起動を防ぐ（9章）。別の実行が終わるのを wait_seconds 秒まで待ち、取れなければ None。
    12:00・19:00 は collect と send が同時に起動するので、すぐにあきらめると選定枠を逃すため待つ。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    f = open(path, "w")
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return f
        except BlockingIOError:
            if time.monotonic() >= deadline:
                f.close()
                return None
            sleep(1)


def cmd_collect(args, cfg: Config, sources: list[Source], env: Env, out: TextIO = sys.stdout) -> int:
    dry_run = args.dry_run
    if not dry_run:
        missing = [name for name, value in (("GEMINI_API_KEY", env.gemini_api_key),
                                            ("DISCORD_BOT_TOKEN", env.discord_bot_token),
                                            ("DISCORD_CHANNEL_LOG", env.discord_channel_log),
                                            ("CONTACT", env.contact)) if not value]
        if missing:
            print(f".env に {', '.join(missing)} がありません（.env.example を参照）", file=sys.stderr)
            return 2
        lock = _lock(ROOT / "data" / "otoku.lock", cfg.lock_wait_seconds)
        if lock is None:
            log.error("別の otoku の実行が %d 秒たっても終わらないため、collect を終了します", cfg.lock_wait_seconds)
            return 0
    if not env.contact:
        print("注意: .env に CONTACT がないため、User-Agent に連絡先が入りません", file=sys.stderr)
    extractor = None
    if env.gemini_api_key:
        prompt = (ROOT / "config" / "prompts" / "extract.md").read_text(encoding="utf-8")
        extractor = Extractor(cfg.gemini, prompt, api_key=env.gemini_api_key)
    else:
        print("注意: .env に GEMINI_API_KEY がないため、AI判定はしません（ルールフィルタまで）", file=sys.stderr)

    discord = None if dry_run else DiscordClient(env.discord_bot_token, max_429_retries=cfg.discord.max_429_retries)
    log_channel = LogChannel(dry_run=dry_run, max_chars=cfg.discord.max_message_chars, client=discord,
                             channel_id=env.discord_channel_log, outbox=ROOT / "data" / "discord_outbox.jsonl",
                             out=out)
    store = Store(ROOT / "data" / "otoku.db", dry_run=dry_run)
    fetcher = Fetcher(contact=env.contact, timeout=cfg.collect.timeout_seconds,
                      host_spacing=cfg.collect.host_spacing_seconds, retry=cfg.collect.retry)
    now = utcnow()
    try:
        summary = run_collect(cfg=cfg, sources=sources, store=store, fetcher=fetcher, extractor=extractor,
                              log_channel=log_channel, now=now)
    finally:
        failed = log_channel.flush()
        fetcher.close()
        store.close()
    if failed:
        log.warning("#ログ に送れなかったメッセージ %d 件を次回に回します", len(failed))
    text = format_summary(summary, dry_run=dry_run, now=now)
    log.info("%s", text.replace("\n", " | "))
    if dry_run:
        print(text, file=out)
    return 0


# ---------------------------------------------------------------- send（フェーズ2）

@dataclass
class SendSummary:
    mode: str
    note: str = ""
    candidates: list = field(default_factory=list)
    eligible: int = 0
    sent_before: int = 0
    remaining: int = 0
    sent: list = field(default_factory=list)
    updated: list = field(default_factory=list)
    duplicates: int = 0
    expired: Counter = field(default_factory=Counter)
    errors: list[str] = field(default_factory=list)


def _store_key(name: Optional[str]) -> str:
    return "".join(ch for ch in (name or "").lower() if ch.isalnum())


def _apply_updates(cfg, store, log_channel, now, client, channel_id, out, s: "SendSummary", items) -> None:
    """送信済みのグループに入った候補（8.5）。Aで新しい店舗なら元のメッセージを編集して追記し（上限に数えない）、
    それ以外（同じ店舗、Bの同じ企画）は重複として落とす。"""
    by_group: dict[int, list] = {}
    for c in items:
        by_group.setdefault(c.group_id, []).append(c)
    for group_id, new in by_group.items():
        sent = store.sent_in_group(group_id)
        known = {_store_key(c.organizer) for c in sent}
        added = [c for c in new if c.scope == "A" and _store_key(c.organizer) and _store_key(c.organizer) not in known]
        if not added:
            for c in new:
                store.set_item_status(c.id, "dropped", "重複（通知済み）")
                s.duplicates += 1
                log_channel.add(log_line("dropped", "重複（通知済み）", c.title, c.source_id, c.score))
            continue
        message_id = new[0].group_message_id
        text = action_message(sent + new)
        if client is None:
            print("\n".join(f"#行動（編集） {line}" for line in text.splitlines()), file=out)
        else:
            try:
                client.edit_message(channel_id, message_id, text)
            except DiscordError as e:  # 候補のまま残り、次の実行で編集し直す
                s.errors.append(f"#行動 編集: {e}")
                log_channel.add(error_line("#行動", f"メッセージを編集できませんでした。次回やり直します（{e}）"))
                continue
        store.mark_updated(new, group_id, message_id, now)
        store.commit()
        s.updated.extend(new)
        n = len(stores_of(sent + new))
        for c in added:
            log_channel.add(log_line("update", f"店舗を追記（{n}店）", c.title, c.source_id, c.score))


def run_send(*, cfg: Config, store: Store, log_channel: LogChannel, now: datetime, urgent_only: bool,
             client: Optional[DiscordClient], channel_id: str = "", out: TextIO = sys.stdout) -> SendSummary:
    """8.7 送信選定と 8.8 #行動 への通知。client が None なら dry-run（送らずに標準出力へ）。"""
    if is_quiet(now, cfg.quiet_hours["start"], cfg.quiet_hours["end"]):
        return SendSummary(mode="静音時間", note="静音時間なので送りません")
    s = SendSummary(mode="緊急のみ" if urgent_only else "通常")
    live = []
    for c in store.candidates():
        if c.deadline_at and c.deadline_at < now:  # 静音時間明けの7:00に、7:00より前の締切のものもここで落ちる
            store.set_item_status(c.id, "expired")
            s.expired["締切が過去"] += 1
            log_channel.add(log_line("expired", "締切が過去", c.title, c.source_id))
            continue
        c.score = score(c, now, cfg.weights, store.source_weight(c.source_id))
        c.urgent = is_urgent(c, now, cfg.send.urgent_within_hours)
        store.set_score(c.id, c.score)
        live.append(c)
    s.candidates = live
    _apply_updates(cfg, store, log_channel, now, client, channel_id, out, s,
                   [c for c in live if c.group_message_id])
    units = make_units([c for c in live if not c.group_message_id])
    day_start, day_end = jst_day_bounds(now)
    s.sent_before = store.count_sent(day_start, day_end)
    p = plan(units, threshold=cfg.score_threshold, remaining=cfg.daily_cap - s.sent_before, urgent_only=urgent_only)
    s.eligible, s.remaining = p.eligible, p.remaining

    failed = False
    for u in p.send:
        text = action_message(u.items)
        title = max(u.items, key=lambda c: c.score or 0.0)
        if client is None:
            print("\n".join(f"#行動 {line}" for line in text.splitlines()), file=out)
            s.sent.append(u)
            log_channel.add(log_line("sent", None, title.title, title.source_id, u.score))
            continue
        try:
            message_id = client.post_message(channel_id, text, suppress_embeds=True)
        except DiscordError as e:  # 送れなかったものは候補のまま残り、次の実行で送り直す（12章）
            failed = True
            s.errors.append(f"#行動: {e}")
            log_channel.add(error_line("#行動", f"送信できませんでした。次回送り直します（{e}）"))
            break
        store.mark_sent(u.items, message_id, now, u.score)
        store.commit()
        s.sent.append(u)
        log_channel.add(log_line("sent", None, title.title, title.source_id, u.score))
        for emoji in REACTIONS:  # 8.8：ワンタップで回答できるように、送信直後に付ける
            try:
                client.add_reaction(channel_id, message_id, emoji)
            except DiscordError as e:
                s.errors.append(f"reaction {emoji}: {e}")
                log_channel.add(error_line("#行動", f"リアクション {emoji} を付けられませんでした（{e}）"))
                break
    if not failed:
        for u in p.expire:
            for c in u.items:
                store.set_item_status(c.id, "expired")
                s.expired["上限超過・締切不明"] += 1
                log_channel.add(log_line("expired", "上限超過・締切不明", c.title, c.source_id, c.score))
    store.commit()
    return s


def format_send_summary(s: SendSummary, *, dry_run: bool, now: datetime) -> str:
    lines = [f"=== send（{'dry-run・' if dry_run else ''}{s.mode}） {now.astimezone(JST):%Y-%m-%d %H:%M} JST ==="]
    if s.note:
        lines.append(s.note)
    if s.mode == "静音時間":
        return "\n".join(lines)
    lines += [
        f"候補 {len(s.candidates)} / 閾値以上 {s.eligible} / 今日の送信済み {s.sent_before} / 残り枠 {s.remaining}",
        f"送信 {len(s.sent)}" + ("（dry-run なので送ったとみなした数）" if dry_run else "")
        + f" / 店舗の追記 {len(s.updated)} / 重複で落とした {s.duplicates}",
        "expired: " + (" / ".join(f"{k} {v}" for k, v in s.expired.items()) or "なし"),
        "スコア（高い順）:",
    ]
    for c in sorted(s.candidates, key=lambda c: -c.score)[:10]:
        lines.append(f"  {c.score:.0f}{' 緊急' if c.urgent else ''}  {c.kind}/{c.genre}  {c.product or c.title}  / {c.source_id}")
    if s.errors:
        lines.append("エラー: " + " | ".join(s.errors))
    return "\n".join(lines)


def cmd_send(args, cfg: Config, env: Env, out: TextIO = sys.stdout) -> int:
    dry_run = args.dry_run
    if not dry_run:
        missing = [name for name, value in (("DISCORD_BOT_TOKEN", env.discord_bot_token),
                                            ("DISCORD_CHANNEL_ACTION", env.discord_channel_action),
                                            ("DISCORD_CHANNEL_LOG", env.discord_channel_log)) if not value]
        if missing:
            print(f".env に {', '.join(missing)} がありません（.env.example を参照）", file=sys.stderr)
            return 2
        lock = _lock(ROOT / "data" / "otoku.lock", cfg.lock_wait_seconds)
        if lock is None:
            log.error("別の otoku の実行が %d 秒たっても終わらないため、send を終了します", cfg.lock_wait_seconds)
            return 0
    now = utcnow()
    slot = in_slot(now, cfg.select_slots, cfg.send.slot_window_minutes)
    # 通常の選定は select_slots の時刻だけ。dry-run は確認用なので時刻に関係なく通常の選定を試す
    urgent_only = args.urgent_only or (slot is None and not dry_run)
    if not args.urgent_only and urgent_only:
        log.info("選定枠（%s）の時刻ではないため、緊急のものだけ送ります", ", ".join(cfg.select_slots))

    client = None if dry_run else DiscordClient(env.discord_bot_token, max_429_retries=cfg.discord.max_429_retries)
    log_channel = LogChannel(dry_run=dry_run, max_chars=cfg.discord.max_message_chars, client=client,
                             channel_id=env.discord_channel_log, outbox=ROOT / "data" / "discord_outbox.jsonl",
                             out=out)
    store = Store(ROOT / "data" / "otoku.db", dry_run=dry_run)
    try:
        summary = run_send(cfg=cfg, store=store, log_channel=log_channel, now=now, urgent_only=urgent_only,
                           client=client, channel_id=env.discord_channel_action, out=out)
    finally:
        failed = log_channel.flush()
        store.close()
    if failed:
        log.warning("#ログ に送れなかったメッセージ %d 件を次回に回します", len(failed))
    text = format_send_summary(summary, dry_run=dry_run, now=now)
    log.info("%s", text.replace("\n", " | "))
    if dry_run:
        print(text, file=out)
    return 0


# ---------------------------------------------------------------- sync・remind・check-sources（フェーズ4）

def _require(env: Env, names: list[str]) -> bool:
    missing = [n for n in names if not getattr(env, n.lower())]
    if missing:
        print(f".env に {', '.join(missing)} がありません（.env.example を参照）", file=sys.stderr)
    return not missing


def _log_channel(cfg: Config, env: Env, client: Optional[DiscordClient], dry_run: bool, out: TextIO) -> LogChannel:
    return LogChannel(dry_run=dry_run, max_chars=cfg.discord.max_message_chars, client=client,
                      channel_id=env.discord_channel_log, outbox=ROOT / "data" / "discord_outbox.jsonl", out=out)


def _finish(text: str, dry_run: bool, out: TextIO) -> int:
    log.info("%s", text.replace("\n", " | "))
    if dry_run:
        print(text, file=out)
    return 0


def cmd_sync(args, cfg: Config, env: Env, out: TextIO = sys.stdout) -> int:
    """8.9：リアクションを読んで feedback に記録する。--weekly-report なら重みを調整し、#ログ に週次報告。
    dry-run でもリアクションは読む（読むだけで、DBには書かない）。"""
    dry_run = args.dry_run
    if not _require(env, ["DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_ACTION"] + ([] if dry_run else ["DISCORD_CHANNEL_LOG"])):
        return 2
    if not dry_run and _lock(ROOT / "data" / "otoku.lock", cfg.lock_wait_seconds) is None:
        log.error("別の otoku の実行が終わらないため、sync を終了します")
        return 0
    client = DiscordClient(env.discord_bot_token, max_429_retries=cfg.discord.max_429_retries)
    log_channel = _log_channel(cfg, env, None if dry_run else client, dry_run, out)
    store = Store(ROOT / "data" / "otoku.db", dry_run=dry_run)
    now = utcnow()
    try:
        res = sync(store, client, env.discord_channel_action, now, cfg.feedback.lookback_days)
        if res.errors:
            log_channel.add(error_line("sync", f"リアクションを読めない通知が {len(res.errors)} 件: {res.errors[0]}"))
        report = ""
        if args.weekly_report:
            changes = adjust_weights(store, cfg)
            report = weekly_report(store, now, cfg.report.weekly_days, changes)
            log_channel.add(report)
    finally:
        log_channel.flush()
        store.close()
    names = {"applied": "✅", "later": "⏰", "reject": "❌"}
    changed = "、".join(f"group {g}: +{''.join(names[x] for x in a) or '-'} -{''.join(names[x] for x in r) or '-'}"
                       for g, a, r in res.changes)
    text = (f"=== sync{'（dry-run）' if dry_run else ''} {now.astimezone(JST):%Y-%m-%d %H:%M} JST ===\n"
            f"読んだ通知 {res.groups}件 / 変化 {len(res.changes)}件" + (f"（{changed}）" if changed else "")
            + (f"\nエラー: {' | '.join(res.errors)}" if res.errors else ""))
    return _finish(text, dry_run, out)


def cmd_remind(args, cfg: Config, env: Env, out: TextIO = sys.stdout) -> int:
    """8.10：⏰ のものだけ、締切の前に1回だけ #行動 へ（元メッセージへの返信）。"""
    dry_run = args.dry_run
    if not dry_run:
        if not _require(env, ["DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_ACTION", "DISCORD_CHANNEL_LOG"]):
            return 2
        if _lock(ROOT / "data" / "otoku.lock", cfg.lock_wait_seconds) is None:
            log.error("別の otoku の実行が終わらないため、remind を終了します")
            return 0
    now = utcnow()
    if is_quiet(now, cfg.quiet_hours["start"], cfg.quiet_hours["end"]):
        return _finish(f"=== remind {now.astimezone(JST):%Y-%m-%d %H:%M} JST ===\n静音時間なので送りません",
                       dry_run, out)
    client = None if dry_run else DiscordClient(env.discord_bot_token, max_429_retries=cfg.discord.max_429_retries)
    log_channel = _log_channel(cfg, env, client, dry_run, out)
    store = Store(ROOT / "data" / "otoku.db", dry_run=dry_run)
    try:
        res = remind(store, client, env.discord_channel_action, now, cfg.remind.before_hours, out)
        for e in res.errors:
            log_channel.add(error_line("remind", f"リマインドを送れませんでした。次回やり直します（{e}）"))
    finally:
        log_channel.flush()
        store.close()
    text = (f"=== remind{'（dry-run）' if dry_run else ''} {now.astimezone(JST):%Y-%m-%d %H:%M} JST ===\n"
            f"リマインド {len(res.sent)}件" + (f"\nエラー: {' | '.join(res.errors)}" if res.errors else ""))
    return _finish(text, dry_run, out)


def _log_problems(day) -> int:
    """その日（JST）のログファイルの WARNING・ERROR の行数（稼働報告のエラー数）。"""
    prefix, n = day.isoformat(), 0
    for f in (ROOT / "data" / "logs").glob("otoku.log*"):
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith(prefix) and (" WARNING " in line or " ERROR " in line):
                n += 1
    return n


def daily_report_line(store: Store, now: datetime) -> str:
    """12章：毎朝 #ログ へ「前日の取得件数／候補数／送信数／エラー数」を1行で。"""
    today_start, _ = jst_day_bounds(now)
    start = today_start - timedelta(days=1)
    c = store.period_counts(start, today_start)
    return (f"[稼働報告] {start.month}/{start.day}　新規取得 {c['new']} / 候補 {c['candidates']} / 送信 {c['sent']} / "
            f"エラー {_log_problems(start.date())}")


def cmd_check_sources(args, cfg: Config, sources: list[Source], env: Env, out: TextIO = sys.stdout) -> int:
    """情報源の疎通と robots.txt の確認。--report なら #ログ に、問題のあった情報源と稼働報告だけを送る。"""
    dry_run = args.dry_run
    if not dry_run:
        if args.report and not _require(env, ["DISCORD_BOT_TOKEN", "DISCORD_CHANNEL_LOG"]):
            return 2
        if _lock(ROOT / "data" / "otoku.lock", cfg.lock_wait_seconds) is None:
            log.error("別の otoku の実行が終わらないため、check-sources を終了します")
            return 0
    post = args.report and not dry_run  # #ログ に送るのは本番の --report のときだけ（dry-run は標準出力）
    client = DiscordClient(env.discord_bot_token, max_429_retries=cfg.discord.max_429_retries) if post else None
    log_channel = _log_channel(cfg, env, client, not post, out)
    store = Store(ROOT / "data" / "otoku.db", dry_run=dry_run)
    fetcher = Fetcher(contact=env.contact, timeout=cfg.collect.timeout_seconds,
                      host_spacing=cfg.collect.host_spacing_seconds, retry=cfg.collect.retry)
    now = utcnow()
    try:
        results = check_sources(sources, store, fetcher, now)
        lines = [f"[check] {r.source_id}: {r.detail}" for r in results]
        problems = [line for r, line in zip(results, lines) if not r.ok]
        if args.report:
            log_channel.add(daily_report_line(store, now))
            for line in problems:
                log_channel.add(line)
    finally:
        log_channel.flush()
        fetcher.close()
        store.close()
    for line in problems:
        log.warning("%s", line)
    text = (f"=== check-sources{'（dry-run）' if dry_run else ''} {now.astimezone(JST):%Y-%m-%d %H:%M} JST ===\n"
            f"確認 {len(results)} / 問題 {len(problems)}\n" + "\n".join(lines))
    if not args.report and not dry_run:
        print(text, file=out)
    return _finish(text, dry_run, out)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(prog="otoku", description="お得情報収集システム")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("collect", help="収集〜候補登録まで")
    p.add_argument("--dry-run", action="store_true", help="Discord送信とDB書き込みをせず、標準出力に出す")
    p = sub.add_parser("send", help="送信選定と #行動 への通知")
    p.add_argument("--dry-run", action="store_true", help="Discord送信とDB書き込みをせず、標準出力に出す")
    p.add_argument("--urgent-only", action="store_true", help="緊急（先着・締切が近い）のものだけ送る")
    p = sub.add_parser("sync", help="リアクションの取得とスコア調整")
    p.add_argument("--dry-run", action="store_true", help="Discord送信とDB書き込みをせず、標準出力に出す")
    p.add_argument("--weekly-report", action="store_true", help="情報源の重みを調整し、#ログ に週次報告を送る")
    p = sub.add_parser("remind", help="締切リマインド")
    p.add_argument("--dry-run", action="store_true", help="Discord送信とDB書き込みをせず、標準出力に出す")
    p = sub.add_parser("check-sources", help="情報源の疎通・robots確認")
    p.add_argument("--dry-run", action="store_true", help="Discord送信とDB書き込みをせず、標準出力に出す")
    p.add_argument("--report", action="store_true", help="#ログ に稼働報告と問題のあった情報源を送る")
    args = parser.parse_args(argv)

    cfg = load_config(ROOT / "config" / "config.yaml")
    sources = load_sources(ROOT / "config" / "sources.yaml")
    env = load_env(ROOT / ".env")
    _setup_logging(args.dry_run)
    if args.command == "collect":
        return cmd_collect(args, cfg, sources, env)
    if args.command == "send":
        return cmd_send(args, cfg, env)
    if args.command == "sync":
        return cmd_sync(args, cfg, env)
    if args.command == "remind":
        return cmd_remind(args, cfg, env)
    if args.command == "check-sources":
        return cmd_check_sources(args, cfg, sources, env)
    return 2


if __name__ == "__main__":
    sys.exit(main())
