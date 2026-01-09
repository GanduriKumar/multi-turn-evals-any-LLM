import json
import pytest
import httpx

from backend.app import app


@pytest.mark.anyio
async def test_build_combined_array_dry_run():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/coverage/generate", json={
            "combined": True,
            "dry_run": True,
            "save": False,
            "version": "1.0.0",
            "as_array": True
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True
        assert data["saved"] is False
        assert isinstance(data["count"], int) and data["count"] > 0
        cbr = data.get("counts_by_risk") or {}
        assert set(cbr.keys()) <= {"high","medium","low"}


@pytest.mark.anyio
async def test_save_combined_array(tmp_path):
    # Point datasets root to temp
    from backend.orchestrator import Orchestrator
    orch = Orchestrator(datasets_dir=tmp_path / 'datasets', runs_root=tmp_path / 'runs')
    from backend.app import app as fastapi_app
    fastapi_app.state.orch = orch

    transport = httpx.ASGITransport(app=fastapi_app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.post("/coverage/generate", json={
            "combined": True,
            "dry_run": False,
            "save": True,
            "overwrite": True,
            "version": "1.0.0",
            "as_array": True
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["ok"] is True and data["saved"] is True
        assert str(tmp_path / 'datasets' / 'arrays') in data["file"]
