from __future__ import annotations

import re
from typing import Any, Dict, Iterable, List, Optional


def _normalize(text: str) -> str:
    # Lowercase and collapse whitespace for robust matching
    t = text.strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def matches_any_variant(actual_text: str, variants: Iterable[str]) -> Optional[str]:
    """Return the first matching variant (case/whitespace-insensitive substring), else None."""
    norm_actual = _normalize(actual_text)
    for v in variants:
        nv = _normalize(str(v))
        if not nv:
            continue
        if nv in norm_actual or norm_actual in nv:
            return v
    return None


def score_turn(actual_text: str, expected: Dict[str, Any]) -> Dict[str, Any]:
    """Score a single turn against expected variants.

    expected should contain 'text_variants': List[str]. Any variant matching is accepted.
    Returns a dict with: passed (bool), matched_variant (str|None).
    """
    variants: List[str] = list(expected.get("text_variants", []) or [])
    matched = matches_any_variant(actual_text, variants)
    return {
        "passed": matched is not None,
        "matched_variant": matched,
    }


__all__ = ["matches_any_variant", "score_turn"]
