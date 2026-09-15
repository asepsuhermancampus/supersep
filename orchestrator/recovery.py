"""
orchestrator/recovery.py — Self-Healing Council: Checkpoint & Agent Substitution.
SuperSep v3.0

Handles the Self-Healing Council protocol when 2+ agents fail:
1. Save partial results to checkpoint file
2. Run agent substitution (available agents cover failed agents personas)
3. Cleanup checkpoint after successful completion

Used by: pipeline.py, ensemble_code_stage.py
"""
import asyncio
import json
import os
import re
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from orchestrator.models import AgentSolution

if TYPE_CHECKING:
    from orchestrator.router import GeminiRouter

# Persona descriptions for substitution prompts
AGENT_PERSONAS = {
    "agent_1": ("The Conservative Guardian", "risk-averse, stability-first. Always ask: what can break? what is rollback? Choose proven production patterns."),
    "agent_2": ("The Innovator", "bleeding-edge, convention-challenging. What is the most modern elegant solution? Push boundaries."),
    "agent_3": ("The Adversarial Skeptic", "assume everything will break. Devil's advocate. Hunt security holes, race conditions, edge cases."),
    "agent_4": ("The Pragmatist", "deadline-first, MVP mindset. YAGNI. Good enough IS perfect when shipped."),
    "agent_5": ("The Perfectionist", "clean code, zero tech debt. SOLID, DRY. Every function does one thing."),
    "agent_6": ("The Scalability Architect", "1M+ users mindset. Bottleneck hunter. Edge-first. What fails at 100x load?"),
    "agent_7": ("The DX Champion", "developer experience, team velocity. Fast CI. Can a new engineer onboard in 1 day?"),
    "agent_8": ("The User Advocate", "empathy-driven, human-first. WCAG 2.1. Real user scenarios. Does this work for everyone?"),
    "agent_9": ("The Data Whisperer", "database-first, data integrity. N+1 hunter. Query optimization. Migration safety."),
    "agent_10": ("The Synthesis Master", "meta-thinking, cross-pattern recognition. Sees the whole. Arbitrates conflicts."),
}

ROUND1_OUTPUT_FORMAT = """
Respond in JSON format (no markdown fences):
{
  "solution": "Complete solution from this persona perspective...",
  "rationale": "Why this approach from this persona lens...",
  "risks": ["Risk 1...", "Risk 2..."],
  "improvements": ["What could be even better..."],
  "artifacts": "Code / design / plan relevant to the task..."
}"""


class RecoveryManager:
    """
    Manages Self-Healing Council checkpoints and agent substitution.

    Checkpoint lifecycle:
    1. save_checkpoint() — called when 2+ agents fail
    2. run_substitution() — available agents cover failed agents personas
    3. cleanup_checkpoint() — called after successful final output
    """

    def __init__(self, checkpoint_base_dir: Path | str | None = None):
        if checkpoint_base_dir is None:
            checkpoint_base_dir = os.getenv("CHECKPOINT_DIR", "memory/projects")
        self.checkpoint_base_dir = Path(checkpoint_base_dir)
        self._max_substitution_attempts = int(os.getenv("MAX_SUBSTITUTION_ATTEMPTS", "3"))

    def save_checkpoint(
        self,
        project_name: str,
        solutions: list[AgentSolution],
        task: str,
    ) -> Path:
        """
        Save partial council results to a checkpoint file.

        Args:
            project_name: Sanitized project name for directory scoping
            solutions: All agent solutions (including failed ones)
            task: The original user task string

        Returns:
            Path to the created checkpoint file
        """
        checkpoint_dir = self.checkpoint_base_dir / project_name / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_path = checkpoint_dir / f"round1_partial_{timestamp}.json"
        data = {
            "timestamp": timestamp,
            "task": task,
            "solutions": [asdict(s) for s in solutions],
            "failed_agents": [s.agent_id for s in solutions if s.status == "failed"],
            "successful_agents": [s.agent_id for s in solutions if s.status == "success"],
        }
        checkpoint_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"[Recovery] Checkpoint saved: {checkpoint_path}")
        return checkpoint_path

    def load_checkpoint(self, project_name: str) -> dict | None:
        """
        Load the most recent checkpoint for a project.

        Args:
            project_name: Sanitized project name

        Returns:
            Checkpoint data dict, or None if no checkpoint exists
        """
        checkpoint_dir = self.checkpoint_base_dir / project_name / "checkpoints"
        if not checkpoint_dir.exists():
            return None
        checkpoints = sorted(checkpoint_dir.glob("round1_partial_*.json"), reverse=True)
        if not checkpoints:
            return None
        try:
            return json.loads(checkpoints[0].read_text(encoding="utf-8"))
        except Exception:
            return None

    def cleanup_checkpoint(self, project_name: str) -> None:
        """
        Delete all checkpoint files for a project after successful completion.

        Args:
            project_name: Sanitized project name
        """
        checkpoint_dir = self.checkpoint_base_dir / project_name / "checkpoints"
        if not checkpoint_dir.exists():
            return
        for f in checkpoint_dir.glob("round1_partial_*.json"):
            try:
                f.unlink()
            except Exception:
                pass
        print(f"[Recovery] Checkpoint cleaned up for: {project_name}")

    def get_failed_agents(self, solutions: list[AgentSolution]) -> list[AgentSolution]:
        """
        Return only the failed AgentSolutions from a list.

        Args:
            solutions: Full list of agent solutions

        Returns:
            List of solutions with status == 'failed'
        """
        return [s for s in solutions if s.status == "failed"]

    def get_successful_agents(self, solutions: list[AgentSolution]) -> list[AgentSolution]:
        """Return only successful solutions."""
        return [s for s in solutions if s.status == "success"]

    async def run_substitution(
        self,
        failed_solutions: list[AgentSolution],
        available_solutions: list[AgentSolution],
        task: str,
        task_type: str,
        router: "GeminiRouter",
    ) -> list[AgentSolution]:
        """
        Run agent substitution: available agents cover failed agents personas.

        Args:
            failed_solutions: Solutions from agents that failed
            available_solutions: Solutions from agents that succeeded
            task: Original user task
            task_type: Detected task type
            router: GeminiRouter instance for making requests

        Returns:
            List of substituted AgentSolution objects (status='substituted')
        """
        if not failed_solutions or not available_solutions:
            return []
        print(f"[Recovery] Running agent substitution for {len(failed_solutions)} failed agent(s)...")
        substitution_tasks = [
            self._run_single_substitution(
                failed_agent_id=failed.agent_id,
                substitute_context=available_solutions[i % len(available_solutions)].solution[:2000],
                task=task,
                task_type=task_type,
                router=router,
            )
            for i, failed in enumerate(failed_solutions)
        ]
        results = await asyncio.gather(*substitution_tasks, return_exceptions=True)
        substituted = [r for r in results if isinstance(r, AgentSolution)]
        failed_count = sum(1 for r in results if isinstance(r, Exception))
        if failed_count:
            print(f"[Recovery] {failed_count} substitution(s) also failed.")
        print(f"[Recovery] Substitution complete: {len(substituted)}/{len(failed_solutions)} recovered")
        return substituted

    async def _run_single_substitution(
        self,
        failed_agent_id: str,
        substitute_context: str,
        task: str,
        task_type: str,
        router: "GeminiRouter",
    ) -> AgentSolution:
        """Run a single agent substitution request."""
        persona_name, persona_desc = AGENT_PERSONAS.get(
            failed_agent_id,
            (failed_agent_id, "expert full-stack engineer")
        )
        system_prompt = f"""You are a world-class full-stack engineer stepping in to cover for a team member.

You have complete mastery of: routing, state management, form validation, UI/UX design,
Tailwind CSS, animations, Zod schemas, TypeScript, API routes, Server Actions, Prisma ORM,
PostgreSQL, Redis caching, Next.js App Router, authentication, authorization, OWASP security,
input sanitization, error handling, Docker, CI/CD, Vitest, Playwright, WCAG 2.1,
performance optimization, PWA — everything in modern web/application development.

## Substitution Role: {persona_name}
Think and respond EXACTLY as "{persona_name}" would: {persona_desc}"""

        user_prompt = f"""TASK TYPE: {task_type}
TASK: {task}

Context from another council member:\n{substitute_context}

Now respond as {persona_name} with a COMPLETE solution in JSON:
{ROUND1_OUTPUT_FORMAT}"""

        last_error: Exception | None = None
        for attempt in range(self._max_substitution_attempts):
            try:
                raw = await router.request(system_prompt=system_prompt, user_prompt=user_prompt)
                clean = re.sub(r"^```(?:json)?\n|```$", "", raw.strip(), flags=re.MULTILINE)
                parsed = json.loads(clean)
                print(f"[Recovery] Substitution OK: {failed_agent_id} covered as {persona_name}")
                return AgentSolution(
                    agent_id=failed_agent_id,
                    persona=persona_name,
                    status="substituted",
                    solution=parsed.get("solution", ""),
                    rationale=parsed.get("rationale", ""),
                    risks=parsed.get("risks", []),
                    improvements=parsed.get("improvements", []),
                    artifacts=parsed.get("artifacts", ""),
                    raw=raw,
                )
            except Exception as e:
                last_error = e
                print(f"[Recovery] Substitution attempt {attempt + 1}/{self._max_substitution_attempts} failed: {e}")
        raise RuntimeError(f"Substitution failed for {failed_agent_id} after all attempts: {last_error}")
