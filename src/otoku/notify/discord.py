"""Discord への送信（8.8：Botトークンを使い REST API だけで実装する）。"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Callable, Optional, TextIO
from urllib.parse import quote

import httpx

from .. import __version__

API = "https://discord.com/api/v10"
SUPPRESS_EMBEDS = 1 << 2  # リンクのプレビュー（埋め込み）を出さない
REACTIONS = ("✅", "⏰", "❌")  # 8.8：応募した／あとでやる／いらない
REACTION_NAMES = {"✅": "applied", "⏰": "later", "❌": "reject"}  # feedback.reaction の値（7章）


class DiscordError(Exception):
    def __init__(self, message: str, status: Optional[int] = None):
        super().__init__(message)
        self.status = status


class DiscordClient:
    def __init__(self, token: str, *, max_429_retries: int, client: Optional[httpx.Client] = None,
                 sleep: Callable[[float], None] = time.sleep):
        self._client = client or httpx.Client(timeout=20)
        self._headers = {"Authorization": f"Bot {token}",
                         "User-Agent": f"DiscordBot (otoku, {__version__})"}
        self._max_429 = max_429_retries
        self._sleep = sleep

    def _request(self, method: str, path: str, **kw) -> httpx.Response:
        """429 は Retry-After に従って待ってから送り直す（12章）。"""
        for _ in range(1 + self._max_429):
            try:
                r = self._client.request(method, f"{API}{path}", headers=self._headers, **kw)
            except httpx.HTTPError as e:
                raise DiscordError(f"{type(e).__name__}: {e}") from e
            if r.status_code == 429:
                self._sleep(_retry_after(r))
                continue
            if r.status_code >= 300:
                raise DiscordError(f"HTTP {r.status_code}: {r.text[:200]}", status=r.status_code)
            return r
        raise DiscordError("429 が続いたため送信をあきらめました")

    def post_message(self, channel_id: str, content: str, *, suppress_embeds: bool = False,
                     reply_to: Optional[str] = None) -> str:
        """POST /channels/{id}/messages。reply_to を渡すと、そのメッセージへの返信として送る（8.10 リマインド）。"""
        body = {"content": content, "allowed_mentions": {"parse": []}}  # タイトル中の @everyone などを効かせない
        if suppress_embeds:
            body["flags"] = SUPPRESS_EMBEDS
        if reply_to:
            body["message_reference"] = {"message_id": reply_to, "fail_if_not_exists": False}
        return str(self._request("POST", f"/channels/{channel_id}/messages", json=body).json().get("id", ""))

    def me(self) -> str:
        """GET /users/@me。Bot自身のユーザーID（自分で付けたリアクションを数えないため）。"""
        return str(self._request("GET", "/users/@me").json()["id"])

    def reaction_users(self, channel_id: str, message_id: str, emoji: str) -> list[str]:
        """GET /channels/{id}/messages/{message_id}/reactions/{emoji}。リアクションを付けたユーザーのID。"""
        users, after = [], None
        while True:
            params = {"limit": 100} | ({"after": after} if after else {})
            page = self._request("GET", f"/channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}",
                                 params=params).json()
            users += [str(u["id"]) for u in page]
            if len(page) < 100:
                return users
            after = page[-1]["id"]

    def edit_message(self, channel_id: str, message_id: str, content: str) -> None:
        """PATCH /channels/{id}/messages/{message_id}（8.5：店舗の追記）。"""
        body = {"content": content, "allowed_mentions": {"parse": []}, "flags": SUPPRESS_EMBEDS}
        self._request("PATCH", f"/channels/{channel_id}/messages/{message_id}", json=body)

    def add_reaction(self, channel_id: str, message_id: str, emoji: str) -> None:
        """PUT /channels/{id}/messages/{message_id}/reactions/{emoji}/@me。"""
        self._request("PUT", f"/channels/{channel_id}/messages/{message_id}/reactions/{quote(emoji)}/@me")


def _retry_after(r: httpx.Response) -> float:
    for value in (r.headers.get("Retry-After"), _json_retry_after(r)):
        try:
            if value is not None:
                return max(float(value), 0.0)
        except ValueError:
            pass
    return 1.0


def _json_retry_after(r: httpx.Response):
    try:
        return r.json().get("retry_after")
    except ValueError:
        return None


def pack(lines: list[str], max_chars: int) -> list[str]:
    """1行ずつのまま、1メッセージ max_chars 文字以内にまとめる。"""
    messages, cur = [], ""
    for line in lines:
        line = line[:max_chars]
        if cur and len(cur) + 1 + len(line) > max_chars:
            messages.append(cur)
            cur = line
        else:
            cur = f"{cur}\n{line}" if cur else line
    if cur:
        messages.append(cur)
    return messages


class LogChannel:
    """#ログ。dry-run では送らずに標準出力へ出す。
    送れなかったメッセージは outbox に残し、次の実行の最初に送り直す（12章）。"""

    def __init__(self, *, dry_run: bool, max_chars: int, client: Optional[DiscordClient] = None,
                 channel_id: str = "", outbox: Optional[Path] = None, out: TextIO = sys.stdout):
        self.dry_run = dry_run
        self.max_chars = max_chars
        self.client = client
        self.channel_id = channel_id
        self.outbox = outbox
        self.out = out
        self.lines: list[str] = []

    def add(self, line: str) -> None:
        self.lines.append(line)

    def _pending(self) -> list[str]:
        if not self.outbox or not self.outbox.exists():
            return []
        return [json.loads(x)["content"] for x in self.outbox.read_text(encoding="utf-8").splitlines() if x.strip()]

    def flush(self) -> list[str]:
        """送れなかったメッセージを返す（outbox にも残す）。"""
        if self.dry_run:
            for line in self.lines:
                print(f"#ログ {line}", file=self.out)
            self.lines = []
            return []
        messages = self._pending() + pack(self.lines, self.max_chars)
        self.lines = []
        failed = []
        for i, m in enumerate(messages):
            try:
                self.client.post_message(self.channel_id, m)
            except DiscordError:
                failed = messages[i:]  # 順番を保つため、失敗した以降はまとめて次回へ
                break
        if self.outbox:
            if failed:
                self.outbox.parent.mkdir(parents=True, exist_ok=True)
                self.outbox.write_text("".join(json.dumps({"content": m}, ensure_ascii=False) + "\n" for m in failed),
                                       encoding="utf-8")
            elif self.outbox.exists():
                self.outbox.unlink()
        return failed
