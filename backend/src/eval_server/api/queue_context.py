from __future__ import annotations

from ..queue import ExecutionQueue

# Singleton queue shared across API modules
queue = ExecutionQueue()

__all__ = ["queue"]
