from __future__ import annotations

import json
import time
from pathlib import Path
from fastapi.testclient import TestClient

from eval_server.__main__ import create_app


def make_payload(repo_root: Path) -> dict:
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


def _find_run_dir(run_id: str) -> Path:
    runs = Path('runs')
    for p in runs.iterdir():
        if p.is_dir() and run_id in p.name:
            return p
    raise AssertionError('run directory not found')


def test_submit_run_feedback_valid(tmp_path: Path):
    app = create_app()
    client = TestClient(app)
    repo_root = Path(__file__).resolve().parents[2]

    # Start run and wait for completion
    r = client.post('/api/v1/runs/', json=make_payload(repo_root))
    assert r.status_code == 200
    run_id = r.json()['run_id']

    for _ in range(80):
        time.sleep(0.1)
        pr = client.get(f'/api/v1/runs/{run_id}/progress')
        assert pr.status_code == 200
        if pr.json().get('overall_status') in ('completed', 'cancelled'):
            break

    run_dir = _find_run_dir(run_id)
    results = json.loads((run_dir / 'results.json').read_text(encoding='utf-8'))
    # Grab a valid reference
    ref = results['results'][0]
    ds = ref['dataset_id']; cid = str(ref['conversation_id']); model = ref['model_name']; tid = str(ref['turns'][0]['turn_id'])

    payload = {
        'feedback': [
            {
                'dataset_id': ds,
                'conversation_id': cid,
                'model_name': model,
                'turn_id': tid,
                'rating': 4.0,
                'notes': 'Looks good',
                'override_pass': True,
                'override_score': 0.9,
            }
        ]
    }

    res = client.post(f'/api/v1/runs/{run_id}/feedback', json=payload, headers={'X-User': 'tester'})
    assert res.status_code == 200, res.text
    body = res.json()
    assert body['run_id'] == run_id
    assert body['total_records'] == 1

    content = json.loads((_find_run_dir(run_id) / 'annotations.json').read_text(encoding='utf-8'))
    assert content['run_id'] == run_id
    assert len(content['annotations']) >= 1
    last = content['annotations'][-1]
    assert last['dataset_id'] == ds and str(last['conversation_id']) == cid and last['model_name'] == model and str(last['turn_id']) == tid


def test_submit_run_feedback_invalid_references(tmp_path: Path):
    app = create_app()
    client = TestClient(app)
    repo_root = Path(__file__).resolve().parents[2]

    # Start run and wait for completion
    r = client.post('/api/v1/runs/', json=make_payload(repo_root))
    assert r.status_code == 200
    run_id = r.json()['run_id']

    for _ in range(80):
        time.sleep(0.1)
        pr = client.get(f'/api/v1/runs/{run_id}/progress')
        assert pr.status_code == 200
        if pr.json().get('overall_status') in ('completed', 'cancelled'):
            break

    # Submit invalid reference (wrong identifiers)
    bad_payload = {
        'feedback': [
            {
                'dataset_id': 'dsX',
                'conversation_id': 'cX',
                'model_name': 'mX',
                'turn_id': '999',
                'rating': 3.0
            }
        ]
    }
    res = client.post(f'/api/v1/runs/{run_id}/feedback', json=bad_payload)
    assert res.status_code == 400
    err = res.json()
    assert 'errors' in err['detail']

    # Validation: rating beyond range
    bad_payload2 = {
        'feedback': [
            {
                'dataset_id': 'ds', 'conversation_id': 'c', 'model_name': 'm', 'turn_id': '1', 'rating': 6.0
            }
        ]
    }
    res2 = client.post(f'/api/v1/runs/{run_id}/feedback', json=bad_payload2)
    assert res2.status_code == 422
