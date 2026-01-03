from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .loader import load_golden


GoldenDict = Mapping[str, Any]


def _normalize_key(conversation_id: str, turn_id: str) -> Tuple[str, str]:
    return (str(conversation_id), str(turn_id))


def index_golden(golden: GoldenDict) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Create an index mapping (conversation_id, turn_id) -> expected payload.

    If an item includes its own conversation_id, it is used; else the root's conversation_id is used.
    """
    root_conv = str(golden.get("conversation_id", "")).strip()
    idx: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for item in golden.get("expectations", []) or []:
        item_conv = str(item.get("conversation_id", root_conv) or "").strip()
        turn_id = str(item.get("turn_id"))
        exp = item.get("expected")
        if not item_conv or not turn_id or not isinstance(exp, dict):
            # skip malformed entries silently; schema validation should have caught this earlier
            continue
        idx[_normalize_key(item_conv, turn_id)] = exp
    return idx


def build_index_from_files(paths: Iterable[str | Path]) -> Dict[Tuple[str, str], Dict[str, Any]]:
    """Load multiple golden files and build a combined index.

    Later files override earlier ones for identical keys.
    """
    index: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for p in paths:
        g = load_golden(p)
        index.update(index_golden(g))
    return index


def get_expected(index: Dict[Tuple[str, str], Dict[str, Any]], conversation_id: str, turn_id: str) -> Optional[Dict[str, Any]]:
    return index.get(_normalize_key(conversation_id, turn_id))


__all__ = [
    "index_golden",
    "build_index_from_files",
    "get_expected",
]
