"""robots.txt の判定（RFC 9309）。check-sources で使う。

- 自分の名前（otoku）のグループがあればそれ、なければ * のグループに従う。
- 一致する規則のうち最も長いもの。同じ長さなら Allow を優先。* と $ に対応。
- robots.txt が 4xx なら制限なし、5xx や通信できないときは全体を禁止として扱う。
"""
from __future__ import annotations

import re
from urllib.parse import urlsplit

TOKEN = "otoku"


def _groups(text: str) -> list[dict]:
    groups, cur, last_ua = [], None, False
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].strip()
        if ":" not in line:
            continue
        k, v = (x.strip() for x in line.split(":", 1))
        k = k.lower()
        if k == "user-agent":
            if cur is None or not last_ua:
                cur = {"agents": [], "rules": []}
                groups.append(cur)
            cur["agents"].append(v.lower())
            last_ua = True
            continue
        last_ua = False
        if cur is not None and k in ("allow", "disallow"):
            cur["rules"].append((k, v))
    return groups


def _match(pattern: str, path: str) -> bool:
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    rx = "".join(".*" if ch == "*" else re.escape(ch) for ch in body)
    return re.match("^" + rx + ("$" if anchored else ""), path) is not None


def evaluate(text: str, url: str) -> tuple[bool, str]:
    """(許可されているか, 決め手になった規則)。"""
    p = urlsplit(url)
    path = (p.path or "/") + (f"?{p.query}" if p.query else "")
    groups = _groups(text.lstrip("﻿"))
    chosen = [g for g in groups if TOKEN in g["agents"]] or [g for g in groups if "*" in g["agents"]]
    best = None
    for g in chosen:
        for kind, pattern in g["rules"]:
            if pattern and _match(pattern, path):
                cand = (len(pattern), kind == "allow", kind, pattern)
                if best is None or cand[:2] > best[:2]:
                    best = cand
    if best is None:
        return True, "該当する規則なし"
    return best[2] == "allow", f"{best[2].capitalize()}: {best[3]}"


def robots_url(url: str) -> str:
    p = urlsplit(url)
    return f"{p.scheme}://{p.netloc}/robots.txt"
