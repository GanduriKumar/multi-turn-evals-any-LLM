import json
import os
from pathlib import Path

from backend import cli


def test_cli_init(tmp_path: Path, monkeypatch):
    code = cli.main(["init", "--root", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "datasets" / "demo.dataset.json").exists()
    assert (tmp_path / "datasets" / "demo.golden.json").exists()
    assert (tmp_path / "configs" / "sample.run.json").exists()


def test_cli_run_with_sample(tmp_path: Path, monkeypatch):
    # initialize
    assert cli.main(["init", "--root", str(tmp_path)]) == 0
    # Modify sample run to use gemini (disabled) but should still succeed (runs with provider returning disabled)
    rc = json.loads((tmp_path / "configs" / "sample.run.json").read_text(encoding="utf-8"))
    rc["models"] = ["gemini:gemini-2.5"]
    (tmp_path / "configs" / "sample.run.json").write_text(json.dumps(rc), encoding="utf-8")

    code = cli.main(["run", "--root", str(tmp_path), "--file", str(tmp_path / "configs" / "sample.run.json")])
    assert code == 0
    # should have created a runs folder with at least one subdir
    runs = list((tmp_path / "runs").glob("*/"))
    assert runs, "expected at least one run folder created"
