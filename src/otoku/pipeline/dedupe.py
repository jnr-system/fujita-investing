"""8.1 重複排除：URLを正規化してハッシュ化する。同じURLは本文が変わっても再処理しない。"""
from __future__ import annotations

import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

# 計測用のクエリ
_TRACKING_PREFIXES = ("utm_",)
_TRACKING_KEYS = {"fbclid", "gclid", "yclid", "dclid", "msclkid", "mc_cid", "mc_eid", "igshid", "_hsenc", "_hsmi"}
_DEFAULT_PORTS = {"http": 80, "https": 443}


def normalize_url(url: str) -> str:
    """計測パラメータを除き、末尾のスラッシュをそろえる（ルート以外は付けない）。
    スキームとホストは小文字、#以降は捨て、残りのクエリは並べ替える。"""
    p = urlsplit(url.strip())
    scheme = p.scheme.lower()
    host = (p.hostname or "").lower()
    netloc = host if p.port in (None, _DEFAULT_PORTS.get(scheme)) else f"{host}:{p.port}"
    path = p.path or "/"
    if len(path) > 1:
        path = path.rstrip("/") or "/"
    query = sorted((k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
                   if not k.lower().startswith(_TRACKING_PREFIXES) and k.lower() not in _TRACKING_KEYS)
    return urlunsplit((scheme, netloc, path, urlencode(query), ""))


def url_hash(url: str) -> str:
    return hashlib.sha256(normalize_url(url).encode("utf-8")).hexdigest()


def content_hash(title: str, body: str) -> str:
    return hashlib.sha256(f"{title}\n{body}".encode("utf-8")).hexdigest()
