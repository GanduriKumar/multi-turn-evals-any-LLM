from __future__ import annotations

import ast
import json
import re
from typing import Any, Dict, List, Mapping, Optional


def canonicalize_text(text: str) -> str:
    """Normalize text by stripping, lowercasing, and collapsing whitespace."""
    t = (text or "").strip().lower()
    t = re.sub(r"\s+", " ", t)
    return t


def _try_parse_literal(value: str) -> Any:
    try:
        return ast.literal_eval(value)
    except Exception:
        # try json if it looks like json
        try:
            return json.loads(value)
        except Exception:
            return value


def extract_tool_results(context_lines: List[str]) -> List[Dict[str, Any]]:
    """Parse TOOL: lines from context into structured tool results.

    Expected format from TurnRunner: "TOOL: <name> args=<...> result=<...>"
    where args/result are Python-literal-like or JSON-like strings.
    """
    tools: List[Dict[str, Any]] = []
    for line in context_lines:
        if not line.startswith("TOOL:"):
            continue
        # Example: TOOL: doc_search args={'query': 'q'} result={'doc_id': 1}
        # Split by spaces but keep args/result segments
        try:
            after = line[len("TOOL:"):].strip()
            # name up to first space
            parts = after.split(" ", 1)
            name = parts[0].strip()
            rest = parts[1] if len(parts) > 1 else ""
            # find args=... and result=...
            args_val: Any = None
            res_val: Any = None
            m_args = re.search(r"args=(.*?)(?:\s+result=|$)", rest)
            if m_args:
                args_val = _try_parse_literal(m_args.group(1).strip())
            m_res = re.search(r"result=(.*)$", rest)
            if m_res:
                res_val = _try_parse_literal(m_res.group(1).strip())
            tools.append({"tool_name": name, "arguments": args_val, "result": res_val})
        except Exception:
            # fallback: keep raw
            tools.append({"raw": line})
    return tools


_KV_PATTERNS = [
    # Capture value up to end of line; later trim punctuation for next_action
    re.compile(r"(?im)^(decision)\s*[:=]\s*([^\r\n]+)"),
    re.compile(r"(?im)^(reason[_ ]?code)\s*[:=]\s*([^\r\n]+)"),
    re.compile(r"(?im)^(next[_ ]?action)\s*[:=]\s*([^\r\n]+)"),
]


def extract_structured(text: str) -> Dict[str, Any]:
    """Extract structured fields from text using simple heuristics.

    - Attempts key:value pairs for decision, reason_code, next_action (case-insensitive).
    - Extracts a days_allowed number when patterns like "25 days" appear.
    - If a top-level JSON object is present, merges its keys (shallow) preferring JSON values.
    """
    structured: Dict[str, Any] = {}
    t = text or ""

    # Try to detect and parse a JSON object in the text
    json_obj: Optional[Dict[str, Any]] = None
    try:
        candidate = t.strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                json_obj = parsed
    except Exception:
        json_obj = None

    # Key-value patterns
    for pat in _KV_PATTERNS:
        for m in pat.finditer(t):
            key = m.group(1).lower().replace(" ", "_")
            val = m.group(2).strip()
            # Trim trailing punctuation
            val = re.sub(r"[\s\.;:,]+$", "", val)
            if key == "decision":
                v = val.upper()
                if v in ("ALLOW", "DENY"):
                    structured[key] = v
                else:
                    structured[key] = val
            elif key == "next_action":
                # keep only the first clause/token before punctuation
                val = re.split(r"[\.;:,]", val, maxsplit=1)[0].strip()
                structured[key] = val
            else:
                structured[key] = val

    # Extract simple numeric hints like "25 days"
    m_days = re.search(r"(?i)(\d+)\s+days", t)
    if m_days:
        try:
            structured.setdefault("days_allowed", int(m_days.group(1)))
        except Exception:
            pass

    # Merge JSON object last to let it override heuristics
    if json_obj:
        for k, v in json_obj.items():
            structured[str(k)] = v

    return structured


def normalize_turn_output(raw_text: str, context_lines: List[str], metadata: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
    """Produce a canonical evaluation record from raw output and context.

    Returns a dict with: raw_text, text, structured, tools, metadata.
    """
    record: Dict[str, Any] = {
        "raw_text": raw_text,
        "text": canonicalize_text(raw_text),
        "structured": extract_structured(raw_text),
        "tools": extract_tool_results(context_lines),
        "metadata": dict(metadata or {}),
    }
    return record


__all__ = [
    "canonicalize_text",
    "extract_tool_results",
    "extract_structured",
    "normalize_turn_output",
]
