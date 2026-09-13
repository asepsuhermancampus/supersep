import tempfile
from pathlib import Path
import pytest
from orchestrator.triage import WorkspaceDetector, ProjectMemory

def test_detect_project_extracts_folder_name():
    path = Path("C:/Users/asep/Projects/HariKita - Web App/subfolder")
    detector = WorkspaceDetector()
    project_info = detector.detect(path)
    assert project_info["name"] == "subfolder"
    assert project_info["safe_name"] == "subfolder"

def test_detect_project_custom():
    path = Path("C:/Users/asep/Projects/HariKita - Web App")
    detector = WorkspaceDetector()
    project_info = detector.detect(path)
    assert project_info["name"] == "HariKita - Web App"
    assert project_info["safe_name"] == "HariKita-Web-App"

def test_project_memory_create_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(base_dir=Path(tmpdir))
        memory.save_context("Test-Project", {"tech_stack": ["Next.js", "Tailwind"]})
        loaded = memory.load("Test-Project")
        assert loaded["context"]["tech_stack"] == ["Next.js", "Tailwind"]

def test_project_memory_append_decision():
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(base_dir=Path(tmpdir))
        memory.append_decision("Test-Project", "Use cookie-based auth")
        loaded = memory.load("Test-Project")
        assert "Use cookie-based auth" in loaded["decisions"]
