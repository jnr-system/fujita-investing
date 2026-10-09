"""取得した中身を、情報源の方式（rss・json_api・html_diff・sitemap）ごとに読む。"""
from __future__ import annotations

from datetime import datetime

from ..models import RawItem, Source
from . import FetchResult, html_diff, json_api, rss, sitemap


def parse_source(src: Source, res: FetchResult, now: datetime) -> list[RawItem]:
    if src.type == "rss":
        return rss.parse(res.content, src)
    if src.type == "json_api":
        return json_api.parse(res.content, src, now)
    if src.type == "html_diff":
        return html_diff.parse(res.content, src, res.final_url)
    return sitemap.parse(res.content, src)
