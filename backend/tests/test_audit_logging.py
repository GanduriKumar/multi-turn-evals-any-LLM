from __future__ import annotations

import json
from pathlib import Path

import yaml

from eval_server.headless_engine import run_headless


def _write_run_config(tmp_path: Path, repo_root: Path) -> Path:
    conv = repo_root / "configs" / "datasets" / "examples" / "conversation_001.json"
    gold = repo_root / "configs" / "datasets" / "examples" / "conversation_001.golden.yaml"
    rc = {
        "version": "1.0.0",
        "datasets": [
            {
                "id": "conv001",
                "conversation": conv.as_posix(),
                "golden": gold.as_posix(),
            }
        ],
        "models": [
            {
                "name": "dummy",
                "provider": "dummy",
                "model": "dummy",
            }
        ],
    }
    path = tmp_path / "run.yaml"
    path.write_text(yaml.safe_dump(rc), encoding="utf-8")
    return path


def test_audit_log_created_for_run(tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    cfg_path = _write_run_config(tmp_path, repo_root)
    log_path = tmp_path / "audit.jsonl"
    out_dir = tmp_path / "artifacts"

    run_headless(cfg_path, output_dir=out_dir, audit_actor="tester", audit_log_path=log_path)

    assert log_path.exists()
    lines = [json.loads(line) for line in log_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    actions = {entry.get("action") for entry in lines}
    assert {"evaluation_started", "evaluation_completed"}.issubset(actions)

    for entry in lines:
        assert entry.get("actor") == "tester"
        assert entry.get("run_id") and str(entry.get("run_id")).startswith("run_")
        assert entry.get("config_fingerprint") is not None
        assert entry.get("timestamp")

    # Ensure logs were written to the requested location, not default
    assert log_path.parent == tmp_path
