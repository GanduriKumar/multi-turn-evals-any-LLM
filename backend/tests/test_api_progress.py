from __future__ import annotations

import time
from pathlib import Path
from fastapi.testclient import TestClient

from eval_server.__main__ import create_app


def make_run_payload(repo_root: Path) -> dict:
    conv = repo_root / 'configs' / 'datasets' / 'examples' / 'conversation_001.json'
    gold = repo_root / 'configs' / 'datasets' / 'examples' / 'conversation_001.golden.yaml'
    return {
        'version': '1.0.0',
        'datasets': [
            {'id': 'conv001', 'conversation': conv.as_posix(), 'golden': gold.as_posix()},
        ],
        'models': [
            {'name': 'dummy', 'provider': 'dummy', 'model': 'dummy'},
        ],
        'concurrency': {'max_workers': 1},
    }


def test_progress_polling_updates():
    app = create_app()
    client = TestClient(app)
    repo_root = Path(__file__).resolve().parents[2]

    # Start run
    r = client.post('/api/v1/runs/', json=make_run_payload(repo_root))
    assert r.status_code == 200
    run_id = r.json()['run_id']

    # Poll progress until done or timeout
    done = False
    for _ in range(50):  # up to ~5s
        time.sleep(0.1)
        pr = client.get(f'/api/v1/runs/{run_id}/progress')
        assert pr.status_code == 200
        body = pr.json()
        assert body['run_id'] == run_id
        assert 'overall_status' in body
        if body['conversations']:
            # progress should be in [0,100]
            p = body['conversations'][0]['progress']
            assert 0.0 <= float(p) <= 100.0
        if body['overall_status'] in ('completed', 'cancelled'):
            done = True
            break
    assert done
