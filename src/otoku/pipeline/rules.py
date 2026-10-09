"""8.2 ルールフィルタ（AIに渡す前に件数を減らす）。"""
from __future__ import annotations

import unicodedata


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").lower()


class RuleFilter:
    """対象キーワードはタイトルと本文、除外キーワードはタイトルだけを見る。
    本文には「受付終了：10月15日」のような書き方が多く、本文まで見ると受付中の告知まで落ちるため。"""

    def __init__(self, include: list[str], exclude: list[str]):
        self.include = [(w, _norm(w)) for w in include]
        self.exclude = [(w, _norm(w)) for w in exclude]

    def check(self, title: str, body: str) -> tuple[bool, str]:
        t = _norm(title)
        for word, n in self.exclude:
            if n in t:
                return False, f"除外キーワード「{word}」"
        text = t + "\n" + _norm(body)
        for word, n in self.include:
            if n in text:
                return True, f"対象キーワード「{word}」"
        return False, "対象キーワードなし"
