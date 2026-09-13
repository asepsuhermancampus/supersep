import asyncio
import re
import yaml
from typing import List, Dict, Any

try:
    from orchestrator.router import GeminiRouter
except ImportError:
    from router import GeminiRouter


class Council:
    def __init__(self, router: GeminiRouter | None = None):
        self.router = router or GeminiRouter()

    def build_lean_matrix(self, briefs: List[Dict[str, Any]]) -> str:
        lines = ["### ROUND 1: AGENT DIRECTIVES MATRIX\n"]
        for b in briefs:
            agent_id = b.get("agent_id", "unknown")
            status = b.get("status", "unknown")
            lines.append(f"#### [{agent_id}] (Status: {status})")

            directives = b.get("directives", [])
            constraints = b.get("constraints", [])
            red_flags = b.get("red_flags", [])

            if directives:
                lines.append("**Directives:**")
                for d in directives:
                    lines.append(f"- {d}")

            if constraints:
                lines.append("**Constraints:**")
                for c in constraints:
                    lines.append(f"- {c}")

            if red_flags:
                lines.append("**Red Flags / Risks:**")
                for rf in red_flags:
                    lines.append(f"- {rf}")

            lines.append("")

        return "\n".join(lines)

    async def critique_matrix_agent(
        self,
        agent_id: str,
        role_prompt: str,
        matrix_context: str,
    ) -> Dict[str, Any]:
        system_prompt = f"""
{role_prompt}

CRITICAL TOKEN CONSTRAINT:
You are in ROUND 2: MATRIX DEBATE.
Review the directives produced by ALL 5 agents.
Do NOT write essays. Output strictly in this YAML format (maximum 150 words total):

endorse:
  - "Strong decision from Agent X on Y"
objection:
  - "Critical challenge to Agent Z on W because of R"
consensus_vote:
  - "Recommended unified decision on item V"
"""

        user_prompt = f"""
COUNCIL MATRIX:
{matrix_context}

Provide your matrix critique as {agent_id} in strict YAML format.
"""

        try:
            raw_response = await self.router.request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            clean_yaml = re.sub(r"^```(?:yaml)?\n|```$", "", raw_response.strip(), flags=re.MULTILINE)
            parsed = {}
            try:
                parsed = yaml.safe_load(clean_yaml) or {}
            except Exception:
                parsed = {
                    "endorse": [],
                    "objection": [raw_response.strip()[:200]],
                    "consensus_vote": [],
                }

            print(f"[{agent_id}] Matrix Debate Completed")

            return {
                "agent_id": agent_id,
                "status": "success",
                "endorse": parsed.get("endorse", []),
                "objection": parsed.get("objection", []),
                "consensus_vote": parsed.get("consensus_vote", []),
                "raw": raw_response.strip(),
            }

        except Exception as e:
            print(f"[{agent_id}] ERROR {type(e).__name__}: {e!r}")
            return {
                "agent_id": agent_id,
                "status": "error",
                "endorse": [],
                "objection": [],
                "consensus_vote": [],
                "error": f"{type(e).__name__}: {e!r}",
                "raw": "",
            }

    async def matrix_debate(
        self,
        briefs: List[Dict[str, Any]],
        agent_prompts: Dict[str, str],
    ) -> List[Dict[str, Any]]:
        print("================================")
        print("ACTIVE-5: ROUND 2 (MATRIX DEBATE)")
        print("================================")

        matrix_context = self.build_lean_matrix(briefs)
        tasks = []

        for agent_id, role_prompt in agent_prompts.items():
            tasks.append(
                self.critique_matrix_agent(
                    agent_id,
                    role_prompt,
                    matrix_context,
                )
            )

        critiques = await asyncio.gather(*tasks)
        print("================================")
        print("ROUND 2 COMPLETED (5/5 DEBATES)")
        print("================================")
        return critiques

    async def synthesize_blueprint(
        self,
        task: str,
        briefs: List[Dict[str, Any]],
        debates: List[Dict[str, Any]],
        project_context: str = "",
    ) -> str:
        print("================================")
        print("ACTIVE-5: ROUND 3 (BLUEPRINT SYNTHESIS)")
        print("================================")

        matrix = self.build_lean_matrix(briefs)

        debate_lines = ["### COUNCIL DEBATE CONSENSUS\n"]
        for d in debates:
            agent_id = d.get("agent_id", "unknown")
            debate_lines.append(f"**[{agent_id}]**")
            for e in d.get("endorse", []):
                debate_lines.append(f"+ Endorse: {e}")
            for o in d.get("objection", []):
                debate_lines.append(f"- Objection: {o}")
            for c in d.get("consensus_vote", []):
                debate_lines.append(f"= Vote: {c}")
            debate_lines.append("")

        debates_summary = "\n".join(debate_lines)

        system_prompt = """
You are the Lead Master Architect synthesizing the final engineering consensus of an elite 5-agent council.
Your goal is to produce a single, production-grade, authoritative Master Architecture Blueprint.
Resolve all agent contradictions decisively based on best engineering practices.
Do NOT leave unresolved questions or vague placeholders.

Format with clear Markdown:
# [Project Name] Master Architecture Blueprint
## 1. System Overview & Tech Stack Selection
## 2. API Contracts & Data Interface Schema
## 3. UI/UX Hierarchy & Interaction Specification
## 4. Security, Error Handling & Failure Modes
## 5. Phased Assembly-Line Task Checklist
"""

        user_prompt = f"""
ORIGINAL TASK:
{task}

PROJECT CONTEXT:
{project_context or 'None provided'}

ROUND 1 BRIEFS:
{matrix}

ROUND 2 DEBATES:
{debates_summary}

Synthesize the final authoritative Master Blueprint now.
"""

        blueprint = await self.router.request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        print("================================")
        print("ROUND 3 MASTER BLUEPRINT READY")
        print("================================")
        return blueprint