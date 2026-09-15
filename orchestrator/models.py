"""
orchestrator/models.py — Shared dataclasses for SuperSep v3.0 Omni Protocol.
Replaces raw dict[str, Any] with typed, IDE-friendly dataclasses.
Used by: agent_runner.py, council.py, ensemble_code_stage.py, recovery.py
"""
from dataclasses import dataclass
from typing import Literal


@dataclass
class AgentSolution:
    """
    Output of a single agent in Round 1 (Full Parallel Solutions).

    Attributes:
        agent_id: Unique agent identifier e.g. 'agent_1'
        persona: Human-readable persona name e.g. 'The Conservative Guardian'
        status: 'success' | 'failed' | 'substituted'
        solution: The agent complete solution text
        rationale: Why the agent chose this approach
        risks: List of risks/concerns identified
        improvements: List of suggested improvements
        artifacts: Code, designs, or plans produced (task-type dependent)
        raw: Raw response string from the model (for debugging)
        error: Error message if status == 'failed', else None
    """
    agent_id: str
    persona: str
    status: Literal["success", "failed", "substituted"]
    solution: str
    rationale: str
    risks: list[str]
    improvements: list[str]
    artifacts: str
    raw: str
    error: str | None = None


@dataclass
class AgentCritique:
    """
    Output of a single agent in Round 2 (Cross-Agent Critique).

    Attributes:
        agent_id: Unique agent identifier
        persona: Human-readable persona name
        status: 'success' | 'failed'
        strengths_to_adopt: Insights from other agents worth incorporating
        weaknesses_found: Problems found in other agents solutions with fixes
        improvement_patches: Specific patches to apply to the final output
        conflicts_to_resolve: Contradictions between agent solutions with resolutions
        raw: Raw response string from the model
        error: Error message if status == 'failed', else None
    """
    agent_id: str
    persona: str
    status: Literal["success", "failed"]
    strengths_to_adopt: list[dict]
    weaknesses_found: list[dict]
    improvement_patches: list[str]
    conflicts_to_resolve: list[dict]
    raw: str
    error: str | None = None
