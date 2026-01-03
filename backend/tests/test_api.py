from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from eval_server.__main__ import create_app


@pytest.fixture(scope="module")
def client() -> TestClient:
    app = create_app()
    return TestClient(app)


def test_datasets_list_and_get(client: TestClient):
    r = client.get("/api/v1/datasets/")
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data, list)
    if data:
        dsid = data[0]["id"]
        r2 = client.get(f"/api/v1/datasets/{dsid}")
        assert r2.status_code == 200
        one = r2.json()
        assert one["id"] == dsid


def test_jobs_crud(client: TestClient):
    r = client.post("/api/v1/jobs/")
    assert r.status_code == 200
    jid = r.json()["job_id"]
    assert jid

    r = client.get(f"/api/v1/jobs/{jid}")
    assert r.status_code == 200

    r = client.get("/api/v1/jobs/")
    assert r.status_code == 200

    r = client.post(f"/api/v1/jobs/{jid}/cancel")
    assert r.status_code == 200

    r = client.get("/api/v1/jobs/does-not-exist")
    assert r.status_code == 404


def test_feedback_submit(client: TestClient, tmp_path: Path):
    # Use a dummy run_id; backend falls back to runs/<run_id>
    payload = {
        "run_id": "test-run-123",
        "feedback": [
            {
                "dataset_id": "ds-1",
                "conversation_id": "conv-1",
                "model_name": "m-1",
                "turn_id": "t1",
                "rating": 4.5,
                "notes": "ok",
                "override_pass": True,
                "override_score": 0.9,
            }
        ],
    }
    r = client.post("/api/v1/feedback/", json=payload, headers={"X-User": "tester"})
    assert r.status_code == 200
    data = r.json()
    assert data["run_id"] == payload["run_id"]
    assert data["total_records"] == 1


def test_results_endpoints_missing(client: TestClient):
    r = client.get("/api/v1/results/no-such-run/summary")
    assert r.status_code in (404, 400)
    r = client.get("/api/v1/results/no-such-run/results")
    assert r.status_code in (404, 400)


def test_reports_error_paths(client: TestClient, tmp_path: Path):
    r = client.post("/api/v1/reports/html", params={"results_path": str(tmp_path / "missing.json")})
    assert r.status_code == 404
    r = client.post("/api/v1/reports/markdown", params={"results_path": str(tmp_path / "missing.json")})
    assert r.status_code == 404
    r = client.post("/api/v1/reports/compare", params={"results_path": str(tmp_path / "a.json"), "baseline_results_path": str(tmp_path / "b.json")})
    assert r.status_code == 404


def test_runs_start_invalid(client: TestClient, tmp_path: Path):
    r = client.post("/api/v1/runs/start", json={"config_path": str(tmp_path / "missing.yaml")})
    assert r.status_code == 404
