from __future__ import annotations

from pathlib import Path
import json

from eval_server.runner.turn_runner import TurnRunner


def test_raw_outputs_capture_tokens_latency_metadata():
    repo = Path(__file__).resolve().parents[2]
    conv_path = repo / "configs" / "datasets" / "examples" / "conversation_001.json"
    conversation = json.loads(conv_path.read_text(encoding="utf-8"))

    runner = TurnRunner("dummy", prefix="RAW:")
    results = runner.run(conversation)

    r = results[0]
    assert r.llm_request is not None
    assert r.llm_response is not None

    # Token usage should be computed and total consistent
    usage = r.llm_response.usage
    assert usage.total_tokens == usage.prompt_tokens + usage.completion_tokens

    # Latency should be non-negative
    assert r.llm_response.latency_ms >= 0.0

    # Provider metadata must include context_length
    assert "context_length" in r.llm_response.provider_metadata


def test_error_metadata_on_exception(monkeypatch):
    # Force provider.generate to raise
    runner = TurnRunner("dummy", prefix="ERR:")

    def boom(prompt: str, context):
        raise RuntimeError("boom")

    # Monkeypatch the underlying provider
    monkeypatch.setattr(runner._provider, "generate", boom)

    conversation = {
        "version": "1.0.0",
        "conversation_id": "c",
        "turns": [
            {"turn_id": "t1", "role": "system", "content": "hello"},
            {"turn_id": "t2", "role": "user", "content": "question"},
        ]
    }

    results = runner.run(conversation)
    r = results[0]
    assert r.error is not None and "RuntimeError" in r.error
    assert r.llm_request is not None
    # llm_response may be None on error, but provider_metadata should record error if response exists
    if r.llm_response is not None:
        assert "error" in r.llm_response.provider_metadata
