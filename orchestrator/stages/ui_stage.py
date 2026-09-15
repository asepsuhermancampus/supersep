"""
orchestrator/stages/ui_stage.py — Stage 1: UI/UX Discovery & Visual Design System
SuperSep v2.0

Triggered by: /mikirsep --stage ui
Pipeline state: INIT → UI_COMPLETED
Deliverables:
  - memory/projects/<name>/deliverables/ui_design_system.md
  - memory/projects/<name>/deliverables/preview.html
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


_UI_STAGE_CONTEXT = """
STAGE FOCUS: UI/UX Discovery & Visual Design System

In this stage, the council is specifically tasked with:
1. Analyzing user journeys, interaction flows, and mental models (Agent 1)
2. Defining design tokens (colors, typography, spacing, shadows) and component hierarchy (Agent 2)
3. Determining UI state management needs — skeleton, optimistic UI, empty states (Agent 3)
4. Evaluating rendering feasibility and framework UI conventions (Agent 4)
5. Auditing contrast ratios, keyboard navigation, and responsive edge cases (Agent 5)

The deliverable is a complete, self-consistent Design System specification
that will serve as the immutable source of truth for the Architecture stage.

References to benchmark against: Stripe Dashboard, Vercel Dashboard, Linear App, Apple HIG.
"""


class UIStage:
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
        image_path: str | None = None,
    ) -> dict[str, Any]:
        """
        Execute Stage 1: UI/UX Discovery.

        Args:
            task: The design task description.
            safe_name: Sanitized project name (for memory/deliverables path).
            project_context: Prior decisions and context from project memory.
            image_path: Optional path/URL to reference screenshot or mockup.
        """
        print("\n" + "="*55)
        print("STAGE 1: UI/UX DISCOVERY & VISUAL DESIGN SYSTEM")
        print("="*55)

        # Build stage-specific context
        image_note = ""
        if image_path:
            image_note = f"\nREFERENCE VISUAL: {image_path} (attached as image input)\n"

        stage_context = _UI_STAGE_CONTEXT + image_note

        # Round 1: 5-agent micro-briefs with UI focus
        briefs = await self.runner.run_micro_briefs(
            task=task,
            project_context=project_context,
            stage_context=stage_context,
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

        # Round 3: Synthesize Design System Blueprint
        blueprint = await self.council.synthesize_blueprint(
            task=task,
            briefs=briefs,
            debates=debates,
            project_context=project_context,
            stage_focus="UI/UX Design System — produce complete design token specifications, "
                        "component hierarchy, typography scale, color palette, spacing grid, "
                        "and interaction patterns. Include a standalone HTML preview specification.",
        )

        # Generate deliverable files
        deliverables_dir = self._ensure_deliverables_dir(safe_name)
        ui_design_system_path = await self._write_design_system(
            blueprint=blueprint,
            task=task,
            deliverables_dir=deliverables_dir,
        )
        preview_html_path = await self._generate_preview_html(
            blueprint=blueprint,
            task=task,
            deliverables_dir=deliverables_dir,
        )

        # Advance pipeline state
        self.state_manager.advance(
            safe_name=safe_name,
            next_state="UI_COMPLETED",
            metadata={
                "ui_deliverable": str(ui_design_system_path),
                "preview_html": str(preview_html_path),
                "ui_task": task,
            },
        )

        print(f"\n✓ UI Design System saved: {ui_design_system_path}")
        print(f"✓ Preview HTML saved: {preview_html_path}")

        return {
            "stage": "ui",
            "status": "completed",
            "blueprint": blueprint,
            "briefs": briefs,
            "debates": debates,
            "ui_design_system_path": str(ui_design_system_path),
            "preview_html_path": str(preview_html_path),
        }

    def _ensure_deliverables_dir(self, safe_name: str) -> Path:
        d = (
            Path(__file__).resolve().parent.parent.parent
            / "memory" / "projects" / safe_name / "deliverables"
        )
        d.mkdir(parents=True, exist_ok=True)
        return d

    async def _write_design_system(
        self,
        blueprint: str,
        task: str,
        deliverables_dir: Path,
    ) -> Path:
        """Write the UI design system markdown deliverable."""
        path = deliverables_dir / "ui_design_system.md"

        content = f"""# UI Design System
Generated by SuperSep v2.0 — Stage 1: UI/UX Discovery
Task: {task}

---

{blueprint}
"""
        path.write_text(content, encoding="utf-8")
        return path

    async def _generate_preview_html(
        self,
        blueprint: str,
        task: str,
        deliverables_dir: Path,
    ) -> Path:
        """
        Ask the model to generate a standalone Tailwind CSS HTML preview
        based on the design system blueprint.
        """
        print("\n[UI Stage] Generating standalone HTML preview prototype...")

        system_prompt = """You are a master frontend developer specializing in rapid UI prototyping.

Your task: Convert the provided Design System specification into a beautiful, 
standalone, self-contained HTML file using Tailwind CSS via CDN.

Rules:
- Use ONLY a single HTML file — no external assets beyond Tailwind CDN.
- Use <script src="https://cdn.tailwindcss.com"></script> for Tailwind.
- Include ALL color tokens in a Tailwind config block using tailwind.config.
- Demonstrate every major component and state defined in the spec.
- Show responsive behavior (mobile-first).
- Include micro-animations using CSS transitions.
- Make it pixel-perfect and visually impressive.
- The file must work when opened directly in a browser (no build step).
- Output ONLY the raw HTML — no markdown fences, no explanation text.
"""

        user_prompt = f"""TASK: {task}

DESIGN SYSTEM SPECIFICATION:
{blueprint}

Generate the complete standalone HTML preview file now. Output raw HTML only.
"""

        try:
            html_content = await self.router.request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            # Strip markdown code fences if model wraps output
            import re
            html_content = re.sub(
                r"^```(?:html)?\n|```$", "", html_content.strip(), flags=re.MULTILINE
            )

        except Exception as e:
            print(f"[UI Stage] Warning: HTML preview generation failed: {e}")
            html_content = self._fallback_preview_html(task)

        path = deliverables_dir / "preview.html"
        path.write_text(html_content, encoding="utf-8")
        return path

    def _fallback_preview_html(self, task: str) -> str:
        """Minimal fallback HTML if model generation fails."""
        return f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>UI Preview — {task[:60]}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50 min-h-screen flex items-center justify-center p-8">
  <div class="max-w-2xl w-full bg-white rounded-2xl shadow-lg p-8 text-center">
    <h1 class="text-2xl font-bold text-gray-900 mb-4">UI Preview</h1>
    <p class="text-gray-600 mb-2">Task: {task[:200]}</p>
    <p class="text-sm text-amber-600 bg-amber-50 rounded-lg p-3 mt-4">
      Preview generation encountered an issue. Please refer to ui_design_system.md for full specification.
    </p>
  </div>
</body>
</html>"""
