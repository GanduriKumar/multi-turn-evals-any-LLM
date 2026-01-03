from __future__ import annotations

from typing import Mapping, Optional, Tuple

from ..evaluation.weights import aggregate_conversation as weighted_aggregate


def aggregate_conversation_scores(
    turn_scores: Mapping[str, float],
    *,
    method: str = "mean",
    turn_weights: Optional[Mapping[str, float]] = None,
    threshold: Optional[float] = None,
) -> Tuple[float, bool]:
    """Aggregate per-turn scores into a conversation score and pass/fail.

    - method: "mean" | "min" | "weighted"
    - turn_weights: used when method is "weighted" (defaults to 1.0 for missing turns)
    - threshold: pass if aggregated score >= threshold (defaults to 0.5 if None)
    """
    if not turn_scores:
        return 0.0, False

    m = (method or "").strip().lower()
    vals = list(float(v) for v in turn_scores.values())

    if m == "min":
        score = min(vals)
    elif m in ("weighted", "weighted_mean"):
        score = float(weighted_aggregate(turn_scores, turn_weights))
    else:  # mean
        score = sum(vals) / len(vals)

    thr = 0.5 if threshold is None else float(threshold)
    passed = score >= thr
    return score, passed


__all__ = ["aggregate_conversation_scores"]
