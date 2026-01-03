from __future__ import annotations

import json
from pathlib import Path

from eval_server.headless_engine import run_headless


def test_headless_engine_writes_raw_outputs(tmp_path: Path):
    repo = Path(__file__).resolve().parents[2]
    sample = repo / "configs" / "runs" / "sample_run_config.yaml"

    out_dir = tmp_path / "out"
    path = run_headless(sample, output_dir=out_dir)

    raw_path = path / "raw_outputs.jsonl"
    assert raw_path.exists()

    lines = raw_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 1
    row = json.loads(lines[0])
    assert "conversation_id" in row and "turn_id" in row
    assert "llm_request" in row and "llm_response" in row
