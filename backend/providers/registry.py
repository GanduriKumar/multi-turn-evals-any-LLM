from __future__ import annotations
import os
from typing import Dict
from pathlib import Path

# Load .env from repo root so CLI and scripts pick up API keys without starting the web app
def _load_env_from_file() -> None:
    try:
        root = Path(__file__).resolve().parents[2]
        env_path = root / '.env'
        if env_path.exists():
            try:
                from dotenv import load_dotenv  # type: ignore
                load_dotenv(env_path)
                return
            except Exception:
                pass
            # Fallback simple loader if python-dotenv is unavailable
            for line in env_path.read_text(encoding='utf-8').splitlines():
                line = line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                k, v = line.split('=', 1)
                k = k.strip(); v = v.strip()
                if k and v and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        # non-fatal
        pass

_load_env_from_file()

try:
    from .ollama import OllamaProvider
    from .gemini import GeminiProvider
    from .openai import OpenAIProvider
except ImportError:
    from providers.ollama import OllamaProvider
    from providers.gemini import GeminiProvider
    from providers.openai import OpenAIProvider

class ProviderRegistry:
    def __init__(self) -> None:
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self._ollama = OllamaProvider(self.ollama_host)
        self._gemini = GeminiProvider(self.google_api_key)
        self._openai = OpenAIProvider(self.openai_api_key)

    @property
    def gemini_enabled(self) -> bool:
        return self._gemini.enabled

    def get(self, provider: str):
        if provider == "ollama":
            return self._ollama
        if provider == "gemini":
            return self._gemini
        if provider == "openai":
            return self._openai
        raise KeyError(f"Unknown provider: {provider}")
