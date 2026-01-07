from metrics_extra import consistency, adherence, hallucination


def test_consistency():
    state = {"decision": "ALLOW", "order_id": "A1", "refund_amount": 10.0}
    out = "We deny this and refund of $5 for order A2."
    res = consistency(out, state)
    assert res["pass"] is False
    assert any("decision mismatch" in r for r in res["reasons"]) or any("refund_amount" in r for r in res["reasons"]) or any("order_id" in r for r in res["reasons"]) 


def test_adherence():
    constraints = {"refund_after_ship": False, "max_refund": 10}
    out = "We will process a refund after it's shipped of $25."
    res = adherence(out, constraints)
    assert res["pass"] is False
    assert any("max_refund" in r for r in res["reasons"]) and any("refund_after_ship" in r for r in res["reasons"]) 


def test_hallucination():
    state = {"order_id": "A1", "refund_amount": 10.0}
    history = ["User: order A1", "Assistant: refund $10"]
    out = "I see order A2 and $99 refund available."
    res = hallucination(out, state, history)
    assert res["pass"] is False
    assert any("unseen" in r for r in res["reasons"]) 
