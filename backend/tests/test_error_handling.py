from __future__ import annotations

from pathlib import Path
from fastapi.testclient import TestClient

from eval_server.__main__ import create_app


def test_not_found_errors_are_consistent():
    app = create_app()
    client = TestClient(app)

    # Non-existent dataset
    r = client.get('/api/v1/datasets/nonexistent')
    assert r.status_code == 404
    body = r.json()
    assert body['error']['code'] == 'not_found'
    assert body['status'] == 404

    # Non-existent run
    r = client.get('/api/v1/results/does-not-exist/results')
    assert r.status_code == 404
    body = r.json()
    assert body['error']['code'] == 'not_found'


def test_validation_errors_are_consistent(tmp_path: Path):
    app = create_app()
    client = TestClient(app)

    # Missing required fields in start_run
    payload = {'version': '1.0.0', 'datasets': [], 'models': []}
    r = client.post('/api/v1/runs/', json=payload)
    assert r.status_code == 400
    body = r.json()
    assert body['error']['code'] == 'bad_request'

    # Pydantic validation error: wrong type
    r2 = client.get('/api/v1/datasets/', params={'page': 0})  # page must be >= 1
    assert r2.status_code == 422
    spec = r2.json()
    assert spec['error']['code'] == 'validation_error'


essential_paths = [
    '/api/v1/datasets/',
    '/api/v1/runs/',
    '/api/v1/runs/compare',
]


def test_internal_error_is_masked(monkeypatch):
    app = create_app()
    # Allow server to return the error response instead of re-raising exceptions
    client = TestClient(app, raise_server_exceptions=False)

    # Monkeypatch datasets list to raise a raw exception
    from eval_server.api import datasets as dsmod

    def boom(*args, **kwargs):
        raise RuntimeError('boom')

    monkeypatch.setattr(dsmod, '_list_example_datasets', boom)
    r = client.get('/api/v1/datasets/')
    assert r.status_code == 500
    body = r.json()
    assert body['error']['code'] == 'internal_error'
    assert body['error']['message'] == 'an unexpected error occurred'
    assert 'trace_id' in body
