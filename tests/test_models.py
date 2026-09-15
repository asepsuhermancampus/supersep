from orchestrator.models import AgentSolution, AgentCritique


def test_agent_solution_success_defaults():
    sol = AgentSolution(
        agent_id="agent_1",
        persona="The Conservative Guardian",
        status="success",
        solution="test solution",
        rationale="test rationale",
        risks=["risk1"],
        improvements=["improvement1"],
        artifacts="test code",
        raw="raw response",
    )
    assert sol.error is None
    assert sol.status == "success"
    assert sol.agent_id == "agent_1"
    assert sol.risks == ["risk1"]


def test_agent_solution_failed():
    sol = AgentSolution(
        agent_id="agent_5",
        persona="The Perfectionist",
        status="failed",
        solution="",
        rationale="",
        risks=[],
        improvements=[],
        artifacts="",
        raw="",
        error="TimeoutError: request timed out after 300s",
    )
    assert sol.status == "failed"
    assert sol.error is not None
    assert "TimeoutError" in sol.error


def test_agent_solution_substituted():
    sol = AgentSolution(
        agent_id="agent_3",
        persona="The Adversarial Skeptic",
        status="substituted",
        solution="substituted solution",
        rationale="covered by agent_7",
        risks=[],
        improvements=[],
        artifacts="",
        raw="raw",
    )
    assert sol.status == "substituted"
    assert sol.error is None


def test_agent_critique_defaults():
    crit = AgentCritique(
        agent_id="agent_3",
        persona="The Adversarial Skeptic",
        status="success",
        strengths_to_adopt=[{"from": "agent_1", "insight": "good point"}],
        weaknesses_found=[{"in": "agent_2", "issue": "missing validation", "fix": "add zod"}],
        improvement_patches=["patch 1"],
        conflicts_to_resolve=[],
        raw="raw response",
    )
    assert crit.error is None
    assert len(crit.strengths_to_adopt) == 1
    assert len(crit.weaknesses_found) == 1
    assert len(crit.improvement_patches) == 1
