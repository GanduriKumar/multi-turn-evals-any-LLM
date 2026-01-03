from __future__ import annotations

import getpass
import hashlib
import json
import os
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Optional


DEFAULT_LOG_PATH = Path(os.environ.get("AUDIT_LOG_PATH", "runs/audit_log.jsonl"))


def _to_plain(obj: Any) -> Any:
    """Convert dataclasses and Paths to JSON-serializable structures."""
    # Only treat dataclass instances (not classes) as serializable
    if is_dataclass(obj) and not isinstance(obj, type):
        return {k: _to_plain(v) for k, v in asdict(obj).items()}
    if isinstance(obj, Path):
        return obj.as_posix()
    if isinstance(obj, dict):
        return {str(k): _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(v) for v in obj]
    return obj


def _stable_dumps(data: Any) -> str:
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def compute_config_fingerprint(run_config: Any, config_path: Optional[Path] = None) -> str:
    """Compute a stable SHA-256 fingerprint for a run config.

    Uses file bytes if a config_path is provided and exists; otherwise, hashes a
    normalized JSON representation of the config object.
    """
    try:
        if config_path and Path(config_path).exists():
            data = Path(config_path).read_bytes()
            return hashlib.sha256(data).hexdigest()
    except Exception:
        pass

    try:
        plain = _to_plain(run_config)
        payload = _stable_dumps(plain)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()
    except Exception:
        return ""


def _resolve_actor(actor: Optional[str] = None) -> str:
    if actor:
        return actor
    env_actor = os.environ.get("AUDIT_ACTOR")
    if env_actor:
        return env_actor
    try:
        return getpass.getuser()
    except Exception:
        return "unknown"


def log_audit_event(
    *,
    action: str,
    run_id: Optional[str] = None,
    config_path: Optional[str | Path] = None,
    config_fingerprint: Optional[str] = None,
    actor: Optional[str] = None,
    source: str = "orchestrator",
    details: Optional[Mapping[str, Any]] = None,
    log_path: Optional[str | Path] = None,
) -> None:
    """Append a JSON audit record.

    Failures in logging are swallowed to avoid interrupting evaluations.
    """
    ts = datetime.now(timezone.utc).isoformat()
    entry = {
        "timestamp": ts,
        "action": action,
        "run_id": run_id,
        "config_path": str(config_path) if config_path else None,
        "config_fingerprint": config_fingerprint,
        "actor": _resolve_actor(actor),
        "source": source,
        "details": dict(details) if details else {},
    }
    path = Path(log_path) if log_path else DEFAULT_LOG_PATH
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        # Do not propagate logging errors
        return


__all__ = ["log_audit_event", "compute_config_fingerprint", "DEFAULT_LOG_PATH"]
