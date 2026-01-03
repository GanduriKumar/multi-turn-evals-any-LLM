from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml

# Reuse backend utilities without requiring installation by resolving path at runtime if needed.
# Assuming this script is run from repo root or within scripts/.
try:
    from eval_server.data.loader import load_golden
    from eval_server.data.versioning import bump_version, parse_version, SemVer
except Exception:
    import sys

    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root / "backend" / "src"))
    from eval_server.data.loader import load_golden
    from eval_server.data.versioning import bump_version, parse_version, SemVer


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            items.append(json.loads(line))
    return items


def write_yaml(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def collect_approved(annotations_path: Path, raw_outputs_path: Path) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Return mapping (conversation_id, turn_id) -> approved expected payload.

    A row is considered approved if annotations contains an entry with
    matching conversation_id & turn_id and override_pass == True.
    The expected payload is built from the model output (text), but you
    can extend to structured fields if present.
    """
    annotations = json.loads(annotations_path.read_text(encoding="utf-8"))
    approved_pairs = set()
    for ann in annotations.get("annotations", []):
        if ann.get("override_pass"):
            approved_pairs.add((str(ann.get("conversation_id")), str(ann.get("turn_id"))))

    # Map from key to canonical text from raw outputs
    approved: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for row in read_jsonl(raw_outputs_path):
        key = (str(row.get("conversation_id")), str(row.get("turn_id")))
        if key in approved_pairs:
            text = row.get("response") or row.get("llm_response", {}).get("text")
            if not text:
                continue
            approved[key] = {
                "text_variants": [text],
            }
    return approved


def merge_proposals(existing_golden: Dict[str, Any], proposals: Dict[Tuple[str, str], Dict[str, Any]]) -> Dict[str, Any]:
    """Return a new golden dict with proposed updates applied in-memory (no write).

    - If an expectation exists for (conv, turn), replace its expected with proposal.
    - Otherwise, append a new expectation entry.
    """
    new_golden = dict(existing_golden)
    exp_list = list(new_golden.get("expectations", []))
    root_conv = str(new_golden.get("conversation_id", "")).strip()

    index: Dict[Tuple[str, str], int] = {}
    for i, item in enumerate(exp_list):
        item_conv = str(item.get("conversation_id", root_conv) or "").strip()
        index[(item_conv, str(item.get("turn_id")))] = i

    for (conv_id, turn_id), expected in proposals.items():
        if (conv_id, turn_id) in index:
            i = index[(conv_id, turn_id)]
            exp_list[i]["expected"] = expected
        else:
            entry: Dict[str, Any] = {"turn_id": turn_id, "expected": expected}
            if not root_conv or conv_id != root_conv:
                entry["conversation_id"] = conv_id
            exp_list.append(entry)

    new_golden["expectations"] = exp_list
    return new_golden


def propose_updates(golden_path: Path, annotations_path: Path, raw_outputs_path: Path, out_path: Path) -> Path:
    golden = load_golden(golden_path)
    proposals = collect_approved(annotations_path, raw_outputs_path)
    merged = merge_proposals(golden, proposals)

    # Save a proposal file next to golden
    out = out_path
    if out.is_dir() or str(out).endswith("/"):
        out = out / (golden_path.stem + ".proposed.yaml")
    write_yaml(out, merged)
    return out


def approve_updates(golden_path: Path, proposal_path: Path, bump: str = "patch", output_format: str = "yaml") -> Path:
    golden = load_golden(golden_path)
    proposed: Dict[str, Any]
    if proposal_path.suffix.lower() == ".json":
        proposed = json.loads(proposal_path.read_text(encoding="utf-8"))
    else:
        proposed = yaml.safe_load(proposal_path.read_text(encoding="utf-8"))

    # bump version
    cur_v = str(golden.get("version", "0.0.0"))
    new_v: SemVer = bump_version(cur_v, bump)
    proposed["version"] = str(new_v)

    # Write new versioned golden file next to original (e.g., conversation_001.golden.v1.0.1.yaml)
    stem = golden_path.stem  # e.g., conversation_001.golden
    if ".golden" in stem:
        base = stem.split(".golden")[0] + ".golden"
    else:
        base = stem
    new_name = f"{base}.v{new_v}{golden_path.suffix if output_format == 'yaml' else '.json'}"
    new_path = golden_path.with_name(new_name)

    if output_format == "json":
        write_json(new_path, proposed)
    else:
        write_yaml(new_path, proposed)

    return new_path


def cli() -> None:
    p = argparse.ArgumentParser(description="Propose and approve golden updates from human-reviewed outputs")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_prop = sub.add_parser("propose", help="Generate a proposed golden by merging approved outputs")
    p_prop.add_argument("--golden", required=True, help="Path to existing golden file (.json/.yaml)")
    p_prop.add_argument("--annotations", required=True, help="Path to annotations.json with override_pass flags")
    p_prop.add_argument("--raw-outputs", required=True, help="Path to raw_outputs.jsonl")
    p_prop.add_argument("--out", required=False, default="configs/datasets/proposals/", help="Output file or directory for proposal")

    p_appr = sub.add_parser("approve", help="Approve a proposal and write a new versioned golden file")
    p_appr.add_argument("--golden", required=True, help="Path to existing golden file to update")
    p_appr.add_argument("--proposal", required=True, help="Path to proposed golden file (.yaml/.json)")
    p_appr.add_argument("--bump", choices=["major", "minor", "patch"], default="patch")
    p_appr.add_argument("--format", choices=["yaml", "json"], default="yaml")

    args = p.parse_args()

    if args.cmd == "propose":
        out = propose_updates(Path(args.golden), Path(args.annotations), Path(args.raw_outputs), Path(args.out))
        print(str(out))
    elif args.cmd == "approve":
        new_path = approve_updates(Path(args.golden), Path(args.proposal), args.bump, args.format)
        print(str(new_path))


if __name__ == "__main__":
    cli()
