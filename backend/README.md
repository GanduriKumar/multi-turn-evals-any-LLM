# Backend

FastAPI REST API providing dataset management, run orchestration, metrics, and reports.

- Stack: Python, FastAPI, Uvicorn
- Config: environment variables for providers and thresholds
- Endpoints: datasets, runs, status, results, artifacts, feedback (to be added in later prompts)

Run locally:
- Create a virtual env and install requirements: `pip install -r backend/requirements.txt`
- Start server: `uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000`

Environment:
- GOOGLE_API_KEY (optional)
- OLLAMA_HOST (default http://localhost:11434)
- SEMANTIC_THRESHOLD (default 0.80)

Endpoints now:
- GET /health
- GET /version

See root `docs/mvp-implementation-plan.md` for the roadmap.
