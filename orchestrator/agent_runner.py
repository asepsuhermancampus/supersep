import asyncio
import re
import yaml
from pathlib import Path
from typing import List, Dict, Any

try:
    from orchestrator.router import GeminiRouter
except ImportError:
    from router import GeminiRouter


class AgentRunner:
    def __init__(self, router: GeminiRouter | None = None):
        self.router = router or GeminiRouter()

        self.agents_dir = (
            Path(__file__).resolve().parent.parent / "agents"
        )

        self.agents = [
            ("agent_1", self.agents_dir / "agent1.md"),
            ("agent_2", self.agents_dir / "agent2.md"),
            ("agent_3", self.agents_dir / "agent3.md"),
            ("agent_4", self.agents_dir / "agent4.md"),
            ("agent_5", self.agents_dir / "agent5.md"),
        ]

    def load_agent_prompt(self, path: Path) -> str:
        if not path.exists():
            raise FileNotFoundError(
                f"Agent prompt tidak ditemukan: {path}"
            )

        return path.read_text(encoding="utf-8")

    async def run_agent_micro_brief(
        self,
        agent_id: str,
        agent_file: Path,
        task: str,
        project_context: str = "",
    ) -> Dict[str, Any]:
        role_prompt = self.load_agent_prompt(agent_file)

        system_prompt = f"""
{role_prompt}

CRITICAL TOKEN CONSTRAINT:
You are in ROUND 1: MICRO-BRIEFS.
Analyze the task strictly from your assigned role.
Do NOT write essays, introductory greetings, or verbose explanations.
You MUST respond strictly in the following YAML format (maximum 150 words total):

directives:
  - "Core directive 1"
  - "Core directive 2"
  - "Core directive 3"
constraints:
  - "Hard constraint 1"
  - "Hard constraint 2"
red_flags:
  - "Critical risk 1"
  - "Critical risk 2"
"""

        context_block = ""
        if project_context:
            context_block = f"\nPROJECT CONTEXT & CONVENTIONS:\n{project_context}\n"

        user_prompt = f"""
TASK:
{task}
{context_block}
Provide your micro-brief in strict YAML format.
"""

        try:
            raw_response = await self.router.request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            # Strip markdown code blocks if any
            clean_yaml = re.sub(r"^```(?:yaml)?\n|```$", "", raw_response.strip(), flags=re.MULTILINE)
            parsed = {}
            try:
                parsed = yaml.safe_load(clean_yaml) or {}
            except Exception:
                parsed = {
                    "directives": [raw_response.strip()[:200]],
                    "constraints": [],
                    "red_flags": [],
                }

            return {
                "agent_id": agent_id,
                "status": "success",
                "directives": parsed.get("directives", []),
                "constraints": parsed.get("constraints", []),
                "red_flags": parsed.get("red_flags", []),
                "raw": raw_response.strip(),
            }

        except Exception as e:
            print(f"[{agent_id}] Micro-Brief ERROR: {type(e).__name__}: {e}")
            return {
                "agent_id": agent_id,
                "status": "error",
                "directives": [],
                "constraints": [],
                "red_flags": [],
                "error": str(e),
                "raw": "",
            }

    async def run_micro_briefs(
        self,
        task: str,
        project_context: str = "",
    ) -> List[Dict[str, Any]]:
        print("================================")
        print("ACTIVE-5: ROUND 1 (MICRO-BRIEFS)")
        print("================================")

        tasks = [
            self.run_agent_micro_brief(
                agent_id,
                agent_file,
                task,
                project_context,
            )
            for agent_id, agent_file in self.agents
        ]

        results = await asyncio.gather(*tasks)
        print("================================")
        print("ROUND 1 COMPLETED (5/5 BRIEFS)")
        print("================================")
        return results