from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Dict

from fastapi import APIRouter, HTTPException
from ..utils.errors import NotFoundError


router = APIRouter(prefix="/results", tags=["results"])


def _find_run_dir(run_id: str) -> Path:
    base = Path("runs")
    if not base.exists():
        raise NotFoundError("runs directory not found")
    for p in base.iterdir():
        if p.is_dir() and run_id in p.name:
            return p
    raise NotFoundError(f"run not found: {run_id}")


@router.get("/{run_id}/summary", response_model=Dict[str, Any], summary="Get run summary", description="Return orchestrator summary.json merged with a path field.")
def get_summary(run_id: str) -> Dict[str, Any]:
    try:
        d = _find_run_dir(run_id)
        path = d / "summary.json"
        if not path.exists():
            raise NotFoundError("summary not found")
        return {"path": str(path), **__import__('json').loads(path.read_text(encoding='utf-8'))}
    except NotFoundError as e:
        raise e


@router.get("/{run_id}/results", response_model=Dict[str, Any], summary="Get consolidated results", description="Return consolidated results.json with per-conversation aggregates and turn metrics.")
def get_results(run_id: str) -> Dict[str, Any]:
    try:
        d = _find_run_dir(run_id)
        path = d / "results.json"
        if not path.exists():
            raise NotFoundError("results not found")
        return {"path": str(path), **__import__('json').loads(path.read_text(encoding='utf-8'))}
    except NotFoundError as e:
        raise e
