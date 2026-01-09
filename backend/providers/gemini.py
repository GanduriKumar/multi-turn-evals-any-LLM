from __future__ import annotations
import os
import time
from typing import Dict, Any, List
import httpx

try:
    from .types import ProviderRequest, ProviderResponse
except ImportError:
    from providers.types import ProviderRequest, ProviderResponse

GEMINI_API = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

class GeminiProvider:
    def __init__(self, api_key: str | None) -> None:
        self.api_key = api_key

    @property
    def enabled(self) -> bool:
        return bool(self.api_key)

    async def chat(self, req: ProviderRequest) -> ProviderResponse:
        if not self.enabled:
            return ProviderResponse(False, "", 0, {}, error="Gemini disabled: missing GOOGLE_API_KEY")
        t0 = time.perf_counter()
        url = GEMINI_API.format(model=req.model, key=self.api_key)
        temperature = 0.2
        top_p = 1.0
        max_output_tokens = 512
        try:
            p = (req.metadata or {}).get("params")
            if isinstance(p, dict):
                temperature = float(p.get("temperature", temperature))
                top_p = float(p.get("top_p", top_p))
                max_output_tokens = int(p.get("max_tokens", max_output_tokens))
        except Exception:
            pass
        # Build contents preserving roles and using systemInstruction for first system message
        system_msg = None
        contents = []
        for m in req.messages:
            role = (m.get("role") or "user").lower()
            text = m.get("content", "")
            if role == "system" and system_msg is None:
                system_msg = {"role": "system", "parts": [{"text": text}]}
                continue
            if role == "assistant":
                role = "model"  # Gemini expects 'model' for assistant messages
            contents.append({"role": role, "parts": [{"text": text}]})

        payload = {
            "contents": contents if contents else [{"role": "user", "parts": [{"text": ""}]}],
            "generationConfig": {
                "temperature": temperature,
                "topP": top_p,
                "maxOutputTokens": max_output_tokens,
            }
        }
        if system_msg is not None:
            payload["systemInstruction"] = system_msg
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                r = await client.post(url, json=payload)
                latency_ms = int((time.perf_counter() - t0) * 1000)
                if r.status_code != 200:
                    return ProviderResponse(False, "", latency_ms, {"status": r.status_code}, error=r.text)
                data = r.json()
                text = (
                    data.get("candidates", [{}])[0]
                    .get("content", {})
                    .get("parts", [{}])[0]
                    .get("text", "")
                )
                return ProviderResponse(True, text, latency_ms, {"candidates": len(data.get("candidates", []))})
            except Exception as e:
                latency_ms = int((time.perf_counter() - t0) * 1000)
                return ProviderResponse(False, "", latency_ms, {}, error=str(e))
