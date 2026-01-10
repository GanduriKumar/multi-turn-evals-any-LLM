# User Guide — Multi‑Turn LLM Evaluation System (MVP)

Welcome! This guide will help you install, run, and use the Multi‑Turn LLM Evaluation System. It uses simple language and walks you through the key features step‑by‑step.

If you’re new to the project, start here.

---

## What this app does

This app lets you evaluate Large Language Models (LLMs) on multi‑turn conversations. You can:
- Upload datasets (conversations) and matching golden files (expected answers).
- Choose a model (local Ollama or Google Gemini).
- Run evaluations and watch progress live.
- View a report with scores per turn and per conversation.
- Export results (JSON/CSV/HTML) and add human feedback.

Everything is stored on your local filesystem. No database needed. The app is a monorepo with a Python backend (FastAPI) and a React frontend (Vite + TypeScript).

---

## Requirements

- Windows 10/11 (PowerShell)
- Python 3.12 (recommended) with virtual environment
- Node.js 18+ and npm
- Optional for LLMs (choose any):
  - Ollama running locally (default host http://localhost:11434) with model `OLLLAMA_MODEL` (default `llama3.2:latest`)
  - Google Gemini API Key (for model `GEMINI_MODEL`, default `gemini-2.5`)
  - OpenAI API Key (for model `OPENAI_MODEL`, default `gpt-5.1`)

Example: Install Ollama and pull a model
- Download Ollama from https://ollama.com and start it.
- In a terminal: `ollama pull llama3.2:latest`

---

## First‑time setup

1) Clone or open the repo folder in VS Code.

2) Python environment (from repo root):
- Create and activate a virtual environment, then install backend dependencies
  - `python -m venv .venv`
  - `.\\.venv\\Scripts\\Activate.ps1`
  - `pip install -r backend/requirements.txt`

3) Node dependencies (frontend):
- `cd frontend`
- `npm install`

4) Optional providers
- Ollama: ensure it’s running and pull the model:
  - `ollama pull llama3.2:latest`
- Gemini: obtain an API key from Google AI Studio.

---

## Start the app (dev)
# User Guide — Multi‑Turn LLM Evaluation System (MVP)

Welcome! This guide will help you install, run, and use the Multi‑Turn LLM Evaluation System. It uses simple language and walks you through the key features step‑by‑step.

Use the provided script to run both backend and frontend together:
This app lets you evaluate Large Language Models (LLMs) on multi‑turn conversations. You can:
 Upload datasets (conversations) and matching golden files (expected answers).
- Choose a model (local Ollama, Google Gemini, or OpenAI).
- Start backend API at http://localhost:8000
- Start frontend at http://localhost:5173
 Windows 10/11 (PowerShell)
 Python 3.12 (recommended) with virtual environment
 Node.js 18+ and npm
 Optional for LLMs (choose any):
  - Ollama running locally (default host http://localhost:11434) with model `OLLLAMA_MODEL` (default `llama3.2:latest`)
  - Google Gemini API Key (for model `GEMINI_MODEL`, default `gemini-2.5`)
  - OpenAI API Key (for model `OPENAI_MODEL`, default `gpt-5.1`)
  - `npm run dev`

 1) Clone or open the repo folder in VS Code.

 2) Python environment (from repo root):
 - Create and activate a virtual environment, then install backend dependencies
   - `python -m venv .venv`
   - `.\\.venv\\Scripts\\Activate.ps1`
   - `pip install -r backend/requirements.txt`

## Quick smoke test
 Use the provided script to run both backend and frontend together:
 - Run: `.\\scripts\\dev.ps1`
- It will check /health and /datasets on the backend.

 - Run: `.\\scripts\\smoke.ps1`
 - It will check /health and /datasets on the backend.
## Using the UI


### 1. Datasets Viewer
 Open http://localhost:5173 in your browser.

Tips and examples:
 Choose a dataset and a model.
- You can also place files manually in `datasets/`. Use the same naming convention.

 Select a run to view a summary.
 Download results as JSON/CSV, or open the HTML report.
 - Submit human feedback (rating, notes). Optionally override conversation‑level pass/fail or a specific turn’s pass/fail. Feedback is stored at `runs/<run_id>/feedback.json` and does not change auto‑scores.
 - Examples:
 - Download JSON: opens `runs/<run_id>/results.json`.
 - Download CSV: opens `runs/<run_id>/results.csv`.
 - Open Report: generates and opens `runs/<run_id>/report-<domain>-<behavior>-<model>.html` when metadata is available.
    {
      "conversation_id": "conv42",
 Configure providers and thresholds:
 - OLLAMA_HOST
 - GOOGLE_API_KEY, OPENAI_API_KEY
 - Semantic threshold
 - Default models: OLLAMA_MODEL, GEMINI_MODEL, OPENAI_MODEL
 - EMBED_MODEL for semantic similarity
 These settings are saved to a local `.env` at the repo root and loaded at startup. Restart backend after changes.
```

 Enable/disable metrics and adjust weights/thresholds.
 Saved to `configs/metrics.json`.
{
  "dataset_id": "commerce_easy",
 Create evaluation datasets automatically using the configured strategy.
 Optionally save generated datasets and goldens to disk.
 Located as the first item in the navigation bar.
      "conversation_id": "conv42",
      "turns": [
      ],
      "final_outcome": { "decision": "ALLOW", "next_action": "issue_refund" }
 backend/ — FastAPI app and evaluation engine
 frontend/ — React + Vite UI
 configs/schemas/ — JSON Schemas (dataset, golden, run_config)
 datasets/<vertical>/ — Your datasets and golden files (per industry vertical)
 runs/<vertical>/ — Generated run artifacts (results.json, results.csv, report.html, per‑turn JSON)
 scripts/ — Helper scripts (dev.ps1, smoke.ps1)
 docs/ — Additional documentation
 - docs/GOVERNANCE.md — Coverage governance & versioning guide (Prompt 13)
- Click Start Run. You’ll see live progress and completion status.

 Common endpoints:
 - GET /health — basic status
 - GET /version — version, provider flags, and default models
 - GET /datasets — list datasets (accepts `?vertical=`)
 - POST /datasets/upload — upload dataset and optional golden
 - GET /datasets/{dataset_id} — get dataset JSON
 - GET /goldens/{dataset_id} — get golden JSON
 - POST /datasets/save — validate and write dataset/golden
 - POST /validate — validate JSON against schemas (dataset/golden/run_config)
 - POST /runs — start a run (UI passes context.vertical)
 - GET /runs — list runs (accepts `?vertical=`)
 - GET /runs/{job_id}/status — live job status
 - GET /runs/{run_id}/results — get results.json (accepts `?vertical=`)
 - GET /runs/{run_id}/artifacts?type=json|csv|html — download/export (HTML includes token totals; CSV includes input_tokens_total/output_tokens_total)
 - POST /runs/{run_id}/feedback — append human feedback
 - GET /compare?runA=&runB= — compare run summaries
 - GET /settings — read settings (providers, models, embedding)
 - POST /settings — update .env (dev only)
 - GET /embeddings/test — verify embedding endpoint/model
 - GET/POST /metrics-config — read/write metrics configuration
 - GET /coverage/taxonomy — list domains and behaviors
 - GET /coverage/manifest — preview counts per domain×behavior pair (query params: domains, behaviors)
 - POST /coverage/generate — generate datasets/goldens (combined or split) with options to save (stores under `datasets/<vertical>/`)
 - POST /coverage/generate (as_array=true) — emit a single JSON array with the combined scenario schema (Prompt 14)
 - GET /coverage/report.csv?type=summary|heatmap — download CSV reports
 - POST /coverage/per-turn.csv — generate a per-turn CSV for a dataset/golden payload
 - GET/POST /coverage/settings — read/write coverage strategy (pairwise/exhaustive, budgets, sampler overrides; Prompt 13)
- Download JSON: opens `runs/<run_id>/results.json`.
- Download CSV: opens `runs/<run_id>/results.csv`.
 ModuleNotFoundError: No module named 'backend'
 - Start backend from repo root, or run .\scripts\dev.ps1 which sets PYTHONPATH.
 - Avoid using --reload on Windows; it can break imports.
- Configure providers and thresholds:
  - OLLAMA_HOST
 Dataset (.dataset.json)
 - Fields: dataset_id, version, metadata { domain, difficulty, tags? }, conversations [ { conversation_id, turns: [{ role, text }] } ]
 - Golden (.golden.json)
 - Fields: dataset_id, version, entries [ { conversation_id, turns: [{ turn_index, expected { variants: string[] } }], final_outcome, constraints? } ]
 - Run results (results.json)
 - Summary per conversation with per‑turn metrics and overall pass/fail.
Example `.env` file:
```
OLLAMA_HOST=http://localhost:11434
GOOGLE_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key
SEMANTIC_THRESHOLD=0.80
OLLAMA_MODEL=llama3.2:latest
GEMINI_MODEL=gemini-2.5
OPENAI_MODEL=gpt-5.1
EMBED_MODEL=nomic-embed-text

Note: “.env (dev-only)” in the UI means these values are stored locally in `.env` for development. Restart the backend to apply.
```

### 5. Metrics page
- Enable/disable metrics and adjust weights/thresholds.
– Saved to `configs/metrics.json`.

Example `configs/metrics.json` structure:
```json
{
  "metrics": [
    { "name": "exact_match", "enabled": true, "weight": 1.0 },
    { "name": "semantic_similarity", "enabled": true, "weight": 1.0, "threshold": 0.8 },
    { "name": "consistency", "enabled": true, "weight": 1.0 },
    { "name": "adherence", "enabled": true, "weight": 1.0 },
    { "name": "hallucination", "enabled": true, "weight": 1.0 }
  ]
}
 See CONTRIBUTING.md for coding standards and tests. For governance/versioning of coverage rules, see `docs/GOVERNANCE.md`.
 License: GPLv3 (see LICENSE).
### 6. Dataset Generator page (formerly “Coverage Generator”)
- Create evaluation datasets automatically using the configured strategy.
 Open an issue in the repository.
 Or ask in your team chat with a link to this guide.

Tips:
- Preview coverage first, then enable “Save to server” to write files.
- Files are stored per vertical under `datasets/<vertical>/`.

### 7. Golden Editor (deprecated)
This tool is currently hidden from the main navigation.

---

## File layout (important folders)

- backend/ — FastAPI app and evaluation engine
- frontend/ — React + Vite UI
- configs/schemas/ — JSON Schemas (dataset, golden, run_config)
- datasets/<vertical>/ — Your datasets and golden files (per industry vertical)
- runs/<vertical>/ — Generated run artifacts (results.json, results.csv, report.html, per‑turn JSON)
- scripts/ — Helper scripts (dev.ps1, smoke.ps1)
- docs/ — Additional documentation
  - docs/GOVERNANCE.md — Coverage governance & versioning guide (Prompt 13)

---

## REST API overview (for advanced users)

Common endpoints:
- GET /health — basic status
- GET /version — version, provider flags, and default models
- GET /datasets — list datasets (accepts `?vertical=`)
- POST /datasets/upload — upload dataset and optional golden
- GET /datasets/{dataset_id} — get dataset JSON
- GET /goldens/{dataset_id} — get golden JSON
- POST /datasets/save — validate and write dataset/golden
- POST /validate — validate JSON against schemas (dataset/golden/run_config)
- POST /runs — start a run (UI passes context.vertical)
- GET /runs — list runs (accepts `?vertical=`)
- GET /runs/{job_id}/status — live job status
- GET /runs/{run_id}/results — get results.json (accepts `?vertical=`)
- GET /runs/{run_id}/artifacts?type=json|csv|html — download/export
- POST /runs/{run_id}/feedback — append human feedback
- GET /compare?runA=&runB= — compare run summaries
- GET /settings — read settings (providers, models, embedding)
- POST /settings — update .env (dev only)
- GET /embeddings/test — verify embedding endpoint/model
- GET/POST /metrics-config — read/write metrics configuration
- GET /coverage/taxonomy — list domains and behaviors
- GET /coverage/manifest — preview counts per domain×behavior pair (query params: domains, behaviors)
- POST /coverage/generate — generate datasets/goldens (combined or split) with options to save (stores under `datasets/<vertical>/`)
- POST /coverage/generate (as_array=true) — emit a single JSON array with the combined scenario schema (Prompt 14)
- GET /coverage/report.csv?type=summary|heatmap — download CSV reports
- POST /coverage/per-turn.csv — generate a per-turn CSV for a dataset/golden payload
- GET/POST /coverage/settings — read/write coverage strategy (pairwise/exhaustive, budgets, sampler overrides; Prompt 13)

---

## Troubleshooting

- ModuleNotFoundError: No module named 'backend'
  - Start backend from repo root, or run .\scripts\dev.ps1 which sets PYTHONPATH.
  - Avoid using --reload on Windows; it can break imports.
Non-deterministic results (flip-flopping scores)
- System now uses temperature=0.0 and seed=42 by default for deterministic outputs.
- If you see variations, ensure you're using the same model version (some providers may update models).
- Embeddings are cached per run to ensure consistent semantic scores.
- To change seed or temperature, pass params_override in run config context.params.
- Frontend cannot reach backend
  - Ensure backend is running on http://localhost:8000.
  - Vite dev server proxies API calls automatically, including /coverage endpoints.
  - If proxy fails, check `frontend/vite.config.ts` for the route and restart the dev server.

- Ollama errors or model not found
  - Install and start Ollama.
  - ollama pull llama3.2:latest
  - Check OLLAMA_HOST in Settings page.
  - Try a quick curl: `curl http://localhost:11434/api/tags` should list models.

- Gemini not enabled
  - Set GOOGLE_API_KEY via Settings, then restart backend.

- Semantic metric failures
  - Ensure Ollama is running, `EMBED_MODEL` is pulled, and `OLLAMA_HOST` is correct.
  - Use `GET /embeddings/test` to validate before running.

Verticals:
- Use the “Vertical” selector in the header to switch between industries.
- Storage is separated by vertical under `datasets/<vertical>/` and `runs/<vertical>/`.

Logs and artifacts:
- Backend logs in the terminal where uvicorn runs.
- Per‑turn artifacts under `runs/<run_id>/conversations/<conversation_id>/turn_XXX.json`.
- Aggregated results in `runs/<run_id>/results.json` and `.csv`.
- Coverage CSVs via the Dataset Generator page: summary, heatmap, and per-turn exports.

---

## Data formats

- Dataset (.dataset.json)
  - Fields: dataset_id, version, metadata { domain, difficulty, tags? }, conversations [ { conversation_id, turns: [{ role, text }] } ]
- Golden (.golden.json)
  - Fields: dataset_id, version, entries [ { conversation_id, turns: [{ turn_index, expected { variants: string[] } }], final_outcome, constraints? } ]
- Run results (results.json)
  - Summary per conversation with per‑turn metrics and overall pass/fail.

Example files are in `datasets/demo.dataset.json` and `datasets/demo.golden.json`.

Run results (snippet):
```json
{
  "run_id": "demo-1.0.0-ollama-llama3.2-latest-abcdef12",
  "dataset_id": "demo",
  "model_spec": "ollama:llama3.2:latest",
  "conversations": [
    {
      "conversation_id": "conv1",
      "turns": [
        {
          "turn_index": 2,
          "metrics": {
            "exact": { "metric": "exact", "pass": false },
            "semantic": { "metric": "semantic", "pass": true, "score_max": 0.86 },
            "adherence": { "metric": "adherence", "pass": true },
            "hallucination": { "metric": "hallucination", "pass": true },
            "consistency": { "metric": "consistency", "pass": true }
          }
        }
      ],
      "summary": { "conversation_pass": true, "weighted_pass_rate": 0.92 }
    }
  ]
}
```

---

## Contributing

- See CONTRIBUTING.md for coding standards and tests. For governance/versioning of coverage rules, see `docs/GOVERNANCE.md`.
- License: GPLv3 (see LICENSE).

---

## Where to get help

- Open an issue in the repository.
- Or ask in your team chat with a link to this guide.
