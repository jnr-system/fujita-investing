"""8.6 スコアと 8.7 緊急の判定。"""
from datetime import timedelta

from otoku.db import Candidate
from otoku.pipeline.score import is_urgent, score

from .conftest import NOW


def cand(kind="free_item", genre="food", deadline=None, first_come=False, benefit=None, **kw) -> Candidate:
    return Candidate(id=kw.get("id", 1), source_id="s", title="t", url="https://example.com/a", body="", scope=None,
                     kind=kind, genre=genre, product="p", organizer="o", start_at=None, deadline_at=deadline,
                     conditions="c", cost_yen=None, benefit_yen=benefit, apply_url=None, first_come=first_come)


def test_base_and_genre(cfg):
    w = cfg.weights
    assert score(cand("refund_first", "food"), NOW, w, 0) == 60
    assert score(cand("refund_all", "drink"), NOW, w, 0) == 55
    assert score(cand("free_item", "cvs"), NOW, w, 0) == 50
    assert score(cand("free_game", "game"), NOW, w, 0) == 45
    assert score(cand("lottery", "tcg"), NOW, w, 0) == 65
    assert score(cand("lottery", "whisky"), NOW, w, 0) == 65
    assert score(cand("lottery", "console"), NOW, w, 0) == 60


def test_urgency_by_deadline(cfg):
    w = cfg.weights
    assert score(cand(deadline=NOW + timedelta(hours=23)), NOW, w, 0) == 65
    assert score(cand(deadline=NOW + timedelta(hours=24)), NOW, w, 0) == 65
    assert score(cand(deadline=NOW + timedelta(hours=50)), NOW, w, 0) == 55
    assert score(cand(deadline=NOW + timedelta(hours=100)), NOW, w, 0) == 50


def test_first_come_takes_the_larger_not_the_sum(cfg):
    w = cfg.weights
    assert score(cand(first_come=True), NOW, w, 0) == 65                                   # 先着は常に +15
    assert score(cand(first_come=True, deadline=NOW + timedelta(hours=10)), NOW, w, 0) == 65  # +30 にはしない


def test_benefit_bonus_and_source_weight(cfg):
    w = cfg.weights
    assert score(cand(benefit=999), NOW, w, 0) == 50
    assert score(cand(benefit=1000), NOW, w, 0) == 55
    assert score(cand(benefit=5000), NOW, w, 0) == 60
    assert score(cand(), NOW, w, 5) == 55
    assert score(cand(), NOW, w, 30) == 60   # 情報源の重みは -10〜+10 に収める
    assert score(cand(), NOW, w, -30) == 40


def test_urgent(cfg):
    h = cfg.send.urgent_within_hours
    assert is_urgent(cand(first_come=True), NOW, h)
    assert is_urgent(cand(deadline=NOW + timedelta(hours=23)), NOW, h)
    assert not is_urgent(cand(deadline=NOW + timedelta(hours=25)), NOW, h)
    assert not is_urgent(cand(), NOW, h)
