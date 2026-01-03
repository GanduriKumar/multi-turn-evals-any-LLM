from __future__ import annotations

from eval_server.scoring.normalizer import normalize_turn_output
from eval_server.scoring.turn_scoring import score_turn_canonical


def test_turn_scoring_basic_correctness_pass():
    raw = "Employees have 25 days of leave per year."
    ctx = []
    canonical = normalize_turn_output(raw, ctx)
    expected = {"text_variants": ["25 days of leave", "employees have 25 days"]}

    scores, passed = score_turn_canonical(canonical, expected, thresholds={"correctness": 0.5, "structured": 0.0, "constraints": 0.0})
    assert passed is True
    assert scores["correctness"] == 1.0


def test_turn_scoring_structured_partial_credit():
    raw = "Decision: Allow\nReason Code: OK-200\nNext Action=proceed"
    ctx = []
    canonical = normalize_turn_output(raw, ctx)
    expected = {"structured": {"decision": "ALLOW", "reason_code": "OK-200", "next_action": "proceed"}}

    scores, passed = score_turn_canonical(canonical, expected, thresholds={"correctness": 1.0, "structured": 0.9, "constraints": 0.0})
    # All keys match, so structured should be 1.0, pass even with high threshold
    assert scores["structured"] == 1.0
    assert passed is True


def test_turn_scoring_fail_on_threshold():
    raw = "No match here"
    ctx = []
    canonical = normalize_turn_output(raw, ctx)
    expected = {"text_variants": ["something else"]}

    scores, passed = score_turn_canonical(canonical, expected, thresholds={"correctness": 1.0})
    assert scores["correctness"] == 0.0
    assert passed is False
