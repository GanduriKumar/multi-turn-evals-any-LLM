from fastapi import FastAPI
from pydantic import BaseModel
import os

APP_VERSION = "0.1.0-mvp"

class Health(BaseModel):
    status: str

class VersionInfo(BaseModel):
    version: str
    gemini_enabled: bool
    ollama_host: str | None
    semantic_threshold: float


def get_settings():
    google_api_key = os.getenv("GOOGLE_API_KEY")
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    semantic_threshold = float(os.getenv("SEMANTIC_THRESHOLD", "0.80"))
    return {
        "GOOGLE_API_KEY": google_api_key,
        "OLLAMA_HOST": ollama_host,
        "SEMANTIC_THRESHOLD": semantic_threshold,
    }

app = FastAPI(title="LLM Eval Backend", version=APP_VERSION)

@app.get("/health", response_model=Health)
async def health():
    return Health(status="ok")

@app.get("/version", response_model=VersionInfo)
async def version():
    s = get_settings()
    return VersionInfo(
        version=APP_VERSION,
        gemini_enabled=bool(s["GOOGLE_API_KEY"]),
        ollama_host=s["OLLAMA_HOST"],
        semantic_threshold=s["SEMANTIC_THRESHOLD"],
    )

