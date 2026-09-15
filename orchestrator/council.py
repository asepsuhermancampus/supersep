import asyncio
import re
import yaml
from pathlib import Path
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
        system_prompt = f"""{role_prompt}

## Round 2: MATRIX DEBATE

You are now in Round 2 of the engineering council. You have access to the full analysis from all 5 agents.

Your mission: Review every agent's directives from your unique cognitive perspective. Endorse what is right, challenge what is wrong or incomplete, and propose unified decisions where there is conflict.

Be specific and substantive in your critique. Generic endorsements ("Agent X made good points") add no value.
Reference specific directives by name or number. Explain WHY you endorse or object.

Respond in YAML format:

endorse:
  - "Specific strong decision from [Agent X]: [what and why it's correct]"
objection:
  - "Critical challenge to [Agent Z]: [specific directive] is wrong because [concrete technical reason]"
consensus_vote:
  - "Unified decision: [specific, actionable resolution to any conflict]"
"""

        user_prompt = f"""COUNCIL MATRIX — ALL AGENT DIRECTIVES:
{matrix_context}

Apply your Chain-of-Thought protocol, then provide your expert matrix critique as {agent_id}.
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
                    "objection": [raw_response.strip()],
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
        n_agents = len(agent_prompts)
        print("================================")
        print(f"ACTIVE-{n_agents}: ROUND 2 (MATRIX DEBATE)")
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
        print(f"ROUND 2 COMPLETED ({len(critiques)}/{n_agents} DEBATES)")
        print("================================")
        return critiques

    async def synthesize_blueprint(
        self,
        task: str,
        briefs: List[Dict[str, Any]],
        debates: List[Dict[str, Any]],
        project_context: str = "",
        stage_focus: str = "",
    ) -> str:
        n_debates = len(debates)
        print("================================")
        print(f"ACTIVE-{n_debates}: ROUND 3 (BLUEPRINT SYNTHESIS)")
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

        stage_instruction = ""
        if stage_focus:
            stage_instruction = f"\nSTAGE FOCUS: {stage_focus}\n"

        system_prompt = f"""You are the Lead Master Architect synthesizing the final engineering consensus of an elite 10-agent council.

Your mission: Produce a single, production-grade, authoritative Master Architecture Blueprint that represents the best collective intelligence of all 10 agents.
{stage_instruction}
**Quality Standards (Non-Negotiable):**
- Zero vague placeholders. No "TBD", "TODO", or "implement later".
- Resolve ALL agent contradictions decisively with clear technical reasoning.
- Reference real-world patterns where applicable (Stripe API design, Vercel architecture, OWASP security, Prisma ORM conventions).
- Every requirement must have a concrete acceptance criterion.
- Every API endpoint must specify its 5-state response contract.
- Every component must have its complete state specification.

**Output Format (use clear Markdown sections):**
# [Project Name] Master Architecture Blueprint
## 1. System Overview & Tech Stack Decision
## 2. Database Schema & Data Models
## 3. API Contracts & 5-State Response Specifications
## 4. UI/UX Component Hierarchy & Design System Tokens
## 5. Security Architecture & Error Handling Strategy
## 6. Phased Assembly-Line Task Checklist (ordered by dependency)
"""

        user_prompt = f"""ORIGINAL TASK:
{task}

PROJECT CONTEXT:
{project_context or 'None provided'}

ROUND 1 — AGENT BRIEFS:
{matrix}

ROUND 2 — COUNCIL DEBATE:
{debates_summary}

Synthesize the final authoritative Master Blueprint now. Be comprehensive, specific, and production-grade.
"""

        blueprint = await self.router.request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        print("================================")
        print("ROUND 3 MASTER BLUEPRINT READY")
        print("================================")
        return blueprint