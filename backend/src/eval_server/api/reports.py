from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from ..reporting.report_generator import generate_html_report
from ..reporting.markdown_export import generate_markdown_report
from ..reporting.comparison_generator import generate_comparison_report


router = APIRouter(prefix="/reports", tags=["reports"])


@router.post("/html", summary="Generate HTML report", description="Generate an HTML report from a results.json path.")
def generate_html(results_path: str, theme: str = Query("default", enum=["default", "dark", "compact"])):
    p = Path(results_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="results not found")
    try:
        out = generate_html_report(p, theme=theme)
        return {"report": str(out)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to generate report: {e}")


@router.post("/markdown", summary="Generate Markdown report", description="Generate a Markdown report from a results.json path.")
def generate_markdown(results_path: str):
    p = Path(results_path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="results not found")
    try:
        out = generate_markdown_report(p)
        return {"report": str(out)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to generate markdown: {e}")


@router.post("/compare", summary="Generate comparison report", description="Generate an HTML comparison report between two results.json files.")
def generate_comparison(results_path: str, baseline_results_path: str):
    rp = Path(results_path)
    bp = Path(baseline_results_path)
    if not rp.exists() or not bp.exists():
        raise HTTPException(status_code=404, detail="results or baseline not found")
    try:
        out = generate_comparison_report(rp, bp)
        return {"report": str(out)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"failed to generate comparison: {e}")
