from conversation_scoring import check_final_outcome, aggregate_conversation


def test_check_final_outcome_pass():
    state = {"decision": "ALLOW", "refund_amount": 10.0, "policy_flags": ["after_shipment"]}
    expected = {"decision": "ALLOW", "refund_amount": 10.0, "policy_flags": ["after_shipment"]}
    res = check_final_outcome(state, expected)
    assert res["pass"] is True


def test_aggregate_outcome_first_with_violation():
    per_turn = [
        {"turn_index": 1, "metrics": {"exact": {"pass": True}}},
        {"turn_index": 2, "metrics": {"semantic": {"pass": True}, "adherence": {"pass": False}}}
    ]
    final_state = {"decision": "ALLOW"}
    expected = {"decision": "ALLOW"}
    agg = aggregate_conversation(per_turn, final_state, expected)
    assert agg["conversation_pass"] is False
    assert agg["high_severity_violation"] is True


def test_aggregate_weighted_rate():
    per_turn = [
        {"turn_index": 1, "metrics": {"exact": {"pass": True}}},
        {"turn_index": 2, "metrics": {"semantic": {"pass": False}}}
    ]
    final_state = {"decision": "ALLOW"}
    expected = {"decision": "ALLOW"}
    agg = aggregate_conversation(per_turn, final_state, expected, weights=[0.8, 0.2])
    assert agg["weighted_pass_rate"] == 0.8
