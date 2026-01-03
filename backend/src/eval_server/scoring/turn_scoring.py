from __future__ import annotations

from typing import Any, Dict, Mapping, Optional, Tuple

from ..evaluation.scoring import matches_any_variant
from ..evaluation.structured import compare_structured
from .normalizer import canonicalize_text


def _metric_correctness(actual_text: str, expected_variants: Mapping[str, Any]) -> float:
    variants = expected_variants.get("text_variants") or []
    if not variants:
        return 0.0
    return 1.0 if matches_any_variant(actual_text, variants) else 0.0


def _metric_structured(actual_struct: Mapping[str, Any], expected_struct: Mapping[str, Any]) -> float:
    if not expected_struct:
        return 0.0
    passed, details = compare_structured(actual_struct, expected_struct)
    if passed:
        return 1.0
    # Partial credit: fraction of keys matched
    total = len(expected_struct)
    mismatches = details.get("mismatches", {})
    matched = total - len(mismatches)
    return matched / total if total > 0 else 0.0


def _metric_constraints(_: Mapping[str, Any], expected: Mapping[str, Any]) -> float:
    # Placeholder: when constraints evaluated elsewhere, here assume pass if no constraints specified
    constraints = expected.get("constraints") or []
    return 1.0 if not constraints else 0.0


def score_turn_canonical(
    canonical: Mapping[str, Any],
    expected: Mapping[str, Any],
    *,
    thresholds: Optional[Mapping[str, float]] = None,
) -> Tuple[Dict[str, float], bool]:
    """Score a canonical record against expected golden for one turn.

    Returns (scores_by_metric, passed_flag) where passed_flag derives from thresholds per metric (default 0.5).
    Metrics implemented: correctness (text_variants), structured (expected.structured), constraints (presence only for now).
    """
    scores: Dict[str, float] = {}
    # Text correctness if expected variants provided
    if expected.get("text_variants"):
        scores["correctness"] = _metric_correctness(canonicalize_text(canonical.get("raw_text", "")), expected)
    # Structured if expected structured provided
    if expected.get("structured"):
        scores["structured"] = _metric_structured(canonical.get("structured", {}), expected.get("structured", {}))
    # Constraints if any specified
    if expected.get("constraints"):
        scores["constraints"] = _metric_constraints(canonical, expected)

    # Determine pass/fail using thresholds per metric
    thr_def = 0.5
    passed = True
    for m, val in scores.items():
        thr = (thresholds or {}).get(m, thr_def)
        if val < thr:
            passed = False
    return scores, passed


__all__ = ["score_turn_canonical"]
