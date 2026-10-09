"""8.3 AI構造化（Gemini は呼ばずに偽物で置き換える）。"""
import pytest

from otoku.models import EXTRACTION_SCHEMA, Extraction, RawItem
from otoku.pipeline.extract import AIUnavailable, Extractor, build_input

from .conftest import NOW, ai_fixture, make_source


def test_input_has_title_body_head_and_jst_time(cfg):
    raw = RawItem(source_id="s", url="https://example.com/a", title="タイトル", body="あ" * 5000)
    text = build_input(raw, make_source(), NOW, cfg.gemini.max_body_chars)
    assert "タイトル: タイトル" in text
    assert "取得日時（JST）: 2026-10-09T12:00+09:00" in text
    assert text.count("あ") == cfg.gemini.max_body_chars == 4000


def test_retry_once_on_invalid_then_give_up(cfg):
    answers = [ai_fixture("invalid_not_json.txt"), ai_fixture("refund_first_ok")]
    ex = Extractor(cfg.gemini, "system", call=lambda s, u: answers.pop(0))
    raw = RawItem(source_id="s", url="https://example.com/a", title="t", body="b")
    assert ex.extract(raw, make_source(), NOW).kind == "refund_first"
    assert ex.calls == 2

    ex = Extractor(cfg.gemini, "system", call=lambda s, u: ai_fixture("invalid_missing_field"))
    assert ex.extract(raw, make_source(), NOW) is None  # → dropped（AI応答不正）
    assert ex.calls == 1 + cfg.gemini.retry_on_invalid


def test_unavailable_propagates(cfg):
    def boom(s, u):
        raise AIUnavailable("quota")
    ex = Extractor(cfg.gemini, "system", call=boom)
    with pytest.raises(AIUnavailable):
        ex.extract(RawItem(source_id="s", url="u", title="t", body="b"), make_source(), NOW)


def test_schema_matches_model():
    assert set(EXTRACTION_SCHEMA["properties"]) == set(Extraction.model_fields)
    assert set(EXTRACTION_SCHEMA["required"]) == set(Extraction.model_fields)


def test_gemini_call_uses_json_schema_and_temperature(cfg, monkeypatch):
    """SDK の呼び方（interactions.create の引数）を、通信せずに確かめる。"""
    seen = {}

    class FakeInteraction:
        output_text = ai_fixture("refund_first_ok")

    class FakeInteractions:
        def create(self, **kw):
            seen.update(kw)
            return FakeInteraction()

    class FakeClient:
        def __init__(self, api_key):
            seen["api_key"] = api_key
            self.interactions = FakeInteractions()

    import google.genai
    monkeypatch.setattr(google.genai, "Client", FakeClient)
    ex = Extractor(cfg.gemini, "system prompt", api_key="k")
    x = ex.extract(RawItem(source_id="s", url="u", title="t", body="b"), make_source(), NOW)
    assert x.kind == "refund_first"
    assert seen["model"] == cfg.gemini.model
    assert seen["generation_config"] == {"temperature": 0}
    assert seen["response_format"]["mime_type"] == "application/json"
    assert seen["response_format"]["schema"] is EXTRACTION_SCHEMA
    assert seen["store"] is False and seen["system_instruction"] == "system prompt"
