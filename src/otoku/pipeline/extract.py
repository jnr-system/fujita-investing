"""8.3 AI構造化（Gemini、JSONスキーマ指定、温度0）。

SDK は google-genai。2026-10-09 時点の公式ドキュメントが案内している interactions を使う。
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Callable, Optional

from pydantic import ValidationError

from ..models import EXTRACTION_SCHEMA, JST, Extraction, GeminiConfig, RawItem, Source


class AIUnavailable(Exception):
    """AIを呼べなかった（通信・認証・上限など）。この回はAI判定をやめ、次回に回す。"""


def build_input(raw: RawItem, source: Source, fetched_at: datetime, max_body_chars: int) -> str:
    """入力はタイトル＋本文の先頭 max_body_chars 文字＋取得日時（JST）。"""
    return "\n".join([
        "# 情報",
        f"情報源ID: {source.id}",
        f"情報源のジャンルの手がかり: {', '.join(source.genre_hint) or 'なし'}",
        f"取得日時（JST）: {fetched_at.astimezone(JST).isoformat(timespec='minutes')}",
        f"URL: {raw.url}",
        f"タイトル: {raw.title}",
        "本文:",
        raw.body[:max_body_chars],
    ])


def parse_response(text: str) -> Optional[Extraction]:
    try:
        return Extraction.model_validate(json.loads(text))
    except (json.JSONDecodeError, ValidationError, TypeError):
        return None


class Extractor:
    def __init__(self, cfg: GeminiConfig, system_prompt: str, *, api_key: str = "",
                 call: Optional[Callable[[str, str], str]] = None):
        self.cfg = cfg
        self.system_prompt = system_prompt
        self._api_key = api_key
        self._client = None
        self._call = call or self._call_gemini
        self.calls = 0

    def _call_gemini(self, system: str, user: str) -> str:
        from google import genai  # SDKは実際に呼ぶときだけ読む（テストでは使わない）

        if self._client is None:
            self._client = genai.Client(api_key=self._api_key)
        try:
            interaction = self._client.interactions.create(
                model=self.cfg.model,
                system_instruction=system,
                input=user,
                generation_config={"temperature": self.cfg.temperature},
                response_format={"type": "text", "mime_type": "application/json", "schema": EXTRACTION_SCHEMA},
                store=False,
                timeout=self.cfg.timeout_seconds,
            )
        except Exception as e:  # SDKの例外は種類が多いので、まとめて「呼べなかった」とする
            raise AIUnavailable(f"{type(e).__name__}: {e}") from e
        return interaction.output_text or ""

    def extract(self, raw: RawItem, source: Source, fetched_at: datetime) -> Optional[Extraction]:
        """スキーマに合わない応答は retry_on_invalid 回まで再試行し、それでもだめなら None（AI応答不正）。"""
        user = build_input(raw, source, fetched_at, self.cfg.max_body_chars)
        for _ in range(1 + self.cfg.retry_on_invalid):
            self.calls += 1
            result = parse_response(self._call(self.system_prompt, user))
            if result is not None:
                return result
        return None
