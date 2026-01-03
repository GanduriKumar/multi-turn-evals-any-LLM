from __future__ import annotations

from eval_server.evaluation.scoring import matches_any_variant, score_turn


def test_matches_any_variant():
    actual = "Employees have 25 DAYS of leave each year."
    variants = [
        "leave policy allows 25 days",
        "employees have 25 days of leave",
        "25 days annual leave"
    ]
    m = matches_any_variant(actual, variants)
    assert m is not None


def test_score_turn_accepts_any_variant():
    expected = {
        "text_variants": [
            "policy allows 25 days",
            "25 days annual leave"
        ]
    }
    out = score_turn("The policy allows 25 days off.", expected)
    assert out["passed"] is True
    assert out["matched_variant"]
