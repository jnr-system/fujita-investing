"""collect の流れ全体（収集 → 重複排除 → ルール → AI → 検証 → #ログ）。通信とAIはすべて偽物。"""
from datetime import timedelta
from xml.sax.saxutils import escape

import httpx

from otoku.cli import run_collect
from otoku.db import Store
from otoku.pipeline.extract import AIUnavailable, Extractor

from .conftest import NOW, FakeAI, Router, make_fetcher, make_source

FEED_URL = "https://feeds.example.com/feed.xml"

# (タイトル, AIの応答)。応答が None のものはルールで落ちてAIに渡らない想定
ENTRIES = [
    ("【先着1万名】新商品 全額キャッシュバック", "refund_first_ok"),
    ("抽選で100名様に全額返金キャンペーン", "excluded_lottery_refund"),
    ("満足できなければ全額返金！お試しキャンペーン", "excluded_refund_guarantee"),
    ("初回無料サンプル 毎月お届け", "subscription"),
    ("先着プレゼントキャンペーン（10/1まで）", "closed"),
    ("限定ウイスキー 抽選販売のお知らせ", "preview_future"),
    ("新型ゲーム機 限定モデル 抽選販売を予定", "preview_no_date"),
    ("無料引換券がもらえる（あいまい）", "low_confidence"),
    ("応答が壊れる 先着プレゼント", "invalid_not_json.txt"),
    ("新店舗オープンのお知らせ", None),
    ("プレゼントキャンペーン 当選発表", None),
]


def feed(entries, n0=0) -> bytes:
    items = "".join(
        f"<item><title>{escape(t)}</title><link>https://example.com/news/{n0 + i}?utm_source=rss</link>"
        f"<description>本文 {i}</description><pubDate>Fri, 09 Oct 2026 01:00:00 +0000</pubDate></item>"
        for i, (t, _) in enumerate(entries))
    return f'<?xml version="1.0"?><rss version="2.0"><channel><title>t</title>{items}</channel></rss>'.encode()


def fake_ai():
    return FakeAI({t: a for t, a in ENTRIES if a})


def extractor(cfg, ai):
    return Extractor(cfg.gemini, "system", call=ai)


def lines(log_out):
    return [l.removeprefix("#ログ ") for l in log_out.getvalue().splitlines()]


def test_pipeline_end_to_end(cfg, store, dry_log, log_out):
    router = Router({FEED_URL: httpx.Response(200, content=feed(ENTRIES), headers={"ETag": '"v1"'})})
    ai = fake_ai()
    s = run_collect(cfg=cfg, sources=[make_source()], store=store, fetcher=make_fetcher(router),
                    extractor=extractor(cfg, ai), log_channel=dry_log, now=NOW)
    dry_log.flush()

    assert s.sources["test_rss"].fetched == 11
    assert s.sources["test_rss"].rule_pass == 9          # ルールで2件落ちる
    assert len(ai.prompts) == 9 + 1                       # 壊れた応答は1回だけ再試行
    assert s.statuses == {"candidate": 1, "waiting": 1, "dropped": 7}
    assert s.kinds["AI応答不正"] == 1
    assert s.rule_drops == {"対象キーワードなし": 1, "除外キーワード「当選発表」": 1}

    out = lines(log_out)
    assert "[candidate] 【先着1万名】新商品 全額キャッシュバック / test_rss / -" in out
    assert "[dropped: AI除外: 抽選で全額返金（懸賞）] 抽選で100名様に全額返金キャンペーン / test_rss / -" in out
    assert any(l.startswith("[dropped: AI除外: 満足できなければ返金の返金保証]") for l in out)
    assert any(l.startswith("[dropped: 継続購入・定期契約・有料会員が条件]") for l in out)
    assert any(l.startswith("[dropped: 締切が過去]") for l in out)
    assert any(l.startswith("[waiting: 開始待ち 10/15 10:00] 限定ウイスキー") for l in out)
    assert any(l.startswith("[dropped: 今は応募・受取できない] 新型ゲーム機") for l in out)
    assert any(l.startswith("[dropped: 確信度不足 0.60]") for l in out)
    assert any(l.startswith("[dropped: AI応答不正] 応答が壊れる") for l in out)
    assert len(out) == 9  # ルールで落としたものは #ログ に出さない

    db = store.conn
    assert db.execute("SELECT COUNT(*) FROM raw_items").fetchone()[0] == 11
    rows = dict(db.execute("SELECT status, COUNT(*) FROM items GROUP BY status").fetchall())
    assert rows == {"candidate": 1, "waiting": 1, "dropped": 7}
    reasons = [r[0] for r in db.execute("SELECT exclude_reason FROM items WHERE status = 'dropped'")]
    assert "AI応答不正" in reasons and all(reasons)       # 落とした理由はDBにも残す
    cand = db.execute("SELECT scope, kind, genre, deadline_at FROM items WHERE status = 'candidate'").fetchone()
    assert tuple(cand) == ("B", "refund_first", "food", "2026-10-20T14:59:00+00:00")  # 保存はUTC
    st = store.source_state("test_rss")
    assert st.etag == '"v1"' and st.last_fetched_at == NOW and st.fail_streak == 0


def test_second_run_uses_conditional_get_and_dedupes(cfg, store, dry_log):
    router = Router({FEED_URL: [httpx.Response(200, content=feed(ENTRIES[:2]), headers={"ETag": '"v1"'}),
                                httpx.Response(304),
                                httpx.Response(200, content=feed(ENTRIES[:2]), headers={"ETag": '"v2"'})]})
    fetcher = make_fetcher(router, retry=0)
    ai = fake_ai()
    src = make_source()
    later = NOW
    for _ in range(3):
        run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=extractor(cfg, ai),
                    log_channel=dry_log, now=later)
        later += timedelta(minutes=30)
    assert router.requests[1].headers["If-None-Match"] == '"v1"'
    assert len(ai.prompts) == 2  # 2回目は304、3回目は同じURLだけなのでAIは呼ばない
    assert store.conn.execute("SELECT COUNT(*) FROM raw_items").fetchone()[0] == 2


def test_min_interval_is_respected(cfg, store, dry_log):
    router = Router({FEED_URL: httpx.Response(200, content=feed([]))})
    fetcher = make_fetcher(router)
    src = make_source(min_interval_minutes=30)
    run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=None, log_channel=dry_log, now=NOW)
    s = run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=None, log_channel=dry_log,
                    now=NOW + timedelta(minutes=10))
    assert s.skipped == {"間隔待ち": 1} and len(router.requests) == 1
    # cron の起動のずれ（30分より数秒早い）は、設定の余裕の範囲で取得する
    s = run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=None, log_channel=dry_log,
                    now=NOW + timedelta(minutes=30) - timedelta(seconds=5))
    assert not s.skipped and len(router.requests) == 2


def test_three_failures_pause_once_and_report_once(cfg, store, dry_log, log_out):
    router = Router({FEED_URL: httpx.Response(500)})
    fetcher = make_fetcher(router)
    src = make_source()
    t = NOW
    for _ in range(5):  # 3回失敗で停止、その後2回は停止中
        run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=None, log_channel=dry_log, now=t)
        t += timedelta(minutes=30)
    dry_log.flush()
    paused = [l for l in lines(log_out) if l.startswith("[paused]")]
    assert paused == ["[paused] test_rss: 3回続けて取得に失敗したため24時間停止します"]
    assert len(router.requests) == 3 * 2  # 1回の取得につき再試行1回
    st = store.source_state("test_rss")
    assert st.paused_until == NOW + timedelta(hours=1) + timedelta(hours=24)
    # 停止が明けたらまた取りに行く
    run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=None, log_channel=dry_log,
                now=st.paused_until + timedelta(minutes=1))
    assert len(router.requests) == 4 * 2


def test_ai_unavailable_leaves_rest_for_next_run(cfg, store, dry_log, log_out):
    router = Router({FEED_URL: httpx.Response(200, content=feed(ENTRIES[:3]), headers={"ETag": '"v1"'})})
    fetcher = make_fetcher(router)
    calls = {"n": 0}
    good = fake_ai()

    def flaky(system, user):
        calls["n"] += 1
        if calls["n"] == 2:
            raise AIUnavailable("429 RESOURCE_EXHAUSTED")
        return good(system, user)

    src = make_source()
    s = run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=extractor(cfg, flaky),
                    log_channel=dry_log, now=NOW)
    dry_log.flush()
    assert s.sources["test_rss"].ai == 1
    assert any(l.startswith("[error] gemini:") for l in lines(log_out))
    assert store.source_state("test_rss").etag is None  # 取得の記録を更新しない → 次回は全体を取り直す
    assert store.conn.execute("SELECT COUNT(*) FROM raw_items").fetchone()[0] == 1

    s = run_collect(cfg=cfg, sources=[src], store=store, fetcher=fetcher, extractor=extractor(cfg, good),
                    log_channel=dry_log, now=NOW + timedelta(minutes=30))
    assert s.sources["test_rss"].ai == 2  # 残りの2件を処理
    assert store.source_state("test_rss").etag == '"v1"'


def test_dry_run_writes_nothing(cfg, tmp_path, dry_log, log_out):
    db_path = tmp_path / "data" / "otoku.db"
    store = Store(db_path, dry_run=True)
    router = Router({FEED_URL: httpx.Response(200, content=feed(ENTRIES[:2]))})
    s = run_collect(cfg=cfg, sources=[make_source()], store=store, fetcher=make_fetcher(router),
                    extractor=extractor(cfg, fake_ai()), log_channel=dry_log, now=NOW)
    dry_log.flush()
    store.close()
    assert not db_path.exists() and not (tmp_path / "data").exists()
    assert s.statuses == {"candidate": 1, "dropped": 1}
    assert len(lines(log_out)) == 2


def test_dry_run_against_existing_db_is_read_only(cfg, tmp_path, dry_log):
    db_path = tmp_path / "otoku.db"
    Store(db_path).close()
    before = db_path.read_bytes()
    store = Store(db_path, dry_run=True)
    router = Router({FEED_URL: httpx.Response(200, content=feed(ENTRIES[:2]))})
    run_collect(cfg=cfg, sources=[make_source()], store=store, fetcher=make_fetcher(router),
                extractor=extractor(cfg, fake_ai()), log_channel=dry_log, now=NOW)
    store.close()
    assert db_path.read_bytes() == before


def test_disabled_sources_are_skipped(cfg, store, dry_log):
    router = Router({})
    s = run_collect(cfg=cfg, sources=[make_source("off", enabled=False)], store=store, fetcher=make_fetcher(router),
                    extractor=None, log_channel=dry_log, now=NOW)
    assert router.requests == [] and not s.sources and not s.skipped
