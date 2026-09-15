"""
orchestrator/pipeline.py — Unified Modular Lifecycle Pipeline
SuperSep v2.0

Orchestrates all stages in the correct order based on execution mode.
Delegates to stage-specific modules rather than containing all logic inline.
"""

import asyncio
from pathlib import Path
from typing import Dict, Any

try:
    from orchestrator.router import GeminiRouter
    from orchestrator.triage import WorkspaceDetector, ProjectMemory
    from orchestrator.agent_runner import AgentRunner
    from orchestrator.council import Council
    from orchestrator.assembly import AssemblyLine
    from orchestrator.learner import KnowledgeDistiller
    from orchestrator.state import CheckpointStateManager
    from orchestrator.stages.ui_stage import UIStage
    from orchestrator.stages.arch_stage import ArchStage
    from orchestrator.stages.ensemble_code_stage import EnsembleCodeStage
    from orchestrator.stages.healing_stage import HealingStage
except ImportError:
    from router import GeminiRouter
    from triage import WorkspaceDetector, ProjectMemory
    from agent_runner import AgentRunner
    from council import Council
    from assembly import AssemblyLine
    from learner import KnowledgeDistiller
    from state import CheckpointStateManager
    from stages.ui_stage import UIStage
    from stages.arch_stage import ArchStage
    from stages.ensemble_code_stage import EnsembleCodeStage
    from stages.healing_stage import HealingStage


class UnifiedPipeline:
    def __init__(
        self,
        router: GeminiRouter | None = None,
        memory: ProjectMemory | None = None,
    ):
        self.router = router or GeminiRouter()
        self.memory = memory or ProjectMemory()
        self.detector = WorkspaceDetector()
        self.state_manager = CheckpointStateManager()

        # Legacy Phase 1 runners (used by 'council' mode for backward compat)
        self.runner = AgentRunner(router=self.router)
        self.council = Council(router=self.router)
        self.learner = KnowledgeDistiller(memory=self.memory, router=self.router)

        # v2.0 Stage Modules
        self.ui_stage = UIStage(router=self.router, memory=self.memory, state_manager=self.state_manager)
        self.arch_stage = ArchStage(router=self.router, memory=self.memory, state_manager=self.state_manager)
        self.ensemble_stage = EnsembleCodeStage(router=self.router, state_manager=self.state_manager)
        self.healing_stage = HealingStage(router=self.router, state_manager=self.state_manager)

        # Legacy assembly (kept for backward compat with 'assembly' mode)
        self.assembly = AssemblyLine(router=self.router)

    async def run(
        self,
        task: str,
        target_path: Path | str | None = None,
        mode: str = "council",
        stage: str | None = None,
        image_path: str | None = None,
    ) -> Dict[str, Any]:
        """
        Main pipeline entry point.

        Args:
            task: Engineering task description.
            target_path: Workspace directory to write code to.
            mode: Execution mode — 'council', 'assembly', 'full' (legacy compat)
            stage: v2.0 granular stage — 'ui', 'arch', 'gas', 'heal', 'status'
            image_path: Optional reference screenshot/mockup for UI stage.
        """
        project_info = self.detector.detect(target_path)
        safe_name = project_info["safe_name"]
        project_data = self.memory.load(safe_name)

        project_context = ""
        if project_data["decisions"]:
            project_context += f"Previous Decisions:\n{project_data['decisions']}\n"
        if project_data["context"]:
            project_context += f"Stack Context:\n{project_data['context']}\n"

        effective_target = Path(target_path) if target_path else Path.cwd()

        print("==================================================")
        print(f"SUPERSEP v2.0: [{project_info['name']}]")
        print(f"MODE: {(stage or mode).upper()} | STATE: {self.state_manager.get_current(safe_name)}")
        print("==================================================")

        # ── v2.0 GRANULAR STAGE ROUTING ──────────────────────────────────────
        if stage == "status":
            self.state_manager.print_status(safe_name)
            return {"status": "info", "project": project_info}

        if stage == "ui":
            result = await self.ui_stage.run(
                task=task,
                safe_name=safe_name,
                project_context=project_context,
                image_path=image_path,
            )
            await self._distill_and_propose(task, result.get("blueprint", ""), safe_name)
            result["project"] = project_info
            return result

        if stage == "arch":
            result = await self.arch_stage.run(
                task=task,
                safe_name=safe_name,
                project_context=project_context,
            )
            await self._distill_and_propose(task, result.get("blueprint", ""), safe_name)
            result["project"] = project_info
            return result

        if stage == "gas":
            result = await self.ensemble_stage.run(
                task=task,
                safe_name=safe_name,
                target_path=effective_target,
                project_context=project_context,
            )
            # Auto-trigger self-healing after ensemble coding
            heal_result = await self.healing_stage.run(
                safe_name=safe_name,
                target_path=effective_target,
                task=task,
            )
            result["healing"] = heal_result
            result["project"] = project_info
            return result

        if stage == "heal":
            result = await self.healing_stage.run(
                safe_name=safe_name,
                target_path=effective_target,
                task=task,
            )
            result["project"] = project_info
            return result

        # ── LEGACY MODE ROUTING (backward compatibility) ──────────────────────
        if mode == "full":
            # Full v2.0 pipeline: UI → Arch → Code → Heal
            ui_result = await self.ui_stage.run(
                task=task, safe_name=safe_name, project_context=project_context, image_path=image_path
            )
            arch_result = await self.arch_stage.run(
                task=task, safe_name=safe_name, project_context=project_context
            )
            code_result = await self.ensemble_stage.run(
                task=task, safe_name=safe_name, target_path=effective_target, project_context=project_context
            )
            heal_result = await self.healing_stage.run(
                safe_name=safe_name, target_path=effective_target, task=task
            )
            blueprint = arch_result.get("blueprint", ui_result.get("blueprint", ""))
            await self._distill_and_propose(task, blueprint, safe_name)
            return {
                "status": "success",
                "project": project_info,
                "mode": "full",
                "ui": ui_result,
                "arch": arch_result,
                "code": code_result,
                "healing": heal_result,
            }

        if mode == "assembly":
            # Legacy assembly: use old assembly.py for backward compat
            print("[Pipeline] Using legacy assembly mode.")
            blueprint = await self._run_legacy_council(task, project_context, safe_name)
            ui_spec = await self.assembly.generate_ui_spec(blueprint)
            data_spec = await self.assembly.generate_data_spec(blueprint)
            code = await self.assembly.implement_code(task, ui_spec, data_spec)
            review = await self.assembly.adversarial_review(code, task)
            await self._distill_and_propose(task, blueprint, safe_name)
            return {
                "status": "success",
                "project": project_info,
                "mode": "assembly",
                "blueprint": blueprint,
                "code": code,
                "review": review,
            }

        # Default: 'council' mode — Phase 1 planning only (legacy compat)
        briefs, debates, blueprint = await self._run_legacy_council_full(task, project_context, safe_name)
        learnings = await self._distill_and_propose(task, blueprint, safe_name)
        return {
            "status": "success",
            "project": project_info,
            "mode": "council",
            "blueprint": blueprint,
            "briefs": briefs,
            "debates": debates,
            "learnings": learnings,
        }

    async def _run_legacy_council_full(
        self,
        task: str,
        project_context: str,
        safe_name: str,
    ) -> tuple[list, list, str]:
        """Run the legacy 3-round council. Returns (briefs, debates, blueprint)."""
        briefs = await self.runner.run_micro_briefs(task=task, project_context=project_context)

        agent_prompts = {
            agent_id: self.runner.load_agent_prompt(agent_file)
            for agent_id, agent_file in self.runner.agents
        }

        debates = await self.council.matrix_debate(briefs=briefs, agent_prompts=agent_prompts)

        blueprint = await self.council.synthesize_blueprint(
            task=task,
            briefs=briefs,
            debates=debates,
            project_context=project_context,
        )
        return briefs, debates, blueprint

    async def _run_legacy_council(
        self,
        task: str,
        project_context: str,
        safe_name: str,
    ) -> str:
        """Thin wrapper — returns only the blueprint string."""
        _, _, blueprint = await self._run_legacy_council_full(task, project_context, safe_name)
        return blueprint

    async def _distill_and_propose(
        self,
        task: str,
        blueprint: str,
        safe_name: str,
    ) -> list:
        """Run knowledge distillation and return learnings for display."""
        try:
            learnings = await self.learner.extract_learnings(
                task=task,
                blueprint=blueprint,
                safe_project_name=safe_name,
            )
            return learnings
        except Exception as e:
            print(f"[Learner] Distillation warning: {e}")
            return []
