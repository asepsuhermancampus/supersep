"""
orchestrator/stages/arch_stage.py — Stage 2: System Architecture & Data Contracts
SuperSep v2.0

Triggered by: /mikirsep --stage arch
Pipeline state: UI_COMPLETED → ARCH_COMPLETED
Prerequisite: ui_design_system.md must exist
Deliverable:
  - memory/projects/<name>/deliverables/master_architecture_blueprint.md
"""

from pathlib import Path
from typing import Any

try:
    from orchestrator.router import GeminiRouter
    from orchestrator.agent_runner import AgentRunner
    from orchestrator.council import Council
    from orchestrator.state import CheckpointStateManager
    from orchestrator.triage import ProjectMemory
except ImportError:
    from router import GeminiRouter
    from agent_runner import AgentRunner
    from council import Council
    from state import CheckpointStateManager
    from triage import ProjectMemory


_ARCH_STAGE_CONTEXT = """
STAGE FOCUS: System Architecture & Data Contracts

The UI Design System has been approved. Now the council must translate the visual
specification into a complete technical architecture.

In this stage, the council is specifically tasked with:
1. Validating business logic integrity and identifying all edge cases in user journeys (Agent 1)
2. Defining UI component data requirements and CSS modular token architecture (Agent 2)
3. Designing database schema (Prisma SDL), Zod validation schemas, API/Server Action contracts,
   and 5-state response specifications for every endpoint (Agent 3)
4. Defining folder architecture, module boundaries, dependency decoupling (Agent 4)
5. Identifying security vulnerabilities (OWASP), race conditions, and failure modes (Agent 5)

The deliverable is the Master Architecture Blueprint — a complete, unambiguous technical
specification that Agent 4 can use to write production code without asking any questions.

Standards to enforce:
- Every endpoint: 5-state response contract (Idle | Loading | Success | Empty | Error)
- Every database table: proper indexes on FK and frequently queried columns
- Zero `any` TypeScript types
- All input validation via Zod schemas
"""


class ArchStage:
    def __init__(
        self,
        router: GeminiRouter | None = None,
        memory: ProjectMemory | None = None,
        state_manager: CheckpointStateManager | None = None,
    ):
        self.router = router or GeminiRouter()
        self.memory = memory or ProjectMemory()
        self.state_manager = state_manager or CheckpointStateManager()
        self.runner = AgentRunner(router=self.router)
        self.council = Council(router=self.router)

    async def run(
        self,
        task: str,
        safe_name: str,
        project_context: str = "",
    ) -> dict[str, Any]:
        """
        Execute Stage 2: System Architecture & Data Contracts.

        Args:
            task: The engineering task description.
            safe_name: Sanitized project name.
            project_context: Prior decisions and stack context from project memory.
        """
        print("\n" + "="*55)
        print("STAGE 2: SYSTEM ARCHITECTURE & DATA CONTRACTS")
        print("="*55)

        # Load UI design system as mandatory context
        ui_design_context = self._load_ui_design_system(safe_name)

        # Compose full context: project memory + UI design system
        full_context = project_context
        if ui_design_context:
            full_context += f"\n\n### UI DESIGN SYSTEM (Approved — Use as Immutable Reference):\n{ui_design_context}"
        else:
            print("[Arch Stage] Warning: ui_design_system.md not found. Proceeding without UI context.")

        # Round 1: 5-agent micro-briefs with Architecture focus
        briefs = await self.runner.run_micro_briefs(
            task=task,
            project_context=full_context,
            stage_context=_ARCH_STAGE_CONTEXT,
        )

        # Load agent prompts for Round 2
        agent_prompts = {
            agent_id: self.runner.load_agent_prompt(agent_file)
            for agent_id, agent_file in self.runner.agents
        }

        # Round 2: Matrix debate
        debates = await self.council.matrix_debate(
            briefs=briefs,
            agent_prompts=agent_prompts,
        )

        # Round 3: Synthesize Architecture Blueprint
        blueprint = await self.council.synthesize_blueprint(
            task=task,
            briefs=briefs,
            debates=debates,
            project_context=full_context,
            stage_focus="System Architecture & Data Contracts — produce complete database schema "
                        "(Prisma SDL), Zod validation schemas, typed API contracts with 5-state "
                        "response specifications, folder structure, state management strategy, "
                        "security architecture, and a phased task checklist ordered by dependency.",
        )

        # Write deliverable
        deliverables_dir = self._ensure_deliverables_dir(safe_name)
        blueprint_path = self._write_blueprint(blueprint, task, deliverables_dir)

        # Advance pipeline state
        self.state_manager.advance(
            safe_name=safe_name,
            next_state="ARCH_COMPLETED",
            metadata={
                "arch_deliverable": str(blueprint_path),
                "arch_task": task,
            },
        )

        print(f"\n✓ Master Architecture Blueprint saved: {blueprint_path}")

        return {
            "stage": "arch",
            "status": "completed",
            "blueprint": blueprint,
            "briefs": briefs,
            "debates": debates,
            "blueprint_path": str(blueprint_path),
        }

    def _ensure_deliverables_dir(self, safe_name: str) -> Path:
        d = (
            Path(__file__).resolve().parent.parent.parent
            / "memory" / "projects" / safe_name / "deliverables"
        )
        d.mkdir(parents=True, exist_ok=True)
        return d

    def _load_ui_design_system(self, safe_name: str) -> str:
        """Load the approved UI design system markdown as context."""
        path = (
            Path(__file__).resolve().parent.parent.parent
            / "memory" / "projects" / safe_name / "deliverables" / "ui_design_system.md"
        )
        if path.exists():
            content = path.read_text(encoding="utf-8")
            # Truncate to prevent context window overflow while keeping key info
            if len(content) > 8000:
                return content[:8000] + "\n\n[... truncated for context window — see full file ...]"
            return content
        return ""

    def _write_blueprint(
        self,
        blueprint: str,
        task: str,
        deliverables_dir: Path,
    ) -> Path:
        """Write the Master Architecture Blueprint markdown deliverable."""
        path = deliverables_dir / "master_architecture_blueprint.md"

        content = f"""# Master Architecture Blueprint
Generated by SuperSep v2.0 — Stage 2: System Architecture & Data Contracts
Task: {task}

---

{blueprint}
"""
        path.write_text(content, encoding="utf-8")
        return path
