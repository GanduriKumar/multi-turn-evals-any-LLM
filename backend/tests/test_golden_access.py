from __future__ import annotations

from pathlib import Path

import yaml

from eval_server.data.golden_access import build_index_from_files, get_expected, index_golden


def test_index_and_lookup_single_file(tmp_path):
    data = {
        "version": "1.0.0",
        "conversation_id": "conv-1",
        "expectations": [
            {"turn_id": "t1", "expected": {"text_variants": ["A"]}},
            {"turn_id": "t2", "expected": {"text_variants": ["B"]}},
        ],
    }
    f = tmp_path / "golden.yaml"
    f.write_text(yaml.safe_dump(data), encoding="utf-8")

    idx = build_index_from_files([f])
    assert get_expected(idx, "conv-1", "t1")["text_variants"] == ["A"]
    assert get_expected(idx, "conv-1", "t2")["text_variants"] == ["B"]
    assert get_expected(idx, "conv-1", "t3") is None


def test_index_with_per_item_conversation_id(tmp_path):
    data = {
        "version": "1.0.0",
        "expectations": [
            {"conversation_id": "conv-A", "turn_id": "t1", "expected": {"text_variants": ["A1"]}},
            {"conversation_id": "conv-B", "turn_id": "t2", "expected": {"text_variants": ["B2"]}},
        ],
    }
    f = tmp_path / "golden.yaml"
    f.write_text(yaml.safe_dump(data), encoding="utf-8")

    idx = build_index_from_files([f])
    assert get_expected(idx, "conv-A", "t1")["text_variants"] == ["A1"]
    assert get_expected(idx, "conv-B", "t2")["text_variants"] == ["B2"]


def test_multi_file_override(tmp_path):
    a = {
        "version": "1.0.0",
        "conversation_id": "conv-1",
        "expectations": [
            {"turn_id": "t1", "expected": {"text_variants": ["A"]}},
        ],
    }
    b = {
        "version": "1.0.0",
        "conversation_id": "conv-1",
        "expectations": [
            {"turn_id": "t1", "expected": {"text_variants": ["A-OVERRIDE"]}},
        ],
    }
    fa = tmp_path / "a.yaml"
    fb = tmp_path / "b.yaml"
    fa.write_text(yaml.safe_dump(a), encoding="utf-8")
    fb.write_text(yaml.safe_dump(b), encoding="utf-8")

    idx = build_index_from_files([fa, fb])
    assert get_expected(idx, "conv-1", "t1")["text_variants"] == ["A-OVERRIDE"]
