from __future__ import annotations

import time
from pathlib import Path
from fastapi.testclient import TestClient

from eval_server.__main__ import create_app


def make_payload(repo_root: Path, model_name: str, turn_pass: float | None = None) -> dict:
    conv = repo_root / 'configs' / 'datasets' / 'examples' / 'conversation_001.json'
    gold = repo_root / 'configs' / 'datasets' / 'examples' / 'conversation_001.golden.yaml'
    payload = {
        'version': '1.0.0',
        'datasets': [
            {'id': 'conv001', 'conversation': conv.as_posix(), 'golden': gold.as_posix()},
        ],
        'models': [
            {'name': model_name, 'provider': 'dummy', 'model': 'dummy'},
        ],
        'concurrency': {'max_workers': 1},
    }
    if turn_pass is not None:
        payload['thresholds'] = {'turn_pass': turn_pass}
    return payload


def _wait_done(client: TestClient, run_id: str):
    for _ in range(80):
        time.sleep(0.1)
        pr = client.get(f'/api/v1/runs/{run_id}/progress')
        assert pr.status_code == 200
        if pr.json().get('overall_status') in ('completed', 'cancelled'):
            return
    raise AssertionError('run did not complete')


def test_compare_runs_delta():
    app = create_app()
    client = TestClient(app)
    repo_root = Path(__file__).resolve().parents[2]

    # Baseline run
    r1 = client.post('/api/v1/runs/', json=make_payload(repo_root, model_name='mA'))
    assert r1.status_code == 200
    run_baseline = r1.json()['run_id']
    _wait_done(client, run_baseline)

    # Current run (same inputs; same scores expected, hence delta ~ 0)
    r2 = client.post('/api/v1/runs/', json=make_payload(repo_root, model_name='mB'))
    assert r2.status_code == 200
    run_current = r2.json()['run_id']
    _wait_done(client, run_current)

    # Compare
    cmp_res = client.get('/api/v1/runs/compare', params={'baseline': run_baseline, 'current': run_current})
    assert cmp_res.status_code == 200
    body = cmp_res.json()

    # Overall delta should be approximately zero (within floating tolerance)
    overall = body['summary']['overall']
    assert abs(float(overall['delta'])) < 1e-6

    # Per-dataset deltas should be zero as well
    for ds in body['per_dataset']:
        assert abs(float(ds['delta'])) < 1e-6

    # Metrics by dataset deltas should be zero too
    for row in body['metrics_by_dataset']:
        assert abs(float(row['delta'])) < 1e-6
