from __future__ import annotations

from pathlib import Path

import yaml

from eval_server.evaluation.final_outcome import evaluate_final_outcome


def test_final_outcome_success_and_failure_cases(tmp_path):
    golden = {
        "version": "1.0.0",
        "conversation_id": "conv-1",
        "expectations": [
            {"turn_id": "t1", "expected": {"text_variants": ["foo"]}},
        ],
        "final_outcome": {
            "success": True,
            "must_include": ["completed", "order"],
            "must_not_include": ["failed"],
        },
    }

    # Successful transcript
    ok = evaluate_final_outcome("The order was COMPLETED successfully.", golden)
    assert ok["checked"] is True
    assert ok["success"] is True

    # Failure due to missing term
    bad = evaluate_final_outcome("The process was done.", golden)
    assert bad["checked"] is True
    assert bad["success"] is False
    assert any("Missing" in r for r in bad["reasons"])  # informative

    # Failure due to forbidden term
    bad2 = evaluate_final_outcome("The order failed due to error.", golden)
    assert bad2["checked"] is True
    assert bad2["success"] is False
    assert any("forbidden" in r.lower() for r in bad2["reasons"])  # informative


def test_final_outcome_conversation_mismatch_skips():
    golden = {
        "version": "1.0.0",
        "final_outcome": {"conversation_id": "conv-ABC", "success": True}
    }
    out = evaluate_final_outcome("anything", golden, conversation_id="conv-XYZ")
    # Not applicable; no check performed
    assert out["checked"] is False
    assert out["success"] is None
