from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi.websockets import WebSocket, WebSocketDisconnect

from .progress_registry import registry


router = APIRouter(prefix="/runs", tags=["progress"])  # shares /runs prefix


class ConversationProgress(BaseModel):
    dataset_id: str
    conversation_id: str
    model: str
    status: str
    progress: float


class RunProgressResponse(BaseModel):
    run_id: str
    overall_status: str
    conversations: List[ConversationProgress]
    events: List[Dict[str, Any]]


@router.get("/{run_id}/progress", response_model=RunProgressResponse, summary="Get run progress", description="Return overall and per-conversation progress for a run.")
def get_progress(run_id: str):
    try:
        status = registry.get_status(run_id)
        return RunProgressResponse(
            run_id=status.get("run_id"),
            overall_status=status.get("overall_status"),
            conversations=[ConversationProgress(**c) for c in status.get("conversations", [])],
            events=list(status.get("events", [])),
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="run not found")


@router.websocket("/{run_id}/progress/ws")
async def ws_progress(ws: WebSocket, run_id: str):
    await ws.accept()
    try:
        # Basic polling loop to push updates periodically
        last_payload: Any = None
        while True:
            try:
                status = registry.get_status(run_id)
            except KeyError:
                await ws.send_json({"error": "run not found"})
                break
            if status != last_payload:
                await ws.send_json(status)
                last_payload = status
            if registry.is_done(run_id):
                break
            await asyncio.sleep(0.2)
    except WebSocketDisconnect:
        return
    finally:
        try:
            await ws.close()
        except Exception:
            pass
