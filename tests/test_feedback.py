"""フェーズ4：リアクションの取得、重みの調整、締切リマインド、週次報告、check-sources、稼働報告。"""
import json
from datetime import timedelta
from urllib.parse import unquote

import httpx
import pytest

from otoku.collectors import Fetcher
from otoku.collectors.check import check_sources
from otoku.feedback.reactions import adjust_weights, sync, weekly_report
from otoku.feedback.reminder import remind
from otoku.notify.discord import DiscordClient

from .conftest import NOW, Router, make_source
from .test_send import FakeDiscord, add_candidate, at, run

ACTION = "111"


class FakeReactions(FakeDiscord):
    """送信（FakeDiscord）に加えて、Bot自身の情報とリアクションの一覧を返す。"""

    def __init__(self):
        super().__init__()
        self.users: dict[tuple[str, str], list[str]] = {}  # (message_id, emoji) -> ユーザーID
        self.deleted: set[str] = set()

    def react(self, message_id, emoji, *users):
        self.users[(message_id, emoji)] = ["BOT", *users]  # 送信直後に Bot 自身も付けている

    def __call__(self, request):
        url = str(request.url)
        if request.method == "GET" and url.endswith("/users/@me"):
            return httpx.Response(200, json={"id": "BOT"})
        if request.method == "GET" and "/reactions/" in url:
            message_id = url.split("/messages/")[1].split("/")[0]
            if message_id in self.deleted:
                return httpx.Response(404, json={"message": "Unknown Message"})
            emoji = unquote(url.split("/reactions/")[1].split("?")[0])
            return httpx.Response(200, json=[{"id": u} for u in self.users.get((message_id, emoji), ["BOT"])])
        if request.method == "POST":
            body = json.loads(request.content)
            self.posts.append(body)
            return httpx.Response(200, json={"id": str(1000 + len(self.posts))})
        return super().__call__(request)


def client(fake):
    return DiscordClient("TOKEN", max_429_retries=1, client=httpx.Client(transport=httpx.MockTransport(fake)),
                         sleep=lambda s: None)


@pytest.fixture(autouse=True)
def _pin(cfg):
    cfg.daily_cap = 50  # 1日に何件も送ってリアクションを試すため
    cfg.score_threshold = 60


def send_some(cfg, store, fake, n, *, deadline=None, source="src", start=0):
    for i in range(start, start + n):
        add_candidate(store, i, first_come=True, deadline=deadline, source=source)  # 65点
    run(cfg, store, at(12), fake)
    return [str(1001 + i) for i in range(start, start + n)]


def feedback_rows(store):
    return sorted(tuple(r) for r in store.conn.execute("SELECT group_id, reaction FROM feedback"))


def test_sync_records_user_reactions_but_not_the_bots_own(cfg, store):
    fake = FakeReactions()
    m1, m2, m3 = send_some(cfg, store, fake, 3)
    fake.react(m1, "✅", "USER")
    fake.react(m2, "⏰", "USER")
    fake.react(m2, "❌", "USER")
    res = sync(store, client(fake), ACTION, at(13), 14)
    assert res.groups == 3 and not res.errors
    assert feedback_rows(store) == [(1, "applied"), (2, "later"), (2, "reject")]  # 3つ目は Bot の分だけ → なし
    fake.users[(m2, "❌")] = ["BOT"]  # あとで外された
    sync(store, client(fake), ACTION, at(14), 14)
    assert feedback_rows(store) == [(1, "applied"), (2, "later")]
    stats = store.conn.execute("SELECT applied_count, reject_count FROM source_stats WHERE source_id='src'").fetchone()
    assert tuple(stats) == (1, 0)


def test_sync_skips_deleted_messages(cfg, store):
    fake = FakeReactions()
    m1, = send_some(cfg, store, fake, 1)
    fake.deleted.add(m1)
    res = sync(store, client(fake), ACTION, at(13), 14)
    assert res.groups == 0 and not res.errors


def test_weights_move_by_step_with_enough_notifications_and_stop_at_limits(cfg, store):
    fake = FakeReactions()
    bad = send_some(cfg, store, fake, 5, source="bad")
    good = send_some(cfg, store, fake, 5, source="good", start=5)
    few = send_some(cfg, store, fake, 2, source="few", start=10)
    for m in bad[:3]:
        fake.react(m, "❌", "USER")              # 3/5 = 60% > 50%
    for m in good[:3]:
        fake.react(m, "✅", "USER")
    for m in few:
        fake.react(m, "❌", "USER")              # 100% だが 2件しかない
    sync(store, client(fake), ACTION, at(13), 14)
    changes = {c.source_id: (c.before, c.after) for c in adjust_weights(store, cfg)}
    assert changes == {"bad": (0, -5), "good": (0, 5), "few": (0, 0)}
    for _ in range(3):                           # 毎週続いても -10〜+10 で止まる
        adjust_weights(store, cfg)
    assert store.source_weight("bad") == -10 and store.source_weight("good") == 10


def test_weights_look_at_the_latest_window_only(cfg, store):
    cfg.feedback.window = 5
    fake = FakeReactions()
    old = send_some(cfg, store, fake, 5, source="s")
    for m in old:
        fake.react(m, "❌", "USER")
    store.conn.execute("UPDATE groups SET first_sent_at = '2026-10-01T00:00:00+00:00'")  # 古い5件
    store.commit()
    send_some(cfg, store, fake, 5, source="s", start=5)  # 新しい5件はリアクションなし
    sync(store, client(fake), ACTION, at(13), 30)
    assert {c.source_id: c.after for c in adjust_weights(store, cfg)} == {"s": 0}


def test_weekly_report_is_one_message_with_rates(cfg, store):
    fake = FakeReactions()
    ms = send_some(cfg, store, fake, 4, source="lawson_sale")
    fake.react(ms[0], "✅", "USER")
    fake.react(ms[1], "✅", "USER")
    fake.react(ms[2], "❌", "USER")
    fake.react(ms[3], "⏰", "USER")
    sync(store, client(fake), ACTION, at(13), 14)
    text = weekly_report(store, at(13), 7, adjust_weights(store, cfg))
    first, second = text.splitlines()
    assert "通知 4件（✅ 2件 50% / ❌ 1件 25% / ⏰ 1件）" in first and "AI判定 4件" in first
    assert second == "情報源別: lawson_sale 4件 ✅50% ❌25% 重み+0"


def test_only_snoozed_items_are_reminded_once(cfg, store):
    """フェーズ4の完了条件：⏰のものだけリマインドが1回届く。"""
    fake = FakeReactions()
    deadline = at(22)  # 送信は 12:00、締切は同じ日の 22:00
    ms = send_some(cfg, store, fake, 5, deadline=deadline)
    no_deadline = send_some(cfg, store, fake, 1, start=5)[0]
    fake.react(ms[0], "⏰", "USER")                       # → リマインドする
    fake.react(ms[1], "⏰", "USER")
    fake.react(ms[1], "✅", "USER")                       # ⏰ のあと応募済み → しない
    fake.react(ms[2], "❌", "USER")                       # → しない
    fake.react(no_deadline, "⏰", "USER")                 # 締切不明 → しない
    sync(store, client(fake), ACTION, at(12, 30), 14)
    posts_before = len(fake.posts)
    sent_before = store.count_sent(at(0), at(0) + timedelta(days=1))
    res = remind(store, client(fake), ACTION, at(13), cfg.remind.before_hours)
    assert res.sent == [1]
    reply = fake.posts[-1]
    assert len(fake.posts) == posts_before + 1
    assert reply["message_reference"]["message_id"] == ms[0]               # 元メッセージへの返信
    assert reply["content"].splitlines()[:2] == ["【締切まで24時間以内】商品0", "締切：10/9 22:00"]
    assert remind(store, client(fake), ACTION, at(14), cfg.remind.before_hours).sent == []  # 2回目はない
    assert store.count_sent(at(0), at(0) + timedelta(days=1)) == sent_before            # 上限に数えない


def test_reminder_waits_until_within_the_window(cfg, store):
    fake = FakeReactions()
    m, = send_some(cfg, store, fake, 1, deadline=at(12, day=11))
    fake.react(m, "⏰", "USER")
    sync(store, client(fake), ACTION, at(13), 14)
    assert remind(store, client(fake), ACTION, at(9, day=10), 24).sent == []   # 締切まで27時間
    assert remind(store, client(fake), ACTION, at(13, day=10), 24).sent == [1]  # 23時間


# ---------------------------------------------------------------- check-sources・稼働報告

def fetcher_for(routes):
    router = Router(routes)
    return Fetcher(contact="", timeout=5, host_spacing=0, retry=0,
                   client=httpx.Client(transport=httpx.MockTransport(router)), sleep=lambda s: None), router


RSS = b'<rss version="2.0"><channel><title>t</title><item><title>a</title><link>https://a.example.com/1</link></item></channel></rss>'


def test_check_sources(store):
    sources = [
        make_source("ok", url="https://a.example.com/feed"),
        make_source("blocked", url="https://b.example.com/api/feed"),
        make_source("forbidden", url="https://c.example.com/feed"),
        make_source("server_down", url="https://d.example.com/feed"),
        make_source("empty_list", type="html_diff", url="https://a.example.com/list", link_selector="div.none"),
    ]
    fetcher, router = fetcher_for({
        "https://a.example.com/robots.txt": httpx.Response(404),
        "https://a.example.com/feed": httpx.Response(200, content=RSS),
        "https://a.example.com/list": httpx.Response(200, content=b"<html><a href='/x'>x</a></html>"),
        "https://b.example.com/robots.txt": httpx.Response(200, text="User-agent: *\nDisallow: /api/\n"),
        "https://c.example.com/robots.txt": httpx.Response(200, text="User-agent: *\nAllow: /\n"),
        "https://c.example.com/feed": httpx.Response(403),
        "https://d.example.com/robots.txt": httpx.Response(503),
    })
    results = {r.source_id: r for r in check_sources(sources, store, fetcher, NOW)}
    assert results["ok"].ok and results["ok"].detail == "OK（rss 1件）"
    assert not results["blocked"].ok and "Disallow: /api/" in results["blocked"].detail
    assert store.source_state("blocked").paused_until == NOW + timedelta(hours=25)  # 止めて、翌朝また確認
    assert not results["forbidden"].ok and "HTTP 403" in results["forbidden"].detail
    assert not results["server_down"].ok and store.source_state("server_down").paused_until is not None
    assert not results["empty_list"].ok and "0件" in results["empty_list"].detail
    robots_requests = [r for r in router.requests if r.url.path == "/robots.txt" and r.url.host == "a.example.com"]
    assert len(robots_requests) == 1  # 同じホストの robots.txt は1回だけ


def test_daily_report_line(cfg, store, tmp_path, monkeypatch):
    import otoku.cli as cli
    fake = FakeReactions()
    send_some(cfg, store, fake, 2)  # 10/9 12:00 に2件送信
    (tmp_path / "data" / "logs").mkdir(parents=True)
    (tmp_path / "data" / "logs" / "otoku.log").write_text(
        "2026-10-09 16:00:17,150 WARNING 取得失敗 geo_news_lottery（1回目）: HTTP 403\n"
        "2026-10-09 16:02:52,559 INFO === collect ===\n"
        "2026-10-10 08:00:00,000 ERROR 別の日\n", encoding="utf-8")
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    line = cli.daily_report_line(store, at(8, day=10))
    assert line == "[稼働報告] 10/9　新規取得 2 / 候補 2 / 送信 2 / エラー 1"
