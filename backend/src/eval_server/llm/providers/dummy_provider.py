from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..provider_registry import LLMProvider, register_provider


class DummyProvider(LLMProvider):
    """A deterministic provider used for testing the registry and flow."""

    def __init__(self) -> None:
        self._name = "dummy"
        self._prefix = ""
        self._version = "1.0"
        self._last_meta: Dict[str, Any] = {}

    def initialize(self, **kwargs: Any) -> None:
        # Allow a configurable prefix to demonstrate init usage
        self._prefix = str(kwargs.get("prefix", "DUMMY:")).strip()
        if not self._prefix:
            self._prefix = "DUMMY:"

    def generate(self, prompt: str, context: List[str] | None = None) -> str:
        # Deterministic composition of context and prompt
        ctx_part = " | ".join(context or [])
        if ctx_part:
            text = f"{self._prefix} [{ctx_part}] -> {prompt}"
        else:
            text = f"{self._prefix} {prompt}"
        # Compute simple token usage
        prompt_tok = (len(prompt.split()) + sum(len(s.split()) for s in (context or [])))
        completion_tok = len(text.split())
        self._last_meta = {
            "usage": {
                "prompt_tokens": prompt_tok,
                "completion_tokens": completion_tok,
            },
            "provider": self._name,
            "version": self._version,
        }
        return text

    def metadata(self) -> Dict[str, Any]:
        return {
            "name": self._name,
            "version": self._version,
            "supports_context": True,
        }

    # Optional hook to expose last call metadata
    def last_metadata(self) -> Dict[str, Any]:
        return dict(self._last_meta)


# Auto-register on import
register_provider("dummy", DummyProvider)
