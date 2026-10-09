"""8.9 フィードバックと調整：リアクションの取得、情報源の重みの調整、週次報告。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ..db import Store
from ..models import JST, Config
from ..notify.discord import REACTION_NAMES, REACTIONS, DiscordClient, DiscordError


@dataclass
class SyncResult:
    groups: int = 0
    changes: list[tuple[int, set, set]] = field(default_factory=list)  # (group_id, 付いた, 外された)
    errors: list[str] = field(default_factory=list)


def sync(store: Store, client: DiscordClient, channel_id: str, now: datetime, lookback_days: int) -> SyncResult:
    """直近 lookback_days 日に送ったメッセージのリアクションを読み、feedback に記録する（Bot自身の分は除く）。"""
    res = SyncResult()
    bot_id = client.me()
    for group_id, message_id in store.sent_groups(now - timedelta(days=lookback_days)):
        present = set()
        try:
            for emoji in REACTIONS:
                users = client.reaction_users(channel_id, message_id, emoji)
                if any(u != bot_id for u in users):
                    present.add(REACTION_NAMES[emoji])
        except DiscordError as e:
            if e.status == 404:  # メッセージが消された
                continue
            res.errors.append(f"group {group_id}: {e}")
            continue
        res.groups += 1
        added, removed = store.set_feedback(group_id, present, now)
        if added or removed:
            res.changes.append((group_id, added, removed))
    store.refresh_feedback_counts()
    store.commit()
    return res


@dataclass
class WeightChange:
    source_id: str
    before: float
    after: float
    n: int
    applied: float
    reject: float


def adjust_weights(store: Store, cfg: Config) -> list[WeightChange]:
    """情報源ごとに直近 window 件の通知を集計し、❌ の割合が ratio を超えたら -step、✅ なら +step（範囲は min〜max）。
    週1回だけ行う。通知が min_notifications 件未満の情報源は調整しない（2026-10-09 ユーザー判断）。"""
    f, sw = cfg.feedback, cfg.weights.source_weight
    out = []
    for source_id in store.sources_with_sent():
        recent = store.recent_feedback(source_id, f.window)
        n = len(recent)
        applied = sum("applied" in r for r in recent) / n if n else 0.0
        reject = sum("reject" in r for r in recent) / n if n else 0.0
        before = store.source_weight(source_id)
        after = before
        if n >= f.min_notifications:
            if reject > f.ratio:
                after = before - sw.step
            elif applied > f.ratio:
                after = before + sw.step
            after = min(max(after, sw.min), sw.max)
        if after != before:
            store.set_weight(source_id, after)
        out.append(WeightChange(source_id, before, after, n, applied, reject))
    store.commit()
    return out


def _pct(n: int, d: int) -> str:
    return f"{n / d * 100:.0f}%" if d else "-"


def weekly_report(store: Store, now: datetime, days: int, changes: list[WeightChange]) -> str:
    """#ログ へ1メッセージ：通知数、✅率、❌率、情報源別の成績（8.9）、AI判定の件数（13章）。"""
    start = now - timedelta(days=days)
    sent = store.sent_groups_between(start, now)
    counts = store.period_counts(start, now)
    total = len(sent)
    applied = sum("applied" in r for _, r, _ in sent)
    reject = sum("reject" in r for _, r, _ in sent)
    later = sum("later" in r for _, r, _ in sent)
    s_local, e_local = start.astimezone(JST), now.astimezone(JST)
    lines = [f"[週次報告] {s_local.month}/{s_local.day}〜{e_local.month}/{e_local.day}　"
             f"通知 {total}件（✅ {applied}件 {_pct(applied, total)} / ❌ {reject}件 {_pct(reject, total)} / ⏰ {later}件）"
             f"　AI判定 {counts['ai']}件　新規取得 {counts['new']}件"]
    by_source: dict[str, list[set]] = {}
    for _, reactions, sources in sent:
        for sid in sources:
            by_source.setdefault(sid, []).append(reactions)
    weights = {c.source_id: c for c in changes}
    parts = []
    for sid in sorted(set(by_source) | set(weights)):
        rs = by_source.get(sid, [])
        a, r = sum("applied" in x for x in rs), sum("reject" in x for x in rs)
        w = weights.get(sid)
        weight = ""
        if w:
            weight = f" 重み{w.after:+.0f}" + (f"（{w.after - w.before:+.0f}）" if w.after != w.before else "")
        parts.append(f"{sid} {len(rs)}件 ✅{_pct(a, len(rs))} ❌{_pct(r, len(rs))}{weight}")
    if parts:
        lines.append("情報源別: " + " / ".join(parts))
    return "\n".join(lines)
