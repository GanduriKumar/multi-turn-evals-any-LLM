# Multi-Turn LLM Evaluation System (MVP)

Monorepo for a multi‑turn LLM evaluation platform.

- Backend: FastAPI REST API (under `backend/`)
- Frontend: React + Vite + TypeScript + Tailwind (under `frontend/`)
- Shared: `configs/`, `datasets/`, `scripts/`, `docs/`

Key capabilities
- Upload JSON datasets and goldens (multiple acceptable variants per turn)
- Select LLM provider/model: Ollama, Gemini, OpenAI
	- Default models configurable in Settings: `OLLAMA_MODEL`, `GEMINI_MODEL`, `OPENAI_MODEL`
- Configure/run evaluations with conversation state + last‑N turns context
- Job controls: Pause, Resume, Abort; stale run detection and “Mark as cancelled” for stale rows
- Metrics: exact, semantic (via local embeddings), consistency, adherence, hallucination
	- Semantic uses Ollama embeddings; set `EMBED_MODEL` (e.g., `nomic-embed-text`) and `OLLAMA_HOST`
	- Quick check endpoint: `GET /embeddings/test`
- Reports: HTML/CSV/JSON with conversation identity (slug/title/metadata), per‑turn snippets, rollups, token totals
- Compare two runs: `GET /compare?runA=&runB=`
- Persistence: filesystem (`runs/`)

What’s new recently
- Multi-vertical storage and runtime selection (header selector). Data under `datasets/<vertical>/` and `runs/<vertical>/`.
- Dataset Generator page (was Coverage Generator) to create datasets per strategy; appears first in the navbar.
- Datasets page renamed to “Datasets Viewer”.
- OpenAI provider support (set `OPENAI_API_KEY`; pick model in Runs)
- Settings page manages API keys, hosts, semantic threshold, default models, and `EMBED_MODEL`
- Metrics config persisted to `configs/metrics.json` and respected across UI and backend
- Rebuild endpoint to enrich old runs: `POST /runs/{run_id}/rebuild`
- Dataset schema additions: conversation `title` and `metadata.short_description`
- Report revamp: overview donut charts, failure tables, stacked summary
- Token accounting: Input/Output tokens aggregated per run; shown in HTML report and exported in CSV
- HTML artifact filenames: `report-{domain}-{behavior}-{model}.html`
- PDF backend fallbacks (WeasyPrint → Playwright → wkhtmltopdf); UI PDF button removed pending env readiness
- Runs page ring color reflects state (green success, red fail/cancel, amber otherwise)
- Prompt/context optimization: last 5 turns; budgets ~1800 input tokens, 400 max completion tokens
- Deterministic evaluation: temperature=0.0, seed=42 for reproducible results across runs

Getting started
- See `UserGuide.md` for end‑to‑end setup and usage.

Notes
- HTML report now includes:
	- Overview with conversation and turn pass donuts
	- Token usage totals (Input/Output)
	- Failure explanations tables (conversation and turn level)
	- Detailed per‑conversation metrics
- CSV adds `input_tokens_total` and `output_tokens_total` columns.
- PDF generation is supported by backend if dependencies are present, but the UI hides the button by default.

License
- Licensed under GNU GPL v3. See `LICENSE`.
