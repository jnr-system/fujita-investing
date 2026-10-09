"""#ログ への送信（REST、429、まとめ送り、未送信の持ち越し、dry-run）。"""
import io
import json

import httpx

from otoku.notify.discord import DiscordClient, LogChannel, pack
from otoku.notify.format import log_line

from .conftest import Router


def client_for(router, sleeps=None):
    return DiscordClient("TOKEN", max_429_retries=5, client=httpx.Client(transport=httpx.MockTransport(router)),
                         sleep=(sleeps.append if sleeps is not None else (lambda s: None)))


URL = "https://discord.com/api/v10/channels/123/messages"


def test_log_line_format():
    assert log_line("dropped", "抽選で返金", "タイトル", "prtimes_all") == "[dropped: 抽選で返金] タイトル / prtimes_all / -"
    assert log_line("candidate", None, "T", "s", 72.4) == "[candidate] T / s / 72"


def test_post_follows_retry_after_on_429():
    sleeps = []
    router = Router({URL: [httpx.Response(429, headers={"Retry-After": "1.5"}, json={"retry_after": 1.5}),
                           httpx.Response(200, json={"id": "999"})]})
    assert client_for(router, sleeps).post_message("123", "hello") == "999"
    assert sleeps == [1.5]
    req = router.requests[-1]
    assert req.headers["Authorization"] == "Bot TOKEN"
    assert json.loads(req.content)["allowed_mentions"] == {"parse": []}


def test_pack_keeps_lines_and_limit():
    lines = [f"[dropped: x] {'あ' * 50} / s / -" for _ in range(100)]
    msgs = pack(lines, 2000)
    assert all(len(m) <= 2000 for m in msgs)
    assert sum(m.count("\n") + 1 for m in msgs) == 100


def test_failed_messages_are_kept_for_next_run(tmp_path):
    outbox = tmp_path / "outbox.jsonl"
    router = Router({URL: httpx.Response(500, text="err")})
    ch = LogChannel(dry_run=False, max_chars=2000, client=client_for(router), channel_id="123", outbox=outbox)
    ch.add("line 1")
    assert ch.flush() == ["line 1"]
    assert outbox.exists()

    router.routes[URL] = httpx.Response(200, json={"id": "1"})
    ch.add("line 2")
    assert ch.flush() == []
    sent = [json.loads(r.content)["content"] for r in router.requests if r.method == "POST"][-2:]
    assert sent == ["line 1", "line 2"]  # 前回の分を先に送る
    assert not outbox.exists()


def test_dry_run_prints_and_does_not_send(tmp_path):
    out = io.StringIO()
    router = Router({})
    ch = LogChannel(dry_run=True, max_chars=2000, client=client_for(router), channel_id="123",
                    outbox=tmp_path / "o.jsonl", out=out)
    ch.add("[candidate] T / s / -")
    ch.flush()
    assert out.getvalue() == "#ログ [candidate] T / s / -\n"
    assert router.requests == [] and not (tmp_path / "o.jsonl").exists()
