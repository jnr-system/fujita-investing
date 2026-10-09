"""取得の共通処理（6.5 取得のマナー、12章 リトライ）。"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional
from urllib.parse import urlsplit

import httpx

from .. import __version__


class FetchError(Exception):
    """取得に失敗した（再試行のあとも）。"""


class ParseError(Exception):
    """取得はできたが、中身を読めなかった。"""


@dataclass
class FetchResult:
    status: int  # 200 か 304
    content: bytes
    etag: Optional[str]
    last_modified: Optional[str]
    final_url: str


def user_agent(contact: str) -> str:
    base = f"otoku/{__version__} (personal non-commercial use"
    return f"{base}; contact: {contact})" if contact else f"{base})"


class Fetcher:
    """同じホストへのリクエストは直列で、前回から host_spacing 秒以上あける。"""

    def __init__(self, *, contact: str, timeout: float, host_spacing: float, retry: int,
                 client: Optional[httpx.Client] = None, sleep: Callable[[float], None] = time.sleep,
                 clock: Callable[[], float] = time.monotonic):
        self._client = client or httpx.Client(timeout=timeout, headers={"User-Agent": user_agent(contact)})
        if client is not None:
            self._client.headers["User-Agent"] = user_agent(contact)
        self._spacing = host_spacing
        self._retry = retry
        self._sleep = sleep
        self._clock = clock
        self._last: dict[str, float] = {}

    def close(self) -> None:
        self._client.close()

    def _wait_for_host(self, host: str) -> None:
        last = self._last.get(host)
        if last is not None:
            wait = self._spacing - (self._clock() - last)
            if wait > 0:
                self._sleep(wait)
        self._last[host] = self._clock()

    def get_status(self, url: str) -> tuple[int, bytes]:
        """どのステータスでも返す（robots.txt 用）。通信エラーと5xxだけ再試行し、それでもだめなら FetchError。"""
        host = (urlsplit(url).hostname or "").lower()
        error = "不明なエラー"
        for _ in range(1 + self._retry):
            self._wait_for_host(host)
            try:
                r = self._client.get(url, follow_redirects=True)
            except httpx.HTTPError as e:
                error = f"{type(e).__name__}: {e}"
                continue
            if r.status_code < 500:
                return r.status_code, r.content
            error = f"HTTP {r.status_code}"
        raise FetchError(error)

    def get(self, url: str, *, etag: Optional[str] = None, last_modified: Optional[str] = None) -> FetchResult:
        headers = {}
        if etag:
            headers["If-None-Match"] = etag
        if last_modified:
            headers["If-Modified-Since"] = last_modified
        host = (urlsplit(url).hostname or "").lower()
        error = "不明なエラー"
        for _ in range(1 + self._retry):
            self._wait_for_host(host)
            try:
                r = self._client.get(url, headers=headers, follow_redirects=True)
            except httpx.HTTPError as e:
                error = f"{type(e).__name__}: {e}"
                continue
            if r.status_code == 304:
                return FetchResult(304, b"", etag, last_modified, str(r.url))
            if r.status_code == 200:
                return FetchResult(200, r.content, r.headers.get("etag"), r.headers.get("last-modified"), str(r.url))
            error = f"HTTP {r.status_code}"
        raise FetchError(error)
