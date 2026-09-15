import pytest
from pathlib import Path
from orchestrator.models import AgentSolution
from orchestrator.recovery import RecoveryManager


def make_sol(agent_id: str, status: str = "success") -> AgentSolution:
    return AgentSolution(
        agent_id=agent_id,
        persona=f"Persona {agent_id}",
        status=status,
        solution="test solution",
        rationale="test rationale",
        risks=[],
        improvements=[],
        artifacts="",
        raw="raw",
        error="timeout" if status == "failed" else None,
    )


def test_save_and_load_checkpoint(tmp_path):
    mgr = RecoveryManager(checkpoint_base_dir=tmp_path)
    solutions = [make_sol(f"agent_{i}") for i in range(1, 11)]
    solutions[5].status = "failed"
    solutions[5].error = "timeout"

    path = mgr.save_checkpoint("test_project", solutions, task="build login page")
    assert path.exists()

    loaded = mgr.load_checkpoint("test_project")
    assert loaded is not None
    assert loaded["task"] == "build login page"
    assert len(loaded["solutions"]) == 10
    assert "agent_6" in loaded["failed_agents"]


def test_cleanup_checkpoint(tmp_path):
    mgr = RecoveryManager(checkpoint_base_dir=tmp_path)
    solutions = [make_sol(f"agent_{i}") for i in range(1, 11)]
    mgr.save_checkpoint("test_project", solutions, task="test task")
    mgr.cleanup_checkpoint("test_project")
    assert mgr.load_checkpoint("test_project") is None


def test_get_failed_agents():
    mgr = RecoveryManager()
    solutions = [make_sol(f"agent_{i}") for i in range(1, 11)]
    solutions[2].status = "failed"
    solutions[7].status = "failed"
    failed = mgr.get_failed_agents(solutions)
    assert len(failed) == 2
    assert failed[0].agent_id == "agent_3"
    assert failed[1].agent_id == "agent_8"


def test_get_successful_agents():
    mgr = RecoveryManager()
    solutions = [make_sol(f"agent_{i}") for i in range(1, 11)]
    solutions[2].status = "failed"
    successful = mgr.get_successful_agents(solutions)
    assert len(successful) == 9


def test_load_checkpoint_no_checkpoint(tmp_path):
    mgr = RecoveryManager(checkpoint_base_dir=tmp_path)
    result = mgr.load_checkpoint("nonexistent_project")
    assert result is None
