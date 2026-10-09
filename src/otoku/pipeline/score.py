"""8.6 スコア（0〜100）：base[kind] + genre_weight[genre] + urgency + benefit_bonus + source_weight。"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..db import Candidate
from ..models import Weights


def hours_left(deadline: Optional[datetime], now: datetime) -> Optional[float]:
    return None if deadline is None else (deadline - now).total_seconds() / 3600


def urgency(c: Candidate, now: datetime, w: Weights) -> float:
    """締切の点数と先着の点数のうち、大きいほうだけ（2026-10-09 ユーザー確認）。"""
    points = 0.0
    left = hours_left(c.deadline_at, now)
    if left is not None and left >= 0:
        for rule in sorted(w.urgency, key=lambda r: r.within_hours):
            if left <= rule.within_hours:
                points = rule.points
                break
    if c.first_come:
        points = max(points, w.first_come)
    return points


def benefit_bonus(c: Candidate, w: Weights) -> float:
    if c.benefit_yen is None:
        return 0.0
    for rule in sorted(w.benefit_bonus, key=lambda r: r.min_yen, reverse=True):
        if c.benefit_yen >= rule.min_yen:
            return rule.points
    return 0.0


def score(c: Candidate, now: datetime, w: Weights, source_weight: float) -> float:
    sw = min(max(source_weight, w.source_weight.min), w.source_weight.max)
    total = w.base.get(c.kind, 0.0) + w.genre.get(c.genre or "", 0.0) + urgency(c, now, w) + benefit_bonus(c, w) + sw
    return min(max(total, 0.0), 100.0)


def is_urgent(c: Candidate, now: datetime, urgent_within_hours: float) -> bool:
    """8.7 緊急：先着、または締切まで urgent_within_hours 時間以内。"""
    left = hours_left(c.deadline_at, now)
    return c.first_come or (left is not None and 0 <= left <= urgent_within_hours)
