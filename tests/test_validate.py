"""8.4 検証と 15章の除外条件。AIの応答は tests/fixtures/ai の保存データ。"""
from datetime import timedelta

import pytest

from otoku.models import RawItem
from otoku.pipeline.dedupe import url_hash
from otoku.pipeline.extract import parse_response
from otoku.pipeline.validate import promote_waiting, validate

from .conftest import NOW, ai_fixture


def run(name, cfg):
    x = parse_response(ai_fixture(name))
    assert x is not None, name
    return validate(x, NOW, min_confidence=cfg.min_confidence, genres_enabled=cfg.genres_enabled)


@pytest.mark.parametrize("name,expected", [
    ("refund_first_ok", ("candidate", "B")),
    ("lottery_tcg_ok", ("candidate", "A")),
    ("free_game_ok", ("candidate", "B")),
])
def test_candidates(cfg, name, expected):
    v = run(name, cfg)
    assert (v.status, v.scope) == expected


@pytest.mark.parametrize("name,reason_part", [
    ("excluded_lottery_refund", "抽選で全額返金"),     # 抽選で返金
    ("excluded_refund_guarantee", "返金保証"),         # 返金保証
    ("subscription", "継続購入・定期契約"),             # 定期購入条件
    ("closed", "締切が過去"),                          # 受付終了
    ("preview_no_date", "今は応募・受取できない"),      # 予告のみ
    ("low_confidence", "確信度不足"),                   # confidence が閾値未満
    ("other_genre", "スコープ外のジャンル"),
    ("lottery_food", "スコープ外: 抽選だがジャンルが food"),  # 懸賞
])
def test_each_exclusion_is_dropped(cfg, name, reason_part):
    v = run(name, cfg)
    assert v.status == "dropped"
    assert reason_part in v.reason


def test_confidence_threshold_boundary(cfg):
    x = parse_response(ai_fixture("refund_first_ok"))
    x.confidence = cfg.min_confidence
    assert validate(x, NOW, min_confidence=cfg.min_confidence, genres_enabled=cfg.genres_enabled).status == "candidate"
    x.confidence = cfg.min_confidence - 0.01
    assert validate(x, NOW, min_confidence=cfg.min_confidence, genres_enabled=cfg.genres_enabled).status == "dropped"


def test_preview_with_future_start_waits(cfg):
    v = run("preview_future", cfg)
    assert v.status == "waiting"
    assert v.start_at.isoformat() == "2026-10-15T10:00:00+09:00"


def test_date_only_deadline_means_end_of_day(cfg):
    v = run("free_game_ok", cfg)  # deadline_at: "2026-10-15"
    assert v.deadline_at.isoformat() == "2026-10-15T23:59:00+09:00"


def test_unreadable_date_is_dropped(cfg):
    x = parse_response(ai_fixture("refund_first_ok"))
    x.deadline_at = "10月20日まで"
    v = validate(x, NOW, min_confidence=cfg.min_confidence, genres_enabled=cfg.genres_enabled)
    assert v.status == "dropped" and "日時を読めない" in v.reason


def test_invalid_ai_responses_are_rejected():
    assert parse_response(ai_fixture("invalid_not_json.txt")) is None
    assert parse_response(ai_fixture("invalid_missing_field")) is None


def test_waiting_is_reevaluated_at_start_time(cfg, store):
    v = run("preview_future", cfg)
    raw = RawItem(source_id="s", url="https://example.com/w", title="限定ウイスキー 抽選販売", body="")
    rid = store.add_raw(raw, url_hash(raw.url), "h", NOW)
    store.add_item(rid, scope=v.scope, kind="lottery", status=v.status, created_at=NOW, start_at=v.start_at,
                   deadline_at=v.deadline_at)
    store.commit()
    assert promote_waiting(store, NOW) == []                       # まだ開始前
    after_start = v.start_at + timedelta(minutes=1)
    assert promote_waiting(store, after_start) == [("candidate", raw.title, "s")]
    assert store.waiting_items() == []


def test_waiting_past_deadline_expires(cfg, store):
    v = run("preview_future", cfg)
    raw = RawItem(source_id="s", url="https://example.com/w2", title="t", body="")
    rid = store.add_raw(raw, url_hash(raw.url), "h", NOW)
    store.add_item(rid, scope="A", kind="lottery", status="waiting", created_at=NOW, start_at=v.start_at,
                   deadline_at=v.deadline_at)
    store.commit()
    assert promote_waiting(store, v.deadline_at + timedelta(hours=1)) == [("expired", "t", "s")]
