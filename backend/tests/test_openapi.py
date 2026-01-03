from __future__ import annotations

from fastapi.testclient import TestClient
from eval_server.__main__ import create_app


def test_openapi_docs_exposed():
    app = create_app()
    client = TestClient(app)

    # Swagger UI should be available
    r_ui = client.get('/docs')
    assert r_ui.status_code == 200

    # OpenAPI JSON should exist
    r = client.get('/openapi.json')
    assert r.status_code == 200
    spec = r.json()

    assert spec['openapi'].startswith('3.')
    assert spec['info']['title'] == 'Eval Server'

    # Ensure key paths are present and have operations
    required_paths = [
        '/api/v1/datasets/',
        '/api/v1/datasets/{dataset_id}',
        '/api/v1/datasets/{dataset_id}/conversations/{conversation_id}',
        '/api/v1/runs/',
        '/api/v1/runs/{run_id}/progress',
        '/api/v1/runs/{run_id}/conversations/{conversation_id}',
        '/api/v1/runs/{run_id}/artifacts',
        '/api/v1/runs/compare',
        '/api/v1/jobs/',
        '/api/v1/jobs/{job_id}',
        '/api/v1/jobs/{job_id}/cancel',
        '/api/v1/results/{run_id}/summary',
        '/api/v1/results/{run_id}/results',
        '/api/v1/reports/html',
        '/api/v1/reports/markdown',
        '/api/v1/reports/compare',
    ]

    for p in required_paths:
        assert p in spec['paths'], f'missing path {p}'
        ops = spec['paths'][p]
        assert any(m in ops for m in ['get', 'post']), f'no operations for {p}'

    # Check that start_run has requestBody schema and response schema
    runs_post = spec['paths']['/api/v1/runs/']['post']
    assert 'requestBody' in runs_post and 'content' in runs_post['requestBody']
    assert 'responses' in runs_post and '200' in runs_post['responses']

    # Check that conversation metrics endpoint has documented response
    conv_get = spec['paths']['/api/v1/runs/{run_id}/conversations/{conversation_id}']['get']
    assert 'responses' in conv_get and '200' in conv_get['responses']
