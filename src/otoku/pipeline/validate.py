"""8.4 検証。迷ったら落とす側に倒す。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from ..db import Store
from ..models import A_GENRES, B_GENRES, Extraction, fmt_jst, parse_jst


@dataclass
class Verdict:
    status: str  # candidate / waiting / dropped
    reason: Optional[str]
    scope: Optional[str]
    start_at: Optional[datetime] = None
    deadline_at: Optional[datetime] = None


def _dropped(reason: str, scope: Optional[str] = None) -> Verdict:
    return Verdict("dropped", reason, scope)


def validate(x: Extraction, now: datetime, *, min_confidence: float, genres_enabled: list[str]) -> Verdict:
    if x.kind == "excluded":
        return _dropped(f"AI除外: {x.exclude_reason or '理由なし'}")
    scope = "A" if x.kind == "lottery" else "B"
    if x.genre not in genres_enabled:
        return _dropped(f"スコープ外のジャンル: {x.genre}", scope)
    # 2章：Aは tcg・whisky・console の抽選、Bは food〜game の還元・無料。組み合わせが違うものはスコープ外
    if scope == "A" and x.genre not in A_GENRES:
        return _dropped(f"スコープ外: 抽選だがジャンルが {x.genre}", scope)
    if scope == "B" and x.genre not in B_GENRES:
        return _dropped(f"スコープ外: {x.kind} だがジャンルが {x.genre}", scope)
    if x.kind == "free_game" and x.genre != "game":
        return _dropped(f"スコープ外: free_game だがジャンルが {x.genre}", scope)
    if x.confidence < min_confidence:
        return _dropped(f"確信度不足 {x.confidence:.2f}", scope)
    if x.requires_subscription:
        return _dropped("継続購入・定期契約・有料会員が条件", scope)
    try:
        start = parse_jst(x.start_at) if x.start_at else None
        deadline = parse_jst(x.deadline_at, end_of_day=True) if x.deadline_at else None
    except ValueError:
        return _dropped(f"日時を読めない（start_at={x.start_at}, deadline_at={x.deadline_at}）", scope)
    if deadline and deadline < now:
        return _dropped("締切が過去", scope)
    if not x.actionable_now:
        if start and start > now:
            return Verdict("waiting", f"開始待ち {fmt_jst(start)}", scope, start, deadline)
        return _dropped("今は応募・受取できない", scope)
    return Verdict("candidate", None, scope, start, deadline)


def promote_waiting(store: Store, now: datetime) -> list[tuple[str, str, str]]:
    """開始時刻を過ぎた waiting を再評価する。締切が過ぎていれば expired、それ以外は candidate。
    返り値は #ログ 用の (status, title, source_id)。"""
    changed = []
    for w in store.waiting_items():
        if w.start_at and w.start_at > now:
            continue
        status = "expired" if (w.deadline_at and w.deadline_at < now) else "candidate"
        store.set_item_status(w.id, status)
        changed.append((status, w.title, w.source_id))
    return changed
