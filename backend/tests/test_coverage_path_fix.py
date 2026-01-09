"""Test to verify datasets are saved under datasets/commerce/ folder when using flat mode."""
import json
import pytest
import httpx
from pathlib import Path

from backend.app import app
from backend.dataset_repo import DatasetRepository
from backend.orchestrator import Orchestrator


@pytest.mark.anyio
async def test_coverage_generate_saves_to_commerce_folder(tmp_path):
    """Verify that with flat mode and base='commerce', files are saved to datasets/commerce/"""
    # Setup temp orchestrator with custom datasets dir
    orch = Orchestrator(datasets_dir=tmp_path, runs_root=tmp_path / "runs")
    old_orch = app.state.orch
    app.state.orch = orch
    
    try:
        # Ensure coverage.json has the correct settings
        from backend.coverage_config import CoverageConfig
        cfg = CoverageConfig()
        cfg_path = cfg.root / "coverage.json"
        
        # Read current config
        current = json.loads(cfg_path.read_text(encoding='utf-8'))
        
        # Verify dataset_paths settings
        assert 'dataset_paths' in current
        assert current['dataset_paths']['mode'] == 'flat'
        assert current['dataset_paths']['base'] == 'commerce'
        
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/coverage/generate", json={
                "combined": True,
                "dry_run": False,
                "save": True,
                "overwrite": True,
                "version": "1.0.0",
                "domains": ["Orders & Returns"],
                "behaviors": ["Refund/Exchange/Cancellation"]
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["ok"] is True
            assert data["saved"] is True
            assert len(data["files"]) > 0
            
            # Verify files are in commerce subfolder
            commerce_dir = tmp_path / "commerce"
            assert commerce_dir.exists(), f"Expected commerce folder at {commerce_dir}"
            
            # Check that files exist in commerce folder
            dataset_files = list(commerce_dir.glob("*.dataset.json"))
            golden_files = list(commerce_dir.glob("*.golden.json"))
            
            assert len(dataset_files) > 0, f"No dataset files found in {commerce_dir}"
            assert len(golden_files) > 0, f"No golden files found in {commerce_dir}"
            
            # Verify files are NOT directly under tmp_path (datasets root)
            root_dataset_files = list(tmp_path.glob("*.dataset.json"))
            assert len(root_dataset_files) == 0, "Dataset files should not be in root datasets folder"
    finally:
        app.state.orch = old_orch


@pytest.mark.anyio
async def test_coverage_generate_hierarchical_mode(tmp_path):
    """Verify hierarchical mode creates nested folder structure."""
    # Setup temp orchestrator
    orch = Orchestrator(datasets_dir=tmp_path, runs_root=tmp_path / "runs")
    old_orch = app.state.orch
    app.state.orch = orch
    
    # Temporarily modify coverage.json to use hierarchical mode
    from backend.coverage_config import CoverageConfig
    cfg = CoverageConfig()
    cfg_path = cfg.root / "coverage.json"
    current = json.loads(cfg_path.read_text(encoding='utf-8'))
    original_mode = current['dataset_paths']['mode']
    
    try:
        # Set to hierarchical
        current['dataset_paths']['mode'] = 'hierarchical'
        cfg_path.write_text(json.dumps(current, indent=2), encoding='utf-8')
        
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as ac:
            resp = await ac.post("/coverage/generate", json={
                "combined": False,
                "dry_run": False,
                "save": True,
                "overwrite": True,
                "version": "1.0.0",
                "domains": ["Orders & Returns"],
                "behaviors": ["Refund/Exchange/Cancellation"]
            })
            assert resp.status_code == 200
            data = resp.json()
            assert data["saved"] is True
            
            # Verify hierarchical structure: datasets/commerce/<behavior>/<version>/
            behavior_folder = tmp_path / "commerce" / "Refund/Exchange/Cancellation" / "1.0.0"
            # Note: Path may have different separators; check if folder exists
            found_version_folders = list((tmp_path / "commerce").rglob("1.0.0"))
            assert len(found_version_folders) > 0, "Expected version folder in hierarchical structure"
            
    finally:
        # Restore original mode
        current['dataset_paths']['mode'] = original_mode
        cfg_path.write_text(json.dumps(current, indent=2), encoding='utf-8')
        app.state.orch = old_orch
