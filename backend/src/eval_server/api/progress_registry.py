from __future__ import annotations

import threading
from typing import Any, Dict, List, Tuple


class ProgressRegistry:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        # run_id -> state
        self._runs: Dict[str, Dict[str, Any]] = {}

    def init_run(self, run_id: str) -> None:
        with self._lock:
            if run_id not in self._runs:
                self._runs[run_id] = {
                    "overall_status": "running",
                    "events": [],  # recent events
                    # key: (dataset_id, model) -> {status, progress, conversation_id}
                    "conversations": {},
                }

    def record_event(self, run_id: str, evt: Dict[str, Any]) -> None:
        with self._lock:
            st = self._runs.setdefault(run_id, {"overall_status": "running", "events": [], "conversations": {}})
            # Keep last 100 events
            st["events"].append(evt)
            st["events"] = st["events"][-100:]

            ds = str(evt.get("dataset_id") or "")
            conv_id = str(evt.get("conversation_id") or "")
            model = str(evt.get("model") or evt.get("model_name") or "")
            key = (ds, model)
            convs: Dict[Tuple[str, str], Dict[str, Any]] = st["conversations"]  # type: ignore[assignment]
            meta = convs.get(key, {"status": "running", "progress": 0.0, "conversation_id": conv_id})
            if conv_id:
                meta["conversation_id"] = conv_id

            etype = evt.get("event")
            if etype == "start":
                meta["status"] = "running"
                meta["progress"] = 0.0
            elif etype == "turn":
                # coarse progress: at least mid-way
                meta["status"] = "running"
                meta["progress"] = max(float(meta.get("progress", 0.0)), 50.0)
            elif etype == "end":
                status = str(evt.get("status") or "completed")
                meta["status"] = status
                meta["progress"] = 100.0
            convs[key] = meta

            # determine overall
            statuses = {m.get("status") for m in convs.values()}
            if "cancelled" in statuses:
                st["overall_status"] = "cancelled"
            elif statuses and statuses.issubset({"completed", "cancelled"}):
                st["overall_status"] = "completed"
            else:
                st["overall_status"] = "running"

    def get_status(self, run_id: str) -> Dict[str, Any]:
        with self._lock:
            st = self._runs.get(run_id)
            if not st:
                raise KeyError("run not found")
            # materialize conversations to list with fields
            convs = []
            for (ds, model), meta in st["conversations"].items():
                convs.append({
                    "dataset_id": ds,
                    "conversation_id": meta.get("conversation_id", ""),
                    "model": model,
                    "status": meta.get("status"),
                    "progress": meta.get("progress", 0.0),
                })
            return {
                "run_id": run_id,
                "overall_status": st.get("overall_status", "running"),
                "conversations": convs,
                "events": list(st.get("events", [])),
            }

    def is_done(self, run_id: str) -> bool:
        try:
            st = self.get_status(run_id)
            return st.get("overall_status") in {"completed", "cancelled"}
        except KeyError:
            return True


registry = ProgressRegistry()

__all__ = ["registry"]
