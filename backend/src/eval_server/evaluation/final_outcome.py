from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Optional


def _contains_all(text: str, terms: Iterable[str]) -> bool:
    t = text.lower()
    return all(term.lower() in t for term in terms)


def _contains_any(text: str, terms: Iterable[str]) -> bool:
    t = text.lower()
    return any(term.lower() in t for term in terms)


def evaluate_final_outcome(
    transcript_text: str,
    golden: Mapping[str, Any],
    *,
    conversation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Evaluate final conversation outcome against golden expectations.

    - transcript_text: concatenated assistant outputs or a summary representing the conversation result.
    - golden: parsed golden dictionary containing optional final_outcome.
    - conversation_id: used to disambiguate if golden includes multiple conversations per file.

    Returns a result dict with fields: checked (bool), success (bool|None), reasons (list[str]).
    """
    result = {"checked": False, "success": None, "reasons": []}  # type: ignore[dict-item]
    fo = golden.get("final_outcome")
    if not isinstance(fo, Mapping):
        return result

    # If a root conversation_id exists, prefer it; else read from final_outcome
    root_conv = golden.get("conversation_id")
    fo_conv = fo.get("conversation_id")
    if conversation_id is not None:
        target_conv = conversation_id
    else:
        target_conv = root_conv or fo_conv

    # If provided conversation_id does not match final_outcome's, treat as not applicable
    if fo_conv and target_conv and str(fo_conv) != str(target_conv):
        return result

    success_flag = fo.get("success")
    must_inc = list(fo.get("must_include", []) or [])
    must_not = list(fo.get("must_not_include", []) or [])

    result["checked"] = True

    reasons = []
    ok = True
    if must_inc and not _contains_all(transcript_text, must_inc):
        ok = False
        reasons.append("Missing required terms in final transcript")
    if must_not and _contains_any(transcript_text, must_not):
        ok = False
        reasons.append("Contains forbidden terms in final transcript")
    if isinstance(success_flag, bool):
        # If explicit success desired, require ok and 'success' cue if present.
        # We interpret 'success' as additional required cue; here we only set it as ok passthrough.
        # Real systems could attach structured signals; keeping deterministic behavior for tests.
        if not ok and success_flag:
            reasons.append("Expected success but constraints not satisfied")
        if ok and not success_flag:
            reasons.append("Expected failure but constraints indicate success")
        ok = ok and success_flag

    result["success"] = ok
    result["reasons"] = reasons
    return result


__all__ = ["evaluate_final_outcome"]
