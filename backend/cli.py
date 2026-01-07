from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import List

try:
    from .orchestrator import Orchestrator
    from .schemas import SchemaValidator
except ImportError:
    from backend.orchestrator import Orchestrator
    from backend.schemas import SchemaValidator


DEMO_DATASET = {
    "dataset_id": "demo",
    "version": "1.0.0",
    "metadata": {"domain": "commerce", "difficulty": "easy", "tags": ["sample"]},
    "conversations": [
        {
            "conversation_id": "conv1",
            "turns": [
                {"role": "user", "text": "I want a refund for order A1"},
                {"role": "assistant", "text": "Please share the order ID."},
                {"role": "user", "text": "Order ID is A1."}
            ]
        }
    ]
}

DEMO_GOLDEN = {
    "dataset_id": "demo",
    "version": "1.0.0",
    "entries": [
        {
            "conversation_id": "conv1",
            "turns": [
                {"turn_index": 1, "expected": {"variants": ["Please share the order ID.", "Could you provide your order ID?"]}}
            ],
            "final_outcome": {"decision": "ALLOW", "next_action": "issue_refund"},
            "constraints": {"refund_after_ship": False, "max_refund": 10}
        }
    ]
}


def cmd_init(root: Path) -> int:
    root = Path(root)
    (root / "datasets").mkdir(parents=True, exist_ok=True)
    (root / "runs").mkdir(parents=True, exist_ok=True)
    (root / "configs").mkdir(parents=True, exist_ok=True)

    ds_path = root / "datasets" / "demo.dataset.json"
    gd_path = root / "datasets" / "demo.golden.json"
    if not ds_path.exists():
        ds_path.write_text(json.dumps(DEMO_DATASET, indent=2), encoding="utf-8")
    if not gd_path.exists():
        gd_path.write_text(json.dumps(DEMO_GOLDEN, indent=2), encoding="utf-8")

    sample_run = {
        "run_id": "run-demo",
        "datasets": ["demo"],
        "models": ["gemini:gemini-2.5"],
        "metrics": ["exact"],
        "thresholds": {"semantic": 0.80},
    }
    rc_path = root / "configs" / "sample.run.json"
    if not rc_path.exists():
        rc_path.write_text(json.dumps(sample_run, indent=2), encoding="utf-8")

    print(f"Initialized workspace at {root}")
    print(f" - datasets/: demo.dataset.json, demo.golden.json")
    print(f" - configs/: sample.run.json")
    print(f" - runs/: (created)")
    return 0


def cmd_run(root: Path, file: Path) -> int:
    root = Path(root)
    cfg_path = Path(file)
    if not cfg_path.exists():
        print(f"Run config not found: {cfg_path}", file=sys.stderr)
        return 2
    try:
        run_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 2

    # Validate against run_config schema if available
    try:
        sv = SchemaValidator()
        errs = sv.validate("run_config", run_cfg)
        if errs:
            print("run_config validation errors:")
            for e in errs:
                print(" -", e)
            return 3
    except Exception:
        # If schema is unavailable, proceed
        pass

    datasets: List[str] = list(run_cfg.get("datasets") or [])
    models: List[str] = list(run_cfg.get("models") or [])
    metrics: List[str] = list(run_cfg.get("metrics") or [])
    thresholds = run_cfg.get("thresholds") or {}

    if not datasets or not models:
        print("No datasets or models specified", file=sys.stderr)
        return 2

    orch = Orchestrator(datasets_dir=root / "datasets", runs_root=root / "runs")
    run_ids: List[str] = []
    for d in datasets:
        for m in models:
            job = orch.submit(dataset_id=d, model_spec=m, config={"metrics": metrics, "thresholds": thresholds})
            # Run the job inline without requiring an event loop
            import asyncio
            asyncio.run(orch.run_job(job.job_id))
            print(f"Run completed: job={job.job_id} state={job.state} run_id={job.run_id}")
            run_ids.append(job.run_id)

    print("All runs:", ", ".join(run_ids))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="llm-eval-cli", description="LLM Eval CLI")
    p.add_argument("command", choices=["init", "run"], help="CLI command")
    p.add_argument("--root", dest="root", default=str(Path.cwd()), help="Workspace root (default: CWD)")
    p.add_argument("--file", dest="file", default=None, help="Run config file (for run)")
    return p


def main(argv: List[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.root)
    if args.command == "init":
        return cmd_init(root)
    if args.command == "run":
        if not args.file:
            print("--file is required for run", file=sys.stderr)
            return 2
        return cmd_run(root, Path(args.file))
    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
