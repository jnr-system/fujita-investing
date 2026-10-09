"""sitemap.xml の差分（6.1 sitemap）。増えた <loc> を新着とする（既出かどうかは重複排除で判定する）。

サイトマップにはURLと更新日しかないので、タイトルはURLになる。link_pattern でURLを絞れる。
サイトマップインデックス（子のサイトマップの一覧）には対応しない（子のサイトマップのURLを sources.yaml に書く）。
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET

from ..models import RawItem, Source
from . import ParseError


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse(content: bytes, source: Source) -> list[RawItem]:
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ParseError(f"サイトマップとして読めません: {e}") from e
    if _local(root.tag) == "sitemapindex":
        raise ParseError("サイトマップインデックスには対応していません（子のサイトマップのURLを sources.yaml に書く）")
    if _local(root.tag) != "urlset":
        raise ParseError(f"サイトマップではありません（{_local(root.tag)}）")
    rx = re.compile(source.link_pattern) if source.link_pattern else None
    items = []
    for url in root:
        fields = {_local(c.tag): (c.text or "").strip() for c in url}
        loc = fields.get("loc")
        if not loc or (rx and not rx.search(loc)):
            continue
        body = f"更新日：{fields['lastmod']}" if fields.get("lastmod") else ""
        items.append(RawItem(source_id=source.id, url=loc, title=loc, body=body))
    return items
