"""
orchestrator/stages/ensemble_code_stage.py  Stage 3: 10-Agent Mob Coding & Direct File Writer
SuperSep v3.0

Triggered by: /gassep (--stage gas)
Pipeline state: ARCH_COMPLETED -> CODE_COMPLETED

Each agent writes their assigned section. Agent 4 is the primary code implementer.
Code is written directly to the target project workspace on disk.
"""

import json
import re
from pathlib import Path
from typing import Any

try:
    from orchestrator.router import GeminiRouter
    from orchestrator.state import CheckpointStateManager
    from orchestrator.triage import ProjectMemory
    from orchestrator.agent_runner import AgentRunner
    from orchestrator.council import Council
except ImportError:
    from router import GeminiRouter
    from state import CheckpointStateManager
    from triage import ProjectMemory
    from agent_runner import AgentRunner
    from council import Council


class EnsembleCodeStage:
    def __init__(
        self,
        router: GeminiRouter | None = None,
        state_manager: CheckpointStateManager | None = None,
    ):
        self.router = router or GeminiRouter()
        self.state_manager = state_manager or CheckpointStateManager()
        self.agents_dir = Path(__file__).resolve().parent.parent.parent / "agents"
        self.runner = AgentRunner(router=self.router)
        self.council = Council(router=self.router)

    def _load_agent_prompt(self, filename: str) -> str:
        path = self.agents_dir / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        return ""

    def _load_blueprint(self, safe_name: str) -> str:
        """Load the approved architecture blueprint."""
        path = (
            Path(__file__).resolve().parent.parent.parent
            / "memory" / "projects" / safe_name / "deliverables" / "master_architecture_blueprint.md"
        )
        if path.exists():
            content = path.read_text(encoding="utf-8")
            if len(content) > 12000:
                return content[:12000] + "\n\n[... truncated  see full blueprint file ...]"
            return content
        return ""

    async def run(
        self,
        task: str,
        safe_name: str,
        target_path: Path,
        project_context: str = "",
    ) -> dict[str, Any]:
        """Stage 3: 10-Agent Omni Coding  all agents write full implementations, synthesizer merges."""
        print("STAGE 3: ENSEMBLE CODING (10-AGENT OMNI PROTOCOL)")
        
        blueprint = self._load_blueprint(safe_name)
        full_task = f"{task}\n\nARCHITECTURE BLUEPRINT:\n{blueprint}" if blueprint else task
        
        # Round 1: all 10 agents write complete implementations
        solutions = await self.runner.run_all_solutions(
            task=full_task,
            task_type="coding",
            project_context=project_context,
        )
        
        # Self-healing if needed
        import os
        from orchestrator.recovery import RecoveryManager
        quorum = int(os.getenv("COUNCIL_QUORUM", "9"))
        failed = [s for s in solutions if s.status == "failed"]
        if len(failed) >= (len(solutions) - quorum + 1):
            recovery = RecoveryManager()
            recovery.save_checkpoint(safe_name, solutions, full_task)
            available = [s for s in solutions if s.status == "success"]
            if available:
                substituted = await recovery.run_substitution(
                    failed, available, full_task, "coding", self.router
                )
                sol_map = {s.agent_id: s for s in solutions}
                for sub in substituted:
                    sol_map[sub.agent_id] = sub
                solutions = list(sol_map.values())
            recovery.cleanup_checkpoint(safe_name)
        
        # Round 2: cross-critique
        critiques = await self.council.run_cross_critique(solutions)
        
        # Round 3: merged master code
        merged = await self.council.synthesize_merged_master(
            task=full_task,
            solutions=solutions,
            critiques=critiques,
            task_type="coding",
            project_context=project_context,
        )
        
        # Write output files
        written = self._write_output(merged, str(target_path))
        
        # Update state
        self.state_manager.advance(
            safe_name=safe_name,
            next_state="CODE_COMPLETED",
            metadata={"written_files": written},
        )
        return {"stage": "ensemble_code", "status": "completed", "written_files": written}

    def _write_output(self, synthesis: str, target_path: str | None) -> list[str]:
        """Write synthesis output to files. Tries JSON format, falls back to single .md file."""
        import json
        from pathlib import Path
        
        written = []
        try:
            data = json.loads(synthesis)
            files = data.get("files", [])
            if files and target_path:
                base = Path(target_path)
                base.mkdir(parents=True, exist_ok=True)
                for f in files:
                    fp = base / f["path"]
                    fp.parent.mkdir(parents=True, exist_ok=True)
                    fp.write_text(f["content"], encoding="utf-8")
                    written.append(str(fp))
                return written
        except Exception:
            pass
        
        # Fallback: write entire synthesis as markdown
        if target_path:
            out = Path(target_path) / "SUPERSEP_IMPLEMENTATION.md"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(synthesis, encoding="utf-8")
            written.append(str(out))
        return written
