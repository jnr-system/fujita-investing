"""公開JSONの読み取り。JSONの形は情報源ごとに違うので、情報源IDごとの読み取り方を持つ。

形はフェーズ0（docs/sources_review.md）で実際に取得して確かめたもの。
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Callable
from urllib.parse import urljoin

from ..models import RawItem, Source, parse_jst
from . import ParseError

_CONTROL = re.compile(r"[\x00-\x1f\x7f]+")


def _clean(s) -> str:
    return re.sub(r"\s+", " ", _CONTROL.sub(" ", str(s or ""))).strip()


def _load(content: bytes, *, jsonp: str | None = None):
    text = content.decode("utf-8-sig").strip()
    if jsonp:
        m = re.match(rf"^{re.escape(jsonp)}\s*\((.*)\)\s*;?\s*$", text, re.S)
        if m:
            text = m.group(1)
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ParseError(f"JSONとして読めません: {e}") from e


# キリンの一覧データの印と、一覧ページ（campaign_render.js）が表示に使っている名前
_KIRIN_TAGS = {"imasugu": "今すぐ応募", "konyu": "購入して応募", "zettai": "絶対もらえる",
               "mail": "メールアドレスで応募", "hagaki": "はがきで応募"}


def _kirin(content: bytes, source: Source, now: datetime) -> list[RawItem]:
    """JSONP（campaign([...])）。2021年からの終了分も入っているので、受付終了日（end）が過ぎたものは外す。"""
    data = _load(content, jsonp="campaign")
    if not isinstance(data, list):
        raise ParseError("キリン: 配列ではありません")
    items = []
    for e in data:
        if not isinstance(e, dict) or not e.get("link") or not e.get("title"):
            continue
        try:
            end = parse_jst(e["end"]) if e.get("end") else None
        except ValueError:
            end = None
        if end and end < now:
            continue
        tags = [label for key, label in _KIRIN_TAGS.items() if e.get(key) is True]
        lines = [f"応募期間：{e.get('start') or '不明'} 〜 {e.get('end') or '不明'}（JST）"]
        if tags:
            lines.append("印：" + "、".join(tags))
        for key in ("read", "attention"):
            if e.get(key):
                lines.append(_clean(e[key]))
        items.append(RawItem(source_id=source.id, url=urljoin(source.url, e["link"]), title=_clean(e["title"]),
                             body="\n".join(lines)))
    return items


def _matsuzakaya_topics(content: bytes, source: Source, now: datetime) -> list[RawItem]:
    """[{カテゴリ名: [{title, url, period, annotation, date}, ...]}, ...]。同じ記事が複数のカテゴリに載る。"""
    data = _load(content)
    if not isinstance(data, list):
        raise ParseError("松坂屋: 配列ではありません")
    by_url: dict[str, RawItem] = {}
    for block in data:
        if not isinstance(block, dict):
            continue
        for category, entries in block.items():
            for e in entries or []:
                if not isinstance(e, dict) or not e.get("url") or not e.get("title"):
                    continue
                url = urljoin(source.url, e["url"])
                if url in by_url:
                    continue
                lines = [f"カテゴリ：{category}"]
                if e.get("period"):
                    lines.append(f"期間：{_clean(e['period'])}")
                if e.get("annotation"):
                    lines.append(_clean(e["annotation"]))
                if e.get("date"):
                    lines.append(f"掲載日：{e['date']}")
                by_url[url] = RawItem(source_id=source.id, url=url, title=_clean(e["title"]), body="\n".join(lines))
    return list(by_url.values())


ADAPTERS: dict[str, Callable[[bytes, Source, datetime], list[RawItem]]] = {
    "kirin_campaign": _kirin,
    "matsuzakaya_ueno_topics": _matsuzakaya_topics,
}


def parse(content: bytes, source: Source, now: datetime) -> list[RawItem]:
    adapter = ADAPTERS.get(source.id)
    if adapter is None:
        raise ParseError(f"{source.id}: このJSONの読み取り方が未定義です（collectors/json_api.py の ADAPTERS）")
    return adapter(content, source, now)
