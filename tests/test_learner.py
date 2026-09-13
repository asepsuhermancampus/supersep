import tempfile
from pathlib import Path
import pytest
from orchestrator.learner import KnowledgeDistiller
from orchestrator.triage import ProjectMemory

def test_apply_learnings_writes_to_project_and_global():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        memory = ProjectMemory(base_dir=base / "memory")
        agents_dir = base / "agents"
        agents_dir.mkdir()
        (agents_dir / "agent3.md").write_text("# Agent 3\nInitial prompt\n", encoding="utf-8")

        distiller = KnowledgeDistiller(memory=memory, agents_dir=agents_dir)
        
        # Test appending to project memory
        approvals = [
            {"scope": "project", "target": "Test-Project", "rule": "Use Redis for cache"},
            {"scope": "global", "target": "agent_3", "rule": "Always specify DB connection pool"},
        ]
        distiller.apply(approvals)
        
        loaded = memory.load("Test-Project")
        assert "Use Redis for cache" in loaded["decisions"]

        agent3_content = (agents_dir / "agent3.md").read_text(encoding="utf-8")
        assert "Always specify DB connection pool" in agent3_content
