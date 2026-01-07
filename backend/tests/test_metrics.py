import types
import pytest

from metrics import exact_match, semantic_similarity
from embeddings.ollama_embed import OllamaEmbeddings


def test_exact_match_variants():
    res = exact_match("Refund of $10 processed", ["refund of $10 processed", "other"])
    assert res["pass"] is True

@pytest.mark.asyncio
async def test_semantic_similarity_mock(monkeypatch):
    async def fake_embed(self, texts):
        # Return identical vectors for output and first variant, orthogonal for second
        # Suppose 2-dim vectors: output=[1,0], v1=[1,0], v2=[0,1]
        return [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]]
    monkeypatch.setattr(OllamaEmbeddings, "embed", fake_embed, raising=True)

    res = await semantic_similarity("hello", ["hello", "world"], embedder=OllamaEmbeddings(), threshold=0.8)
    assert res["pass"] is True
    assert pytest.approx(res["score_max"], 1e-6) == 1.0
