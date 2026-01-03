from __future__ import annotations

from fastapi.testclient import TestClient

from eval_server.__main__ import create_app


def test_list_datasets_includes_metadata():
    app = create_app()
    client = TestClient(app)

    r = client.get('/api/v1/datasets/?page=1&page_size=50')
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    # Expect at least the example dataset
    found = None
    for item in data:
        if item.get('id') == 'conversation_001':
            found = item
            break
        # also accept conv-001 name
        if item.get('name') == 'conv-001':
            found = item
            break
    assert found is not None
    assert 'conversation_version' in found
    assert 'golden_version' in found
    assert isinstance(found.get('tags', []), list)
    # difficulty is optional but if present should be a string
    if found.get('difficulty') is not None:
        assert isinstance(found['difficulty'], str)


def test_list_datasets_pagination():
    app = create_app()
    client = TestClient(app)

    r1 = client.get('/api/v1/datasets/?page=1&page_size=1')
    r2 = client.get('/api/v1/datasets/?page=2&page_size=1')
    assert r1.status_code == 200 and r2.status_code == 200
    d1 = r1.json()
    d2 = r2.json()
    # page_size=1 implies each page returns at most one item
    assert len(d1) <= 1 and len(d2) <= 1
    if d1 and d2:
        assert d1[0] != d2[0]
