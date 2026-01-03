from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..data.loader import load_conversation, load_golden
from ..data.golden_access import index_golden


router = APIRouter(prefix="/datasets", tags=["datasets"])


class DatasetInfo(BaseModel):
    id: str
    name: str
    conversation: str
    golden: str
    conversation_version: str | None = None
    golden_version: str | None = None
    tags: list[str] = []
    difficulty: str | None = None


class ConversationGoldenResponse(BaseModel):
    dataset_id: str
    conversation_id: str
    conversation: Dict[str, Any]
    golden: Dict[str, Any]


def _list_example_datasets() -> List[DatasetInfo]:
    base = Path("configs/datasets/examples")
    items: List[DatasetInfo] = []
    if not base.exists():
        return items
    # naive pairing by filename stem where possible
    convs = {p.stem: p for p in base.glob("*.json") if p.name.endswith(".json") and not p.name.endswith(".golden.json")}
    goldens = {p.stem.replace(".golden", ""): p for p in base.glob("*.golden.*")}
    for stem, conv in convs.items():
        g = goldens.get(stem)
        if g is None:
            continue
        try:
            c = load_conversation(conv)
            gl = load_golden(g)
            meta = (c.get("metadata") or {}) if isinstance(c, dict) else {}
            tags = list(meta.get("tags") or [])
            difficulty = meta.get("difficulty")
            items.append(DatasetInfo(
                id=stem,
                name=str(c.get("conversation_id") or stem),
                conversation=str(conv),
                golden=str(g),
                conversation_version=str(c.get("version")) if isinstance(c, dict) else None,
                golden_version=str(gl.get("version")) if isinstance(gl, dict) else None,
                tags=tags,
                difficulty=str(difficulty) if difficulty else None,
            ))
        except Exception:
            # skip invalid
            continue
    return items


@router.get("/", response_model=List[DatasetInfo], summary="List datasets", description="List available example datasets with basic metadata. Supports simple pagination.")
def list_datasets(page: int = Query(1, ge=1), page_size: int = Query(100, ge=1, le=1000)) -> List[DatasetInfo]:
    # For now, expose examples folder with simple pagination
    all_items = _list_example_datasets()
    start = (page - 1) * page_size
    end = start + page_size
    return all_items[start:end]


def _get_dataset_by_id(dataset_id: str) -> DatasetInfo:
    for d in _list_example_datasets():
        if d.id == dataset_id:
            return d
    raise HTTPException(status_code=404, detail="dataset not found")


@router.get("/{dataset_id}/conversations/{conversation_id}", response_model=ConversationGoldenResponse, summary="Get conversation and golden", description="Return conversation JSON and filtered golden expectations for a dataset conversation.")
def get_conversation_details(dataset_id: str, conversation_id: str) -> ConversationGoldenResponse:
    # Find dataset files
    ds = _get_dataset_by_id(dataset_id)
    conv = load_conversation(ds.conversation)
    gold = load_golden(ds.golden)

    conv_id = str(conv.get("conversation_id"))
    if conv_id != conversation_id:
        # The requested conversation_id doesn't match the file's conversation
        raise HTTPException(status_code=404, detail="conversation not found in dataset")

    # Filter golden expectations for this conversation id
    root_conv = str(gold.get("conversation_id", "") or "").strip()
    filtered_exps: List[Dict[str, Any]] = []
    for item in gold.get("expectations", []) or []:
        item_conv = str(item.get("conversation_id", root_conv) or "").strip()
        if item_conv == conv_id:
            filtered_exps.append(item)

    # Include final_outcome if applicable to this conversation
    final_outcome = None
    fo = gold.get("final_outcome")
    if isinstance(fo, dict):
        fo_conv = str(fo.get("conversation_id", root_conv) or "").strip()
        if fo_conv == conv_id:
            final_outcome = fo

    golden_payload: Dict[str, Any] = {
        "version": gold.get("version"),
        "conversation_id": root_conv or conv_id,
        "expectations": filtered_exps,
    }
    if final_outcome is not None:
        golden_payload["final_outcome"] = final_outcome

    return ConversationGoldenResponse(
        dataset_id=dataset_id,
        conversation_id=conv_id,
        conversation=conv,  # type: ignore[arg-type]
        golden=golden_payload,
    )


@router.get("/{dataset_id}", response_model=DatasetInfo, summary="Get dataset", description="Return dataset metadata by id.")
def get_dataset(dataset_id: str):
    for d in _list_example_datasets():
        if d.id == dataset_id:
            return d
    raise HTTPException(status_code=404, detail="dataset not found")
