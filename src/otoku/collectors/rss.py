"""RSS/Atom の読み取り。"""
from __future__ import annotations

import calendar
import re
from datetime import datetime, timezone

import feedparser
from bs4 import BeautifulSoup

from ..models import RawItem, Source
from . import ParseError


def html_to_text(html: str) -> str:
    if not html:
        return ""
    text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)
    return re.sub(r"\s+", " ", text).strip()


def _published(entry) -> datetime | None:
    t = entry.get("published_parsed") or entry.get("updated_parsed")
    return datetime.fromtimestamp(calendar.timegm(t), tz=timezone.utc) if t else None


def parse(content: bytes, source: Source) -> list[RawItem]:
    feed = feedparser.parse(content)
    if not feed.entries and not feed.get("version"):  # version が空＝RSS/Atom として認識できなかった（HTMLなど）
        raise ParseError(f"フィードとして読めません: {feed.get('bozo_exception') or 'RSS/Atom ではない'}")
    items = []
    for e in feed.entries:
        url = e.get("link") or e.get("id")
        if not url:
            continue
        body = e["content"][0].get("value", "") if e.get("content") else e.get("summary", "")
        items.append(RawItem(source_id=source.id, url=url.strip(), title=html_to_text(e.get("title", "")),
                             body=html_to_text(body), published_at=_published(e)))
    return items
