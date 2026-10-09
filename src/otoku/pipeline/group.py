"""8.5 グルーピング：同じ商品・同じ企画を1件にまとめる。

キーは scope ＋ 正規化した product。一致は完全一致だけ（あいまい一致は使わない）。
表記ゆれでまとまらないことはあっても、別の商品を誤ってまとめないことを優先する。
"""
from __future__ import annotations

import unicodedata
from typing import Optional


def normalize_product(product: str) -> str:
    """全角半角を統一し（NFKC）、小文字にし、空白と記号を除く（文字と数字だけ残す）。"""
    s = unicodedata.normalize("NFKC", product or "").lower()
    return "".join(ch for ch in s if unicodedata.category(ch)[0] in ("L", "N"))


def group_key(scope: Optional[str], product: Optional[str]) -> Optional[str]:
    """商品名が空になるものはまとめない（None）。"""
    norm = normalize_product(product or "")
    return f"{scope}:{norm}" if scope and norm else None
