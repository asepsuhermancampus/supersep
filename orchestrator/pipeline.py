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
except ImportError:
    from router import GeminiRouter
    from triage import WorkspaceDetector, ProjectMemory
    from agent_runner import AgentRunner
    from council import Council
    from assembly import AssemblyLine
    from learner import KnowledgeDistiller


class UnifiedPipeline:
    def __init__(
        self,
        router: GeminiRouter | None = None,
        memory: ProjectMemory | None = None,
    ):
        self.router = router or GeminiRouter()
        self.memory = memory or ProjectMemory()
        self.detector = WorkspaceDetector()
        self.runner = AgentRunner(router=self.router)
        self.council = Council(router=self.router)
        self.assembly = AssemblyLine(router=self.router)
        self.learner = KnowledgeDistiller(memory=self.memory, router=self.router)

    async def run(
        self,
        task: str,
        target_path: Path | str | None = None,
        mode: str = "council",
    ) -> Dict[str, Any]:
        project_info = self.detector.detect(target_path)
        safe_name = project_info["safe_name"]
        project_data = self.memory.load(safe_name)

        project_context = ""
        if project_data["decisions"]:
            project_context += f"Previous Decisions:\n{project_data['decisions']}\n"
        if project_data["context"]:
            project_context += f"Stack Context:\n{project_data['context']}\n"

        print("==================================================")
        print(f"AI-TEAM ENGINE: ACTIVE FOR [{project_info['name']}]")
        print(f"MODE: {mode.upper()}")
        print("==================================================")

        # PHASE 1: THE COUNCIL
        # Round 1: Micro-Briefs
        briefs = await self.runner.run_micro_briefs(
            task=task,
            project_context=project_context,
        )

        # Load role prompts for Round 2
        agent_prompts = {}
        for agent_id, agent_file in self.runner.agents:
            agent_prompts[agent_id] = self.runner.load_agent_prompt(agent_file)

        # Round 2: Matrix Debate
        debates = await self.council.matrix_debate(
            briefs=briefs,
            agent_prompts=agent_prompts,
        )

        # Round 3: Master Blueprint
        blueprint = await self.council.synthesize_blueprint(
            task=task,
            briefs=briefs,
            debates=debates,
            project_context=project_context,
        )

        result: Dict[str, Any] = {
            "status": "success",
            "project": project_info,
            "mode": mode,
            "briefs": briefs,
            "debates": debates,
            "blueprint": blueprint,
            "code": None,
            "review": None,
            "learnings": [],
        }

        # PHASE 2: THE ASSEMBLY LINE (if mode is 'assembly' or 'full')
        if mode in ("assembly", "full"):
            print("\n==================================================")
            print("PHASE 2: ASSEMBLY LINE EXECUTION")
            print("==================================================")

            print("[Agent 2] Generating UI Component Specification...")
            ui_spec = await self.assembly.generate_ui_spec(blueprint)

            print("[Agent 3] Generating Data Contracts & Schema Specification...")
            data_spec = await self.assembly.generate_data_spec(blueprint)

            print("[Agent 4] Senior Developer Implementing Production Code...")
            code = await self.assembly.implement_code(task, ui_spec, data_spec)

            print("[Agent 5] Adversarial QA Audit & Security Verification...")
            review = await self.assembly.adversarial_review(code, task)

            result["code"] = code
            result["ui_spec"] = ui_spec
            result["data_spec"] = data_spec
            result["review"] = review

        # Knowledge Distillation
        print("\n[Learner] Distilling session learnings...")
        learnings = await self.learner.extract_learnings(
            task=task,
            blueprint=blueprint,
            safe_project_name=safe_name,
        )
        result["learnings"] = learnings

        return result
