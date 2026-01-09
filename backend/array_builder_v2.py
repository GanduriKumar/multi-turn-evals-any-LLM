from __future__ import annotations
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .commerce_taxonomy import load_commerce_config
from .risk_sampler import sample_for_behavior, compute_risk_tier
from .policy_facts import load_policy_and_facts
from .convgen_v2 import u1_text, u2_text
from .canonical_a2_lib import compose_canonical_a2


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_combined_array(
    *,
    domains: Optional[Iterable[str]] = None,
    behaviors: Optional[Iterable[str]] = None,
    version: str = "1.0.0",
    seed: int = 42,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """Build a single JSON-array style dataset from the risk-weighted sampler.

    Each item contains fields per Prompt 14 schema.
    Returns (items, counts_by_risk).
    """
    cfg = load_commerce_config()
    tax = cfg["taxonomy"]
    all_behaviors = list(behaviors) if behaviors is not None else list(tax.get("behaviors", []))
    dom_filter = set(domains) if domains is not None else None

    items: List[Dict[str, Any]] = []
    counts = {"high": 0, "medium": 0, "low": 0}

    for b in all_behaviors:
        manifest = sample_for_behavior(cfg, b)
        for sc in manifest.get("scenarios", []) or []:
            d = sc.get("domain")
            axes = sc.get("axes") or {}
            if dom_filter and d not in dom_filter:
                continue
            # Inputs
            policy_text, facts_text = load_policy_and_facts(d, axes, seed)
            # Messages
            u1 = u1_text(d, axes)
            u2 = u2_text(d, axes)
            # Canonical A2
            a2 = compose_canonical_a2(b, policy_text, facts_text, axes)
            # Risk tier
            r = compute_risk_tier(cfg, d, b, axes)
            counts[r] = counts.get(r, 0) + 1
            # scenario_id: reuse scenario id from sampler if present
            scenario_id = sc.get("id") or f"{d}.{b}.{axes}"
            items.append({
                "scenario_id": scenario_id,
                "version": version,
                "domain": d,
                "behavior": b,
                "risk_tier": r,
                "axes": axes,
                "policy_text": policy_text,
                "facts_text": facts_text,
                "messages": {"u1": u1, "u2": u2},
                "expected": {"outcome": "Allowed", "a2_canonical": a2},
                "metadata": {"seed": seed, "created_ts": _now_iso()},
            })
    return items, counts
