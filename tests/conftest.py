from __future__ import annotations

import io
from datetime import datetime
from pathlib import Path

import httpx
import pytest

from otoku.collectors import Fetcher
from otoku.db import Store
from otoku.models import JST, Source, load_config
from otoku.notify.discord import LogChannel

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures"
NOW = datetime(2026, 10, 9, 12, 0, tzinfo=JST)


@pytest.fixture
def cfg():
    return load_config(ROOT / "config" / "config.yaml")


def make_source(id="test_rss", type="rss", url="https://feeds.example.com/feed.xml", **kw) -> Source:
    return Source(id=id, type=type, url=url, scope=kw.pop("scope", "B"), genre_hint=kw.pop("genre_hint", ["food"]),
                  min_interval_minutes=kw.pop("min_interval_minutes", 30), enabled=kw.pop("enabled", True), **kw)


def ai_fixture(name: str) -> str:
    p = FIX / "ai" / (name if "." in name else f"{name}.json")
    return p.read_text(encoding="utf-8")


class FakeAI:
    """Gemini の代わり。タイトルに含まれる語で、返す応答（tests/fixtures/ai）を選ぶ。"""

    def __init__(self, by_title: dict[str, str | list[str]], default: str = "excluded_lottery_refund"):
        self.by_title = by_title
        self.default = default
        self.prompts: list[str] = []

    def __call__(self, system: str, user: str) -> str:
        self.prompts.append(user)
        for word, answer in self.by_title.items():
            if word in user:
                if isinstance(answer, list):  # 呼ばれるたびに次の応答を返す
                    return ai_fixture(answer.pop(0) if len(answer) > 1 else answer[0])
                return ai_fixture(answer)
        return ai_fixture(self.default)


class Router:
    """httpx.MockTransport 用。URLごとに応答を返し、受けたリクエストを記録する。"""

    def __init__(self, routes: dict[str, list[httpx.Response] | httpx.Response]):
        self.routes = routes
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        r = self.routes.get(str(request.url))
        if r is None:
            return httpx.Response(404)
        if isinstance(r, list):
            return r.pop(0) if len(r) > 1 else r[0]
        return r


def make_fetcher(router: Router, *, retry: int = 1) -> Fetcher:
    client = httpx.Client(transport=httpx.MockTransport(router))
    return Fetcher(contact="test@example.invalid", timeout=5, host_spacing=0, retry=retry, client=client,
                   sleep=lambda s: None)


@pytest.fixture
def store(tmp_path):
    s = Store(tmp_path / "otoku.db")
    yield s
    s.close()


@pytest.fixture
def log_out():
    return io.StringIO()


@pytest.fixture
def dry_log(cfg, log_out):
    return LogChannel(dry_run=True, max_chars=cfg.discord.max_message_chars, out=log_out)
