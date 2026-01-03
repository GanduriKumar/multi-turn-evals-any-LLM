from __future__ import annotations

from eval_server.scoring.conversation_scoring import aggregate_conversation_scores


def test_conversation_mean_aggregation():
    turn_scores = {"t1": 0.8, "t2": 0.6, "t3": 1.0}
    score, passed = aggregate_conversation_scores(turn_scores, method="mean", threshold=0.7)
    assert abs(score - (0.8 + 0.6 + 1.0) / 3) < 1e-9
    assert passed is True


def test_conversation_min_aggregation():
    turn_scores = {"t1": 0.8, "t2": 0.4, "t3": 1.0}
    score, passed = aggregate_conversation_scores(turn_scores, method="min", threshold=0.5)
    assert score == 0.4
    assert passed is False


def test_conversation_weighted_aggregation():
    turn_scores = {"t1": 0.9, "t2": 0.6, "t3": 1.0}
    weights = {"t1": 2.0, "t2": 0.5}
    score, passed = aggregate_conversation_scores(turn_scores, method="weighted", turn_weights=weights, threshold=0.85)
    assert abs(score - (3.1/3.5)) < 1e-9
    assert passed is True
