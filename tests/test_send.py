"""8.7 送信選定と 8.8 #行動 への通知。Discord は偽物。"""
import io
import json
from datetime import datetime, timedelta
from urllib.parse import unquote

import httpx

from otoku.cli import run_send
from otoku.models import JST, RawItem
from otoku.notify.discord import SUPPRESS_EMBEDS, DiscordClient, LogChannel
from otoku.notify.format import action_message
from otoku.pipeline.dedupe import url_hash
from otoku.pipeline.select import in_slot, is_quiet

from .conftest import NOW
from .test_score import cand

ACTION = "111"
MSG_URL = f"https://discord.com/api/v10/channels/{ACTION}/messages"


class FakeDiscord:
    """POST はメッセージIDを返し、リアクションの PUT は 204。fail_post=True なら送信を失敗させる。"""

    def __init__(self, fail_post=False):
        self.posts, self.reactions, self.edits = [], [], []
        self.fail_post = fail_post

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            if self.fail_post:
                return httpx.Response(500, text="boom")
            body = json.loads(request.content)
            self.posts.append(body)
            return httpx.Response(200, json={"id": str(1000 + len(self.posts))})
        if request.method == "PATCH":
            self.edits.append((str(request.url).rsplit("/", 1)[1], json.loads(request.content)))
            return httpx.Response(200, json={"id": str(request.url).rsplit("/", 1)[1]})
        if request.method == "PUT":
            self.reactions.append(unquote(str(request.url).split("/reactions/")[1].split("/")[0]))
            return httpx.Response(204)
        return httpx.Response(404)


def client(fake):
    return DiscordClient("TOKEN", max_429_retries=1, client=httpx.Client(transport=httpx.MockTransport(fake)),
                         sleep=lambda s: None)


def add_candidate(store, n, *, kind="free_item", genre="cvs", deadline=None, first_come=False, benefit=None,
                  status="candidate", title=None, product=None, organizer="店", source="src", cost=None, group=False):
    raw = RawItem(source_id=source, url=f"https://example.com/{n}", title=title or f"候補{n}", body="")
    rid = store.add_raw(raw, url_hash(raw.url), "h", NOW)
    scope = "A" if kind == "lottery" else "B"
    item_id = store.add_item(rid, scope=scope, kind=kind, status=status, created_at=NOW, genre=genre,
                             product=product or f"商品{n}", organizer=organizer, deadline_at=deadline,
                             conditions="条件", benefit_yen=benefit, cost_yen=cost, first_come=first_come,
                             apply_url=None)
    if group:  # collect と同じく、商品名でグループに入れる
        from otoku.pipeline.group import group_key
        store.assign_group(item_id, scope, group_key(scope, product or f"商品{n}"), product or f"商品{n}", NOW, source)
    store.commit()
    return item_id


def run(cfg, store, now, fake=None, urgent_only=False):
    log = LogChannel(dry_run=True, max_chars=2000, out=io.StringIO())
    s = run_send(cfg=cfg, store=store, log_channel=log, now=now, urgent_only=urgent_only,
                 client=client(fake) if fake else None, channel_id=ACTION, out=io.StringIO())
    log.flush()
    return s, log.out.getvalue()


def at(h, m=0, day=9):
    return datetime(2026, 10, day, h, m, tzinfo=JST)


def statuses(store):
    return dict(store.conn.execute("SELECT status, COUNT(*) FROM items GROUP BY status").fetchall())


def test_cap_is_not_exceeded_and_resets_next_day(cfg, store):
    for n in range(5):  # 閾値以上（free_item 50 + 締切まで2日 5 + 5,000円相当 10 = 65）
        add_candidate(store, n, deadline=at(12, day=11), benefit=5000)
    fake = FakeDiscord()
    s, _ = run(cfg, store, at(12), fake)
    assert len(fake.posts) == cfg.daily_cap == 3
    s, _ = run(cfg, store, at(19), fake)                 # 同じ日の2回目の枠：残り0
    assert len(fake.posts) == 3 and s.remaining == 0
    assert statuses(store) == {"sent": 3, "candidate": 2}  # 締切があるので翌日に再評価
    s, _ = run(cfg, store, at(12, day=10), fake)          # 日付が変わると上限がリセット
    assert len(fake.posts) == 5 and s.sent_before == 0


def test_nothing_is_sent_when_no_candidates(cfg, store):
    fake = FakeDiscord()
    s, log = run(cfg, store, at(12), fake)
    add_candidate(store, 1, kind="free_game", genre="game")  # 45点で閾値未満
    s2, _ = run(cfg, store, at(19), fake)
    assert fake.posts == [] and fake.reactions == []
    assert s.sent == [] and s2.sent == [] and s2.eligible == 0
    assert log == ""  # 「該当なし」も送らない


def test_quiet_hours_send_nothing(cfg, store):
    add_candidate(store, 1, first_come=True)  # 緊急
    fake = FakeDiscord()
    for now in (at(23), at(23, 30), at(2), at(6, 59)):
        s, _ = run(cfg, store, now, fake, urgent_only=True)
        assert s.mode == "静音時間"
    assert fake.posts == []
    s, _ = run(cfg, store, at(7), fake, urgent_only=True)   # 7:00 にまとめて送る
    assert len(fake.posts) == 1


def test_urgent_found_at_night_with_deadline_before_7_is_discarded(cfg, store):
    add_candidate(store, 1, first_come=True, deadline=at(6, 30, day=10), title="締切6:30")
    add_candidate(store, 2, first_come=True, deadline=at(9, day=10), title="締切9:00")
    fake = FakeDiscord()
    run(cfg, store, at(23, 30), fake, urgent_only=True)
    s, log = run(cfg, store, at(7, day=10), fake, urgent_only=True)
    assert [p["content"].splitlines()[0] for p in fake.posts] == ["【先着・無料】商品2"]
    assert "[expired: 締切が過去] 締切6:30" in log


def test_urgent_only_sends_only_urgent(cfg, store):
    add_candidate(store, 1, deadline=at(12, day=11), benefit=5000)       # 65点だが緊急ではない
    add_candidate(store, 2, deadline=at(20), title="締切が今夜")             # 50 + 15 = 65、緊急
    fake = FakeDiscord()
    s, _ = run(cfg, store, at(10), fake, urgent_only=True)
    assert [u.items[0].title for u in s.sent] == ["締切が今夜"]
    s, _ = run(cfg, store, at(12), fake)                                  # 通常の枠で残りを送る
    assert [u.items[0].title for u in s.sent] == ["候補1"]


def test_over_cap_without_deadline_expires(cfg, store):
    for n in range(4):
        add_candidate(store, n, first_come=True)       # 65点、締切不明
    add_candidate(store, 9, deadline=at(12, day=12), benefit=1000, title="締切あり")  # 50+5+5 = 60（送られない側）
    fake = FakeDiscord()
    s, log = run(cfg, store, at(12), fake)
    assert len(fake.posts) == 3
    assert statuses(store) == {"sent": 3, "expired": 1, "candidate": 1}
    assert s.expired == {"上限超過・締切不明": 1}
    assert "[expired: 上限超過・締切不明]" in log


def test_message_format_reactions_and_records(cfg, store):
    add_candidate(store, 1, kind="lottery", genre="tcg", deadline=at(16, 59, day=12))
    store.conn.execute("UPDATE items SET cost_yen = 7200, organizer = 'ヨドバシ', product = '◯◯ BOX'")
    store.commit()
    fake = FakeDiscord()
    s, log = run(cfg, store, at(12), fake)
    post = fake.posts[0]
    assert post["content"] == "【抽選】◯◯ BOX（定価7,200円）\n締切：10/12 16:59　店舗：ヨドバシ\nhttps://example.com/1"
    assert post["flags"] == SUPPRESS_EMBEDS and post["allowed_mentions"] == {"parse": []}
    assert fake.reactions == ["✅", "⏰", "❌"]
    assert "[sent] 候補1 / src / 65" in log  # 50 + tcg 15（締切まで約77時間なので緊急度は0）
    row = store.conn.execute("SELECT i.status, i.score, g.discord_message_id, n.kind, n.channel FROM items i "
                             "JOIN groups g ON g.id = i.group_id JOIN notifications n ON n.group_id = g.id").fetchone()
    assert tuple(row) == ("sent", 65.0, "1001", "new", "action")
    assert store.conn.execute("SELECT sent_count FROM source_stats WHERE source_id = 'src'").fetchone()[0] == 1


def test_discord_failure_keeps_candidate_for_next_run(cfg, store):
    add_candidate(store, 1, first_come=True)
    add_candidate(store, 2, first_come=True)
    s, log = run(cfg, store, at(12), FakeDiscord(fail_post=True))
    assert s.sent == [] and "[error] #行動" in log
    assert statuses(store) == {"candidate": 2}  # 失敗したときは上限超過の expired もしない
    fake = FakeDiscord()
    run(cfg, store, at(12, 30), fake)
    assert len(fake.posts) == 2


def test_dry_run_prints_and_writes_nothing(cfg, store):
    add_candidate(store, 1, first_come=True)
    store.dry_run = True
    out = io.StringIO()
    log = LogChannel(dry_run=True, max_chars=2000, out=io.StringIO())
    s = run_send(cfg=cfg, store=store, log_channel=log, now=at(12), urgent_only=False, client=None, out=out)
    assert out.getvalue().startswith("#行動 【先着・無料】商品1")
    assert len(s.sent) == 1
    store.dry_run = False
    assert statuses(store) == {"candidate": 1}
    assert store.conn.execute("SELECT COUNT(*) FROM notifications").fetchone()[0] == 0


def test_labels_and_links():
    c = cand("refund_first", deadline=at(23, 59, day=15))
    c.conditions = "レシート応募、1人1回"
    assert action_message(c).splitlines()[:2] == ["【先着・全額返金】p（実質0円）", "締切：10/15 23:59　条件：レシート応募、1人1回"]
    c = cand("free_game", "game", benefit=3350)
    assert action_message(c).splitlines()[0] == "【無料配布】p（3,350円相当）"
    # AIが返した応募URLは、本文に書かれているときだけ使う
    c = cand()
    c.apply_url = "https://made-up.example.com/apply"
    assert action_message(c).splitlines()[2] == c.url
    c.body = "応募はこちら https://made-up.example.com/apply から"
    assert action_message(c).splitlines()[2] == "https://made-up.example.com/apply"


def test_quiet_and_slots(cfg):
    q = cfg.quiet_hours
    assert is_quiet(at(23), q["start"], q["end"]) and is_quiet(at(6, 59), q["start"], q["end"])
    assert not is_quiet(at(7), q["start"], q["end"]) and not is_quiet(at(22, 59), q["start"], q["end"])
    w = cfg.send.slot_window_minutes
    assert in_slot(at(12), cfg.select_slots, w) == "12:00"
    assert in_slot(at(12, 29), cfg.select_slots, w) == "12:00"
    assert in_slot(at(12, 30), cfg.select_slots, w) is None
    assert in_slot(at(19, 5), cfg.select_slots, w) == "19:00"
    assert in_slot(at(15), cfg.select_slots, w) is None


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _pin_send_numbers(cfg):
    """このファイルのテストは、上限3件・閾値60点を前提に書いている（config.yaml の調整に左右されないように固定）。"""
    cfg.daily_cap = 3
    cfg.score_threshold = 60

