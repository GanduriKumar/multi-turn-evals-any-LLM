from __future__ import annotations

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


def test_conversation_metrics_endpoint(tmp_path: Path):
    app = create_app()
    client = TestClient(app)
    repo_root = Path(__file__).resolve().parents[2]

    # Start run
    r = client.post('/api/v1/runs/', json=make_payload(repo_root))
    assert r.status_code == 200
    run_id = r.json()['run_id']

    # Wait until results available
    # Poll progress until done
    import time
    for _ in range(60):
        time.sleep(0.1)
        pr = client.get(f'/api/v1/runs/{run_id}/progress')
        assert pr.status_code == 200
        status = pr.json().get('overall_status')
        if status in ('completed', 'cancelled'):
            break
    # Discover conversation_id from dataset file used
    conv_path = repo_root / 'configs' / 'datasets' / 'examples' / 'conversation_001.json'
    import json
    with conv_path.open('r', encoding='utf-8') as f:
        conversation_id = str(json.load(f).get('conversation_id'))

    # Hit new endpoint (no filter)
    res = client.get(f'/api/v1/runs/{run_id}/conversations/{conversation_id}')
    assert res.status_code == 200, res.text
    body = res.json()
    assert body['run_id'] == run_id
    assert body['conversation_id'] == conversation_id
    assert isinstance(body['results'], list) and len(body['results']) >= 1

    # Validate structure against stored results.json
    # Read results.json directly
    import os, json
    runs_dir = Path('runs')
    found = None
    for p in runs_dir.iterdir():
        if p.is_dir() and run_id in p.name:
            found = p
            break
    assert found is not None
    rjson = json.loads((found / 'results.json').read_text(encoding='utf-8'))

    # Filter ref entries
    ref_entries = [e for e in (rjson.get('results') or []) if str(e.get('conversation_id')) == conversation_id]
    assert len(ref_entries) >= 1

    # Compare each entry for model
    # We only check keys presence and equality for turns length and weighted scores mapping
    by_model = {e['model_name']: e for e in body['results']}
    ref_by_model = {e['model_name']: e for e in ref_entries}
    for model, entry in by_model.items():
        assert model in ref_by_model
        ref = ref_by_model[model]
        assert entry['aggregate']['score'] == ref['aggregate']['score']
        assert entry['aggregate']['passed'] == ref['aggregate']['passed']
        # turns length
        assert len(entry['turns']) == len(ref['turns'])
        # spot check first turn metrics map and weighted score
        if entry['turns']:
            t0 = entry['turns'][0]
            r0 = ref['turns'][0]
            assert set(t0['metrics'].keys()) == set(r0['metrics'].keys())
            assert t0['weighted_score'] == r0['weighted_score']
        # thresholds attached
        thr = entry.get('thresholds')
        assert thr is None or isinstance(thr, dict)

    # Hit with model filter
    model = next(iter(by_model.keys()))
    res2 = client.get(f'/api/v1/runs/{run_id}/conversations/{conversation_id}', params={'model_name': model})
    assert res2.status_code == 200
    body2 = res2.json()
    assert len(body2['results']) == 1
    assert body2['results'][0]['model_name'] == model
