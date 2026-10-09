"""8.7 送信選定（1日の上限、緊急と通常、静音時間）。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Optional

from ..db import Candidate
from ..models import JST


def jst_day_bounds(now: datetime) -> tuple[datetime, datetime]:
    """上限を数える1日（JSTの0時〜翌0時）。"""
    start = datetime.combine(now.astimezone(JST).date(), time(0, 0), tzinfo=JST)
    return start, start + timedelta(days=1)


def _hm(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def is_quiet(now: datetime, start: str, end: str) -> bool:
    """静音時間か（例：23:00〜07:00。日をまたぐ）。"""
    t = now.astimezone(JST).time()
    s, e = _hm(start), _hm(end)
    return (s <= t or t < e) if s > e else (s <= t < e)


def in_slot(now: datetime, slots: list[str], window_minutes: int) -> Optional[str]:
    """通常の選定枠の時刻（から window_minutes 分のあいだ）なら、その枠を返す。"""
    local = now.astimezone(JST)
    for slot in slots:
        start = datetime.combine(local.date(), _hm(slot), tzinfo=JST)
        if start <= local < start + timedelta(minutes=window_minutes):
            return slot
    return None


@dataclass
class Unit:
    """1通の通知になるまとまり（同じグループの候補。グループのない候補は1件で1つ）。"""
    items: list[Candidate]

    @property
    def score(self) -> float:
        return max(c.score or 0.0 for c in self.items)

    @property
    def urgent(self) -> bool:
        return any(c.urgent for c in self.items)

    @property
    def deadline_at(self) -> Optional[datetime]:
        return min((c.deadline_at for c in self.items if c.deadline_at), default=None)

    @property
    def id(self) -> int:
        return min(c.id for c in self.items)


def make_units(candidates: list[Candidate]) -> list[Unit]:
    by_group: dict[object, list[Candidate]] = {}
    for c in candidates:
        by_group.setdefault(c.group_id if c.group_id is not None else f"item:{c.id}", []).append(c)
    return [Unit(items) for items in by_group.values()]


@dataclass
class Plan:
    send: list[Unit] = field(default_factory=list)
    expire: list[Unit] = field(default_factory=list)  # 上限で送れず、締切も不明なもの
    eligible: int = 0
    remaining: int = 0


def plan(units: list[Unit], *, threshold: float, remaining: int, urgent_only: bool) -> Plan:
    """閾値以上（緊急のみのときは緊急だけ）を、スコアの高い順・締切の近い順に残り枠まで送る。
    上限で送れなかった候補は、締切があれば翌日以降に再評価（候補のまま）、締切が不明なら expired（8.7）。"""
    far = datetime.max.replace(tzinfo=JST)
    eligible = [u for u in units if u.score >= threshold and (u.urgent or not urgent_only)]
    eligible.sort(key=lambda u: (-u.score, u.deadline_at or far, u.id))
    remaining = max(remaining, 0)
    p = Plan(send=eligible[:remaining], eligible=len(eligible), remaining=remaining)
    p.expire = [u for u in eligible[remaining:] if u.deadline_at is None]
    return p
