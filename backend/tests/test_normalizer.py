from __future__ import annotations

from eval_server.scoring.normalizer import (
    canonicalize_text,
    extract_tool_results,
    extract_structured,
    normalize_turn_output,
)


def test_canonicalize_text():
    assert canonicalize_text("  HeLLo  \n World ") == "hello world"


def test_extract_tool_results():
    ctx = [
        "SYSTEM: x",
        "TOOL: doc_search args={'query': 'policy'} result={'doc_id': 7}",
        "TOOL: calc args={'expr': '2+2'} result=4",
    ]
    tools = extract_tool_results(ctx)
    assert len(tools) == 2
    names = [t["tool_name"] for t in tools]
    assert names == ["doc_search", "calc"]
    assert tools[0]["arguments"]["query"] == "policy"
    assert tools[0]["result"]["doc_id"] == 7
    assert tools[1]["result"] == 4


def test_extract_structured_and_normalize_record():
    raw_text = "Decision: Allow\nReason Code: OK-200\nNext Action=proceed. Also 25 days."
    context = [
        "TOOL: doc_search args={'query': 'policy'} result={'doc_id': 42}",
    ]
    rec = normalize_turn_output(raw_text, context, metadata={"model": "dummy"})
    assert rec["text"].startswith("decision: allow")
    s = rec["structured"]
    assert s["decision"] == "ALLOW"
    assert s["reason_code"].lower() == "ok-200"
    assert s["next_action"] == "proceed"
    assert s["days_allowed"] == 25

    tools = rec["tools"]
    assert tools and tools[0]["result"]["doc_id"] == 42
