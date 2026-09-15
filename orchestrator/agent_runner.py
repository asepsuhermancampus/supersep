import asyncio
import random
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
            ("agent_6", self.agents_dir / "agent6.md"),
            ("agent_7", self.agents_dir / "agent7.md"),
            ("agent_8", self.agents_dir / "agent8.md"),
            ("agent_9", self.agents_dir / "agent9.md"),
            ("agent_10", self.agents_dir / "agent10.md"),
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
        stage_context: str = "",
    ) -> Dict[str, Any]:
        role_prompt = self.load_agent_prompt(agent_file)

        # Stage-specific context injection
        stage_block = ""
        if stage_context:
            stage_block = f"\nSTAGE CONTEXT:\n{stage_context}\n"

        system_prompt = f"""{role_prompt}

## Round 1: MICRO-BRIEF DIRECTIVE

You are contributing your expert analysis in Round 1 of a 3-round elite engineering council.

Your mission: Analyze the task strictly from your assigned cognitive lens and deliver your most important directives, constraints, and risk flags.

Be thorough and precise. Do NOT truncate your reasoning. If a point needs explanation, explain it fully.
Be concise where brevity is appropriate, but never sacrifice depth for word count.

Respond in the following YAML format:
{stage_block}
directives:
  - "Concrete directive 1 — with specific technical reasoning"
  - "Concrete directive 2"
  - "Concrete directive 3 (add more if needed)"
constraints:
  - "Hard constraint 1 — why this constraint matters"
  - "Hard constraint 2"
red_flags:
  - "Critical risk 1 — specific scenario and consequence"
  - "Critical risk 2"
"""

        context_block = ""
        if project_context:
            context_block = f"\nPROJECT CONTEXT & CONVENTIONS:\n{project_context}\n"

        user_prompt = f"""TASK:
{task}
{context_block}
Apply your Chain-of-Thought protocol, then provide your expert micro-brief in YAML format.
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
                # If YAML parsing fails, treat the raw response as a directive
                parsed = {
                    "directives": [raw_response.strip()],
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
        stage_context: str = "",
    ) -> List[Dict[str, Any]]:
        n_agents = len(self.agents)
        print("================================")
        print(f"ACTIVE-{n_agents}: ROUND 1 (COLLABORATIVE PROPOSALS)")
        print("================================")

        tasks = [
            self.run_agent_micro_brief(
                agent_id,
                agent_file,
                task,
                project_context,
                stage_context,
            )
            for agent_id, agent_file in self.agents
        ]

        results = await asyncio.gather(*tasks)
        print("================================")
        print(f"ROUND 1 COMPLETED ({len(results)}/{n_agents} PROPOSALS)")
        print("================================")
        return results