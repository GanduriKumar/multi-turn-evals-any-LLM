from __future__ import annotations

from pathlib import Path
from fastapi import APIRouter, HTTPException
from ..reporting.comparison_generator import generate_comparison_report


router = APIRouter(prefix="/comparisons", tags=["comparisons"])


@router.post("/")
def compare(results_path: str, baseline_results_path: str):
    rp = Path(results_path)
    bp = Path(baseline_results_path)
    if not rp.exists() or not bp.exists():
        raise HTTPException(status_code=404, detail="results or baseline not found")
    try:
        out = generate_comparison_report(rp, bp)
        return {"report": str(out)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to generate comparison: {e}")
