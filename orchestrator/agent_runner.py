"""
orchestrator/agent_runner.py — Round 1: Full Parallel Solutions (SuperSep v3.0)

Each of 10 omniscient agents produces a COMPLETE solution simultaneously.
Results are collected as AgentSolution dataclasses.
Failed agents return status='failed' — never raise exceptions to caller.
"""
import asyncio
import json
import os
import re
from pathlib import Path

from orchestrator.models import AgentSolution
from orchestrator.router import GeminiRouter

# Maps agent_id to (persona_name, agent_file_path)
AGENT_REGISTRY: list[tuple[str, str]] = [
    ("agent_1",  "agents/agent1.md"),
    ("agent_2",  "agents/agent2.md"),
    ("agent_3",  "agents/agent3.md"),
    ("agent_4",  "agents/agent4.md"),
    ("agent_5",  "agents/agent5.md"),
    ("agent_6",  "agents/agent6.md"),
    ("agent_7",  "agents/agent7.md"),
    ("agent_8",  "agents/agent8.md"),
    ("agent_9",  "agents/agent9.md"),
    ("agent_10", "agents/agent10.md"),
]

# Persona name lookup (from agent file header line 1: "# Agent N — Persona Name")
AGENT_PERSONA_NAMES: dict[str, str] = {
    "agent_1":  "The Conservative Guardian",
    "agent_2":  "The Innovator",
    "agent_3":  "The Adversarial Skeptic",
    "agent_4":  "The Pragmatist",
    "agent_5":  "The Perfectionist",
    "agent_6":  "The Scalability Architect",
    "agent_7":  "The DX Champion",
    "agent_8":  "The User Advocate",
    "agent_9":  "The Data Whisperer",
    "agent_10": "The Synthesis Master",
}

ROUND1_OUTPUT_FORMAT = """
Respond ONLY in JSON (no markdown fences, no extra text):
{
  "solution": "Your complete solution from your persona perspective...",
  "rationale": "Why you chose this specific approach...",
  "risks": ["Risk 1 with concrete scenario...", "Risk 2..."],
  "improvements": ["What could be even better with more time..."],
  "artifacts": "Key code snippets, designs, or implementation details..."
}"""

ROUND1_TASK_PREFIX = """\
## ROUND 1: FULL SOLUTION — OMNISCIENT COUNCIL PROTOCOL
You are participating in Round 1 of the SuperSep 10-agent Omniscient Council.
TASK TYPE: {task_type}

Your mission: Provide a COMPLETE, production-grade solution for the given task
from your unique cognitive persona. NOT a brief — your FULL expert answer.

TASK:
{task}

PROJECT CONTEXT:
{project_context}
{output_format}"""


class AgentRunner:
    """
    Manages Round 1 of the Omni Protocol: 10 agents produce full solutions in parallel.
    """

    def __init__(self, router: GeminiRouter):
        """Initialize with a shared GeminiRouter instance."""
        self.router = router
        self.agents = AGENT_REGISTRY
        self._timeout = float(os.getenv("AGENT_TIMEOUT_SECONDS", "300"))

    def load_agent_prompt(self, agent_file: str) -> str:
        """
        Load the agent persona prompt from its markdown file.

        Args:
            agent_file: Relative path to agent .md file

        Returns:
            File contents as string, or fallback prompt if file not found
        """
        path = Path(agent_file)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return f"You are a world-class full-stack engineer. Think carefully and provide complete, production-grade solutions."

    async def run_single_solution(
        self,
        agent_id: str,
        agent_file: str,
        task: str,
        task_type: str,
        project_context: str = "",
    ) -> AgentSolution:
        """
        Run a single agent for Round 1.

        Returns AgentSolution with status='failed' on any exception.
        NEVER raises — caller receives all 10 results regardless.

        Args:
            agent_id: e.g. 'agent_1'
            agent_file: Path to agent's .md persona file
            task: The user task string
            task_type: Detected task type e.g. 'brainstorm', 'coding'
            project_context: Optional project context string

        Returns:
            AgentSolution dataclass
        """
        persona = AGENT_PERSONA_NAMES.get(agent_id, agent_id)
        system_prompt = self.load_agent_prompt(agent_file)
        user_prompt = ROUND1_TASK_PREFIX.format(
            task_type=task_type,
            task=task,
            project_context=project_context or "(no prior context)",
            output_format=ROUND1_OUTPUT_FORMAT,
        )
        try:
            raw = await asyncio.wait_for(
                self.router.request(system_prompt=system_prompt, user_prompt=user_prompt),
                timeout=self._timeout,
            )
            parsed = self._parse_response(raw)
            print(f"[Runner] {agent_id} ({persona}): OK")
            return AgentSolution(
                agent_id=agent_id,
                persona=persona,
                status="success",
                solution=parsed.get("solution", raw),
                rationale=parsed.get("rationale", ""),
                risks=parsed.get("risks", []),
                improvements=parsed.get("improvements", []),
                artifacts=parsed.get("artifacts", ""),
                raw=raw,
            )
        except Exception as e:
            print(f"[Runner] {agent_id} ({persona}): FAILED — {type(e).__name__}: {e}")
            return AgentSolution(
                agent_id=agent_id,
                persona=persona,
                status="failed",
                solution="",
                rationale="",
                risks=[],
                improvements=[],
                artifacts="",
                raw="",
                error=f"{type(e).__name__}: {e}",
            )

    async def run_all_solutions(
        self,
        task: str,
        task_type: str = "mixed",
        project_context: str = "",
    ) -> list[AgentSolution]:
        """
        Round 1: Run all 10 agents simultaneously via asyncio.gather.

        Args:
            task: The user task string
            task_type: Task category for tailored prompts
            project_context: Optional project context

        Returns:
            List of 10 AgentSolution objects (some may have status='failed')
        """
        print(f"[Runner] ROUND 1: Launching {len(self.agents)} agents in parallel...")
        coroutines = [
            self.run_single_solution(
                agent_id=agent_id,
                agent_file=agent_file,
                task=task,
                task_type=task_type,
                project_context=project_context,
            )
            for agent_id, agent_file in self.agents
        ]
        solutions: list[AgentSolution] = await asyncio.gather(*coroutines)
        success_count = sum(1 for s in solutions if s.status == "success")
        failed_count = sum(1 for s in solutions if s.status == "failed")
        print(f"[Runner] Round 1 complete: {success_count} success, {failed_count} failed")
        return list(solutions)

    def _parse_response(self, raw: str) -> dict:
        """
        Parse model JSON response. Falls back to raw-as-solution on parse failure.

        Args:
            raw: Raw response string from model

        Returns:
            Parsed dict with keys: solution, rationale, risks, improvements, artifacts
        """
        clean = re.sub(r"^```(?:json)?\n|```$", "", raw.strip(), flags=re.MULTILINE)
        clean = clean.strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            # Model answered but not JSON — treat full text as solution
            return {
                "solution": raw,
                "rationale": "(non-JSON response from model)",
                "risks": [],
                "improvements": [],
                "artifacts": "",
            }

    # ---------------------------------------------------------------------------
    # Backward-compatibility wrappers for --mode council / assembly / full
    # ---------------------------------------------------------------------------

    async def run_micro_briefs(
        self,
        task: str,
        project_context: str = "",
        stage_context: str = "",
    ) -> list[dict]:
        """
        DEPRECATED: Backward-compatible wrapper for v2.0 code paths.

        Calls run_all_solutions() and converts AgentSolution list
        to the old dict format {directives, constraints, red_flags}.

        Args:
            task: User task string
            project_context: Optional context
            stage_context: Ignored (v3.0 agents are omniscient)

        Returns:
            List of dicts in v2.0 format
        """
        solutions = await self.run_all_solutions(
            task=task,
            task_type="mixed",
            project_context=project_context,
        )
        return [
            {
                "agent": s.agent_id,
                "persona": s.persona,
                "directives": s.solution[:500] if s.solution else "",
                "constraints": ", ".join(s.risks[:3]) if s.risks else "",
                "red_flags": ", ".join(s.improvements[:2]) if s.improvements else "",
                "status": s.status,
                "error": s.error,
            }
            for s in solutions
        ]