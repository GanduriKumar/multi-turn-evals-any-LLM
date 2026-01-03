from __future__ import annotations

from fastapi.testclient import TestClient

from eval_server.__main__ import create_app


def test_get_conversation_with_goldens_ok():
    app = create_app()
    client = TestClient(app)

    # The example dataset id equals the stem, e.g., conversation_001
    # Derive it from the listing to be robust
    r = client.get('/api/v1/datasets/')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list) and data
    ds = data[0]
    ds_id = ds['id']
    conv_name = ds['name']  # should equal conversation_id inside conversation file

    r2 = client.get(f"/api/v1/datasets/{ds_id}/conversations/{conv_name}")
    assert r2.status_code == 200
    payload = r2.json()
    assert payload['dataset_id'] == ds_id
    assert payload['conversation_id'] == conv_name
    assert 'conversation' in payload and 'golden' in payload
    assert isinstance(payload['golden'].get('expectations', []), list)


def test_get_conversation_not_found():
    app = create_app()
    client = TestClient(app)

    # pick a dataset id
    r = client.get('/api/v1/datasets/')
    assert r.status_code == 200
    data = r.json()
    ds_id = data[0]['id'] if data else 'conversation_001'

    r2 = client.get(f"/api/v1/datasets/{ds_id}/conversations/does-not-exist")
    assert r2.status_code == 404
    assert 'conversation not found' in r2.text
