from __future__ import annotations
import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from dataset_repo import DatasetRepository
from turn_runner import TurnRunner


JobState = str  # 'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled'


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def compute_run_id(dataset_id: str, dataset_version: str, model_spec: str, config: Dict[str, Any]) -> str:
    # Deterministic checksum of relevant config fields
    relevant = {
        "metrics": config.get("metrics"),
        "thresholds": config.get("thresholds"),
        "context": config.get("context"),
    }
    blob = json.dumps(relevant, sort_keys=True).encode("utf-8")
    cksum = hashlib.sha256(blob).hexdigest()[:8]
    safe_model = model_spec.replace(":", "-")
    return f"{dataset_id}-{dataset_version}-{safe_model}-{cksum}"


@dataclass
class JobRecord:
    job_id: str
    run_id: str
    config: Dict[str, Any]
    state: JobState = "queued"
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    progress_pct: int = 0
    total_conversations: int = 0
    completed_conversations: int = 0
    error: Optional[str] = None
    _task: Optional[asyncio.Task] = None
    _cancel: bool = False


class Orchestrator:
    def __init__(self, datasets_dir: Optional[Path] = None, runs_root: Optional[Path] = None) -> None:
        self.repo = DatasetRepository(datasets_dir)
        self.runs_root = Path(runs_root) if runs_root else Path(__file__).resolve().parents[1] / "runs"
        self.runs_root.mkdir(parents=True, exist_ok=True)
        self.jobs: Dict[str, JobRecord] = {}
        self._id_seq = 0
        self._runner = TurnRunner(self.runs_root)

    @staticmethod
    def parse_model_spec(model_spec: str) -> tuple[str, str]:
        # format provider:model
        parts = model_spec.split(":", 1)
        if len(parts) != 2:
            raise ValueError("model spec must be 'provider:model'")
        return parts[0], parts[1]

    def submit(self, *, dataset_id: str, model_spec: str, config: Dict[str, Any]) -> JobRecord:
        ds = self.repo.get_dataset(dataset_id)
        run_id = compute_run_id(ds["dataset_id"], ds["version"], model_spec, config)
        self._id_seq += 1
        job_id = f"job-{self._id_seq:04d}"
        jr = JobRecord(job_id=job_id, run_id=run_id, config={"dataset_id": dataset_id, "model_spec": model_spec, **config})
        jr.total_conversations = len(ds.get("conversations", []))
        self.jobs[job_id] = jr
        return jr

    def cancel(self, job_id: str) -> None:
        jr = self.jobs[job_id]
        jr._cancel = True

    async def run_job(self, job_id: str) -> JobRecord:
        jr = self.jobs[job_id]
        if jr.state not in ("queued",):
            return jr
        jr.state = "running"
        jr.updated_at = _now_iso()

        try:
            ds = self.repo.get_dataset(jr.config["dataset_id"])
            provider, model = self.parse_model_spec(jr.config["model_spec"])  # e.g., 'ollama', 'llama3.2:2b'
            domain = ds.get("metadata", {}).get("domain", "commerce")

            # Ensure run folder exists even if downstream is mocked
            run_folder = self.runs_root / jr.run_id
            run_folder.mkdir(parents=True, exist_ok=True)

            for conv in ds.get("conversations", []):
                if jr._cancel:
                    jr.state = "cancelled"
                    jr.updated_at = _now_iso()
                    return jr
                conv_id = conv.get("conversation_id")
                turns = conv.get("turns", [])
                # iterate user turns only
                for idx, t in enumerate(turns):
                    if t.get("role") == "user":
                        await self._runner.run_turn(
                            run_id=jr.run_id,
                            provider=provider,
                            model=model,
                            domain=domain,
                            conversation_id=conv_id,
                            turn_index=idx,
                            turns=turns[: idx + 1],
                        )
                jr.completed_conversations += 1
                jr.progress_pct = int(jr.completed_conversations * 100 / max(1, jr.total_conversations))
                jr.updated_at = _now_iso()

            jr.state = "succeeded"
            jr.updated_at = _now_iso()
            jr.progress_pct = 100
            return jr
        except Exception as e:
            jr.state = "failed"
            jr.error = str(e)
            jr.updated_at = _now_iso()
            return jr

    def start(self, job_id: str) -> None:
        jr = self.jobs[job_id]
        if jr._task and not jr._task.done():
            return
        jr._task = asyncio.create_task(self.run_job(job_id))

    async def wait(self, job_id: str) -> JobRecord:
        jr = self.jobs[job_id]
        if jr._task:
            await jr._task
        return jr
