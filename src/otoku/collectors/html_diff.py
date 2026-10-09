"""一覧ページのリンク集合の差分（6.1 html_diff）。

増えたURLだけを新着とする（どのURLが既出かは重複排除の raw_items で判定する）。
個別ページは取りに行かず、一覧ページの文字（リンクの文字・画像の alt・項目の文言）だけを使う（2026-10-09 ユーザー判断）。
どのリンクを見るかは sources.yaml の link_selector（CSSセレクタ）と link_pattern（URLの正規表現）で絞る。
"""
from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from ..models import RawItem, Source

TITLE_MAX = 200
BODY_MAX = 1000
SHORT_TEXT = 15  # リンクの文字がこれより短い（「詳細を見る」など）ときは、囲んでいる項目の文字も使う


def _text(el) -> str:
    return re.sub(r"\s+", " ", el.get_text(" ", strip=True)).strip()


def _anchor_text(a) -> str:
    parts = [_text(a)]
    parts += [img.get("alt", "").strip() for img in a.find_all("img")]
    if a.get("title"):
        parts.append(a["title"].strip())
    return " ".join(dict.fromkeys(p for p in parts if p))


def _context(a, url: str, base_url: str) -> str:
    """そのリンクの項目（カード）の文字。そのリンク（と同じURLのリンク）だけを含む、いちばん外側の囲みを項目とみなす。
    タグ名やクラス名には頼らない。"""
    card = None
    for parent in a.parents:
        if parent.name in (None, "[document]", "body", "html"):
            break
        hrefs = {urljoin(base_url, x.get("href", "").strip()) for x in parent.find_all("a", href=True)}
        if hrefs - {url}:
            break
        card = parent
    return _text(card)[:BODY_MAX] if card else ""


def extract_links(html: bytes, base_url: str, *, selector: str | None = None,
                  pattern: str | None = None) -> list[tuple[str, str, str]]:
    """(URL, リンクの文字, 項目の文字) の一覧。同じURLは最初の1つだけ。"""
    soup = BeautifulSoup(html, "html.parser")
    if selector:
        anchors = []
        for el in soup.select(selector):
            anchors += [el] if el.name == "a" else el.find_all("a", href=True)
    else:
        anchors = soup.find_all("a", href=True)
    rx = re.compile(pattern) if pattern else None
    seen: dict[str, tuple[str, str, str]] = {}
    for a in anchors:
        href = (a.get("href") or "").strip()
        if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
            continue
        url = urljoin(base_url, href)
        if not url.startswith(("http://", "https://")) or (rx and not rx.search(url)) or url in seen:
            continue
        text = _anchor_text(a)
        context = _context(a, url, base_url)
        if len(text) < SHORT_TEXT and context:
            text = f"{text} {context}".strip() if text not in context else context
        seen[url] = (url, text, context)
    return list(seen.values())


def parse(content: bytes, source: Source, final_url: str | None = None) -> list[RawItem]:
    """0件はエラーにしない（実施中のキャンペーンがない日もあるため）。件数は collect の集計に出る。"""
    links = extract_links(content, final_url or source.url, selector=source.link_selector,
                          pattern=source.link_pattern)
    return [RawItem(source_id=source.id, url=url, title=(text or url)[:TITLE_MAX],
                    body=(context if context and context != text else "")[:BODY_MAX])
            for url, text, context in links]
