from __future__ import annotations

import os
from fastapi.testclient import TestClient

from eval_server.__main__ import create_app
from eval_server.settings import load_settings


def test_missing_required_secret_raises(monkeypatch):
    # Ensure secret is not set
    monkeypatch.delenv('EVAL_SERVER_SECRET_KEY', raising=False)
    try:
        load_settings()
        assert False, 'Expected RuntimeError due to missing EVAL_SERVER_SECRET_KEY'
    except RuntimeError as e:
        assert 'EVAL_SERVER_SECRET_KEY' in str(e)


def test_app_can_start_when_secret_present(monkeypatch):
    monkeypatch.setenv('EVAL_SERVER_SECRET_KEY', 'test-secret')
    app = create_app()
    client = TestClient(app)
    r = client.get('/health')
    assert r.status_code == 200


def test_no_secrets_in_results_or_datasets(tmp_path, monkeypatch):
    # Set required secret
    monkeypatch.setenv('EVAL_SERVER_SECRET_KEY', 'test-secret')

    # Spot check example dataset and ensure it doesn't contain known env var names
    import json
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    conv = repo_root / 'configs' / 'datasets' / 'examples' / 'conversation_001.json'
    data = json.loads(conv.read_text(encoding='utf-8'))
    dump = json.dumps(data)
    assert 'API_KEY' not in dump and 'SECRET' not in dump and 'TOKEN' not in dump

    # Also ensure secrets are not written into results.json after a run
    from eval_server.__main__ import create_app as _create
    app = _create()
    client = TestClient(app)

    payload = {
        'version': '1.0.0',
        'datasets': [
            {'id': 'conv001', 'conversation': conv.as_posix(), 'golden': (repo_root / 'configs' / 'datasets' / 'examples' / 'conversation_001.golden.yaml').as_posix()},
        ],
        'models': [
            {'name': 'dummy', 'provider': 'dummy', 'model': 'dummy'},
        ],
        'concurrency': {'max_workers': 1},
    }

    r = client.post('/api/v1/runs/', json=payload)
    assert r.status_code == 200
    run_id = r.json()['run_id']

    import time
    for _ in range(80):
        time.sleep(0.05)
        pr = client.get(f'/api/v1/runs/{run_id}/progress')
        if pr.json().get('overall_status') in ('completed', 'cancelled'):
            break

    # Locate results.json
    from pathlib import Path as _P
    runs = _P('runs')
    rd = None
    for p in runs.iterdir():
        if p.is_dir() and run_id in p.name:
            rd = p; break
    assert rd is not None
    results_text = (rd / 'results.json').read_text(encoding='utf-8')
    # Ensure no environment variable names are present
    assert 'EVAL_SERVER_SECRET_KEY' not in results_text
    assert 'OPENAI_API_KEY' not in results_text
    assert 'AZURE_OPENAI_API_KEY' not in results_text
    assert 'ANTHROPIC_API_KEY' not in results_text
    assert 'GOOGLE_AI_API_KEY' not in results_text
    assert 'HUGGINGFACE_API_TOKEN' not in results_text
