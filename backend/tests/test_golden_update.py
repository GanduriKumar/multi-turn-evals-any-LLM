from __future__ import annotations

from pathlib import Path
import json
import yaml

from eval_server.data.loader import load_golden
from eval_server.data.versioning import parse_version


def _make_sample_golden(tmp_path: Path) -> Path:
    golden = {
        "version": "1.0.0",
        "conversation_id": "conv-001",
        "expectations": [
            {"turn_id": "t3", "expected": {"text_variants": ["old text"]}},
        ],
    }
    p = tmp_path / "conversation_001.golden.yaml"
    p.write_text(yaml.safe_dump(golden), encoding="utf-8")
    return p


def _make_annotations(tmp_path: Path) -> Path:
    anns = {
        "annotations": [
            {
                "dataset_id": "conv001",
                "conversation_id": "conv-001",
                "model_name": "dummy-1",
                "turn_id": "t3",
                "notes": "Approved",
                "override_pass": True,
                "override_score": 1.0,
            }
        ]
    }
    p = tmp_path / "annotations.json"
    p.write_text(json.dumps(anns), encoding="utf-8")
    return p


def _make_raw_outputs(tmp_path: Path) -> Path:
    rows = [
        {
            "dataset_id": "conv001",
            "conversation_id": "conv-001",
            "turn_id": "t3",
            "model_name": "dummy-1",
            "response": "New approved golden text",
        }
    ]
    p = tmp_path / "raw_outputs.jsonl"
    p.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")
    return p


def test_propose_and_approve_workflow(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]

    golden_path = _make_sample_golden(tmp_path)
    annotations_path = _make_annotations(tmp_path)
    raw_outputs_path = _make_raw_outputs(tmp_path)

    # Import script functions
    import sys
    sys.path.insert(0, str(repo_root))
    from scripts.update_golden import propose_updates, approve_updates

    # Propose updates
    proposal_path = tmp_path / "proposal.yaml"
    out = propose_updates(golden_path, annotations_path, raw_outputs_path, proposal_path)
    assert out.exists()

    proposed = yaml.safe_load(out.read_text(encoding="utf-8"))
    # Ensure the text variant got updated
    exp = proposed["expectations"][0]["expected"]["text_variants"][0]
    assert exp == "New approved golden text"

    # Approve with patch bump
    new_path = approve_updates(golden_path, out, bump="patch", output_format="yaml")
    assert new_path.exists()

    approved = load_golden(new_path)
    # version bumped
    assert str(approved["version"]) == "1.0.1"
    # content updated
    exp2 = approved["expectations"][0]["expected"]["text_variants"][0]
    assert exp2 == "New approved golden text"
