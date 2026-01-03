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


def _find_run_dir(run_id: str) -> Path:
    runs = Path('runs')
    for p in runs.iterdir():
        if p.is_dir() and run_id in p.name:
            return p
    raise AssertionError('run directory not found')


essential = ['results', 'summary', 'csv', 'html', 'markdown', 'raw', 'normalized', 'turn_scores', 'progress']


def test_artifacts_download(tmp_path: Path):
    app = create_app()
    client = TestClient(app)
    repo_root = Path(__file__).resolve().parents[2]

    # Start run
    r = client.post('/api/v1/runs/', json=make_payload(repo_root))
    assert r.status_code == 200
    run_id = r.json()['run_id']

    # Wait until completed
    import time
    for _ in range(80):
        time.sleep(0.1)
        pr = client.get(f'/api/v1/runs/{run_id}/progress')
        assert pr.status_code == 200
        if pr.json().get('overall_status') in ('completed', 'cancelled'):
            break

    run_dir = _find_run_dir(run_id)

    # 1) results.json
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'results'})
    assert res.status_code == 200
    on_disk = (run_dir / 'results.json').read_bytes()
    assert res.content == on_disk

    # 2) summary.json
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'summary'})
    assert res.status_code == 200
    on_disk = (run_dir / 'summary.json').read_bytes()
    assert res.content == on_disk

    # 3) csv
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'csv'})
    assert res.status_code == 200
    csv_path = (run_dir / 'results.csv')
    assert csv_path.exists()
    assert res.content == csv_path.read_bytes()

    # 4) html
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'html'})
    assert res.status_code == 200
    html_path = (run_dir / 'report.html')
    assert html_path.exists()
    assert res.content == html_path.read_bytes()

    # 5) markdown
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'markdown'})
    assert res.status_code == 200
    md_path = (run_dir / 'report.md')
    assert md_path.exists()
    assert res.content == md_path.read_bytes()

    # 6) multiple -> zip
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params=[('artifact', 'results'), ('artifact', 'csv')])
    assert res.status_code == 200
    assert res.headers.get('content-type') == 'application/zip'

    # 7) raw
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'raw'})
    assert res.status_code == 200
    assert res.content == (run_dir / 'raw_outputs.jsonl').read_bytes()

    # 8) normalized
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'normalized'})
    assert res.status_code == 200
    assert res.content == (run_dir / 'normalized.jsonl').read_bytes()

    # 9) turn_scores
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'turn_scores'})
    assert res.status_code == 200
    assert res.content == (run_dir / 'scores' / 'turn_scores.jsonl').read_bytes()

    # 10) progress
    res = client.get(f'/api/v1/runs/{run_id}/artifacts', params={'artifact': 'progress'})
    assert res.status_code == 200
    assert res.content == (run_dir / 'logs' / 'progress.jsonl').read_bytes()
