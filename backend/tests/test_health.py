from fastapi.testclient import TestClient
from app import app

def test_health():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"

def test_version():
    client = TestClient(app)
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert "version" in body
    assert "semantic_threshold" in body
