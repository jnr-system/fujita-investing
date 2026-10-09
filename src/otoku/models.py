"""設定・情報源・取得データ・AI出力の型と、時刻の扱い。"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Literal, Optional
from zoneinfo import ZoneInfo

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

JST = ZoneInfo("Asia/Tokyo")
A_GENRES = ("tcg", "whisky", "console")
B_GENRES = ("food", "drink", "daily", "cvs", "game")
GENRES = A_GENRES + B_GENRES
KINDS = ("lottery", "refund_all", "refund_first", "free_item", "free_game", "excluded")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_iso(dt: Optional[datetime]) -> Optional[str]:
    """DB保存用（UTCのISO 8601）。"""
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds") if dt else None


def from_iso(s: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(s) if s else None


def fmt_jst(dt: datetime) -> str:
    """表示用（JST、例：10/15 23:59）。"""
    d = dt.astimezone(JST)
    return f"{d.month}/{d.day} {d:%H:%M}"


def parse_jst(s: str, *, end_of_day: bool = False) -> datetime:
    """日時の文字列を読む。タイムゾーンがなければJST、日付だけなら開始は0:00・締切は23:59とみなす。"""
    s = s.strip()
    if len(s) == 10:  # YYYY-MM-DD
        d = datetime.fromisoformat(s).date()
        return datetime.combine(d, time(23, 59) if end_of_day else time(0, 0), tzinfo=JST)
    dt = datetime.fromisoformat(s.replace(" ", "T", 1))
    return dt if dt.tzinfo else dt.replace(tzinfo=JST)


# ---------------------------------------------------------------- 設定

class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str
    type: Literal["rss", "json_api", "sitemap", "html_diff"]
    url: str
    scope: list[Literal["A", "B"]]
    genre_hint: list[str] = []
    min_interval_minutes: int
    enabled: bool
    verified: str = ""
    # html_diff だけで使う（省略可）。2026-10-09 ユーザー確認で 6.2 の形式に追加
    link_selector: Optional[str] = None  # 見る範囲（CSSセレクタ。a ならそのリンク、それ以外なら中のリンク）
    link_pattern: Optional[str] = None   # 見るリンクのURL（正規表現）

    @field_validator("scope", mode="before")
    @classmethod
    def _scope_list(cls, v):
        return [v] if isinstance(v, str) else v


class GeminiConfig(BaseModel):
    model: str
    temperature: float
    max_body_chars: int
    retry_on_invalid: int
    timeout_seconds: float


class Keywords(BaseModel):
    include: list[str]
    exclude: list[str]


class CollectConfig(BaseModel):
    timeout_seconds: float
    host_spacing_seconds: float
    retry: int
    fail_pause_after: int
    pause_hours: int
    interval_tolerance_seconds: int


class DiscordConfig(BaseModel):
    max_message_chars: int
    max_429_retries: int


class UrgencyRule(BaseModel):
    within_hours: float
    points: float


class BenefitRule(BaseModel):
    min_yen: int
    points: float


class SourceWeightRange(BaseModel):
    min: float
    max: float
    step: float


class Weights(BaseModel):
    base: dict[str, float]
    genre: dict[str, float]
    urgency: list[UrgencyRule]
    first_come: float
    benefit_bonus: list[BenefitRule]
    source_weight: SourceWeightRange


class SendConfig(BaseModel):
    urgent_within_hours: float
    slot_window_minutes: int


class FeedbackConfig(BaseModel):
    window: int
    ratio: float
    min_notifications: int
    lookback_days: int


class RemindConfig(BaseModel):
    before_hours: float


class ReportConfig(BaseModel):
    weekly_days: int


class Config(BaseModel):
    daily_cap: int
    score_threshold: float
    min_confidence: float
    quiet_hours: dict
    select_slots: list[str]
    gemini: GeminiConfig
    genres_enabled: list[str]
    weights: Weights
    keywords: Keywords
    collect: CollectConfig
    discord: DiscordConfig
    send: SendConfig
    feedback: FeedbackConfig
    remind: RemindConfig
    report: ReportConfig
    lock_wait_seconds: int


class Env(BaseModel):
    gemini_api_key: str = ""
    discord_bot_token: str = ""
    discord_channel_action: str = ""
    discord_channel_log: str = ""
    contact: str = ""


def load_config(path: Path) -> Config:
    return Config.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def load_sources(path: Path) -> list[Source]:
    sources = [Source.model_validate(x) for x in yaml.safe_load(path.read_text(encoding="utf-8"))]
    ids = [s.id for s in sources]
    dup = {i for i in ids if ids.count(i) > 1}
    if dup:
        raise ValueError(f"sources.yaml の id が重複しています: {sorted(dup)}")
    return sources


def load_env(path: Path) -> Env:
    """.env だけを読む（シェルの環境変数は使わない。古い値や別の用途の鍵を拾わないため）。"""
    values: dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            value = value.strip()
            if value[:1] in ("'", '"') and value[-1:] == value[:1]:
                value = value[1:-1]
            else:
                value = value.split(" #", 1)[0].strip()
            values[key.strip().lower()] = value
    return Env.model_validate({k: v for k, v in values.items() if k in Env.model_fields})


# ---------------------------------------------------------------- 取得データ

@dataclass
class RawItem:
    source_id: str
    url: str
    title: str
    body: str
    published_at: Optional[datetime] = None
    extra: dict = field(default_factory=dict)


# ---------------------------------------------------------------- AI出力（8.3）

class Extraction(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["lottery", "refund_all", "refund_first", "free_item", "free_game", "excluded"]
    genre: Literal["tcg", "whisky", "console", "food", "drink", "daily", "cvs", "game", "other"]
    product: str
    organizer: str
    start_at: Optional[str]
    deadline_at: Optional[str]
    conditions: str
    cost_yen: Optional[int]
    benefit_yen: Optional[int]
    apply_url: Optional[str]
    requires_subscription: bool
    actionable_now: bool
    first_come: bool  # 先着かどうか（8.6・8.7。2026-10-09 ユーザー確認で 8.3 に追加）
    confidence: float = Field(ge=0.0, le=1.0)
    exclude_reason: Optional[str]


def _nullable(t: str, **kw) -> dict:
    return {"type": [t, "null"], **kw}


# Gemini に渡すJSONスキーマ（公式ドキュメントで対応が明記された書き方：null は type の配列で表す）
EXTRACTION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": list(KINDS)},
        "genre": {"type": "string", "enum": list(GENRES) + ["other"]},
        "product": {"type": "string"},
        "organizer": {"type": "string"},
        "start_at": _nullable("string", description="ISO 8601（+09:00）。本文になければ null"),
        "deadline_at": _nullable("string", description="ISO 8601（+09:00）。本文になければ null"),
        "conditions": {"type": "string", "description": "60字以内"},
        "cost_yen": _nullable("integer"),
        "benefit_yen": _nullable("integer"),
        "apply_url": _nullable("string"),
        "requires_subscription": {"type": "boolean"},
        "actionable_now": {"type": "boolean"},
        "first_come": {"type": "boolean"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "exclude_reason": _nullable("string"),
    },
    "required": ["kind", "genre", "product", "organizer", "start_at", "deadline_at", "conditions", "cost_yen",
                 "benefit_yen", "apply_url", "requires_subscription", "actionable_now", "first_come", "confidence",
                 "exclude_reason"],
}
