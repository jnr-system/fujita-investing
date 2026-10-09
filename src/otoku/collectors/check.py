"""check-sources：情報源の疎通と robots.txt の確認（5章・6.5）。

robots.txt で禁止されていたら、その情報源を止めて報告する（回避はしない）。止める期間は次の確認（毎朝）まで。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional

from ..db import Store
from ..models import Source, fmt_jst
from . import FetchError, Fetcher, ParseError
from .parse import parse_source
from .robots import evaluate, robots_url

PAUSE_UNTIL_NEXT_CHECK = timedelta(hours=25)


@dataclass
class CheckResult:
    source_id: str
    ok: bool
    detail: str


def _robots(fetcher: Fetcher, url: str, cache: dict) -> tuple[Optional[str], str]:
    """(robots.txt の本文 or None, 説明)。None で説明が「なし」なら制限なし、それ以外の None は全体禁止扱い。"""
    key = robots_url(url)
    if key not in cache:
        try:
            status, body = fetcher.get_status(key)
        except FetchError as e:
            cache[key] = (None, f"robots.txt を確認できない（{e}）")
        else:
            if status == 200:
                cache[key] = (body.decode("utf-8", "replace"), "")
            elif 400 <= status < 500:
                cache[key] = (None, "なし")
            else:
                cache[key] = (None, f"robots.txt が HTTP {status} で確認できない")
    return cache[key]


def check_sources(sources: list[Source], store: Store, fetcher: Fetcher, now: datetime) -> list[CheckResult]:
    results, cache = [], {}
    for src in sources:
        if not src.enabled:
            continue
        text, note = _robots(fetcher, src.url, cache)
        if text is None and note != "なし":
            # 5xx や通信できないときは全体を禁止として扱う（RFC 9309）
            store.pause(src.id, now + PAUSE_UNTIL_NEXT_CHECK)
            results.append(CheckResult(src.id, False, f"{note}ので、次の確認まで止めます"))
            continue
        if text is None:
            allowed, rule = True, "robots.txt なし"
        else:
            allowed, rule = evaluate(text, src.url)
        if not allowed:
            store.pause(src.id, now + PAUSE_UNTIL_NEXT_CHECK)
            results.append(CheckResult(src.id, False, f"robots.txt で取得できない（{rule}）。次の確認まで止めます"))
            continue
        state = store.source_state(src.id)
        try:
            res = fetcher.get(src.url)
            items = parse_source(src, res, now)
        except (FetchError, ParseError) as e:
            results.append(CheckResult(src.id, False, f"取得できない（{e}）"))
            continue
        if src.type == "html_diff" and not items:
            results.append(CheckResult(src.id, False, "監視対象のリンクが0件（実施中がないか、ページの作りが変わった）"))
            continue
        detail = f"OK（{src.type} {len(items)}件）"
        if state.paused_until and state.paused_until > now:
            detail += f"　ただし {fmt_jst(state.paused_until)} まで停止中"
        results.append(CheckResult(src.id, True, detail))
    store.commit()
    return results
