from pathlib import Path
from typing import Dict, Any

try:
    from orchestrator.router import GeminiRouter
except ImportError:
    from router import GeminiRouter


class AssemblyLine:
    def __init__(self, router: GeminiRouter | None = None):
        self.router = router or GeminiRouter()
        self.agents_dir = Path(__file__).resolve().parent.parent / "agents"

    def _load_prompt(self, agent_file: str) -> str:
        p = self.agents_dir / agent_file
        if p.exists():
            return p.read_text(encoding="utf-8")
        return ""

    async def generate_ui_spec(self, blueprint: str) -> str:
        agent_prompt = self._load_prompt("agent2.md")
        system_prompt = f"""
{agent_prompt}

You are in PHASE 2: ASSEMBLY LINE (UI SPECIFICATION).
Based on the approved Blueprint, define the exact UI component specifications, layout structure, responsive rules, and styling tokens.
Do NOT write backend logic. Focus on component props, UI state, CSS classes, and micro-interactions.
"""
        user_prompt = f"""
APPROVED BLUEPRINT:
{blueprint}

Produce the Component & UI Design Specification.
"""
        return await self.router.request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    async def generate_data_spec(self, blueprint: str) -> str:
        agent_prompt = self._load_prompt("agent3.md")
        system_prompt = f"""
{agent_prompt}

You are in PHASE 2: ASSEMBLY LINE (DATA & ARCHITECTURE SPECIFICATION).
Based on the approved Blueprint, define the exact TypeScript interfaces, database schemas, API request/response payloads, and state flow.
Do NOT write full frontend layout code. Focus on data contracts, types, and endpoints.
"""
        user_prompt = f"""
APPROVED BLUEPRINT:
{blueprint}

Produce the Data Models, Interfaces & API Contracts Specification.
"""
        return await self.router.request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    async def implement_code(
        self,
        task: str,
        ui_spec: str,
        data_spec: str,
    ) -> str:
        agent_prompt = self._load_prompt("agent4.md")
        system_prompt = f"""
{agent_prompt}

You are the SOLE LEAD IMPLEMENTER in PHASE 2: ASSEMBLY LINE.
Synthesize the UI Specification and the Data Specification into complete, robust, production-ready code.
Follow clean architecture, zero placeholders (no TODO/TBD), proper error boundaries, and idiomatic practices.
"""
        user_prompt = f"""
TASK:
{task}

UI SPECIFICATION:
{ui_spec}

DATA & ARCHITECTURE SPECIFICATION:
{data_spec}

Generate the complete production implementation code now.
"""
        return await self.router.request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    async def adversarial_review(
        self,
        code: str,
        requirements: str,
    ) -> Dict[str, Any]:
        agent_prompt = self._load_prompt("agent5.md")
        system_prompt = f"""
{agent_prompt}

You are the GATEKEEPER / ADVERSARIAL QA in PHASE 2: ASSEMBLY LINE.
Thoroughly audit the generated implementation against requirements, security (injection, XSS, auth bypass), race conditions, error resilience, and edge cases.

Structure your review:
## Verification Status: [PASS / FAIL]
## Security & Vulnerability Analysis
## Edge Cases & Error Handling
## Code Quality & Performance Bottlenecks
## Mandatory Fixes (if any)
"""
        user_prompt = f"""
ORIGINAL REQUIREMENTS:
{requirements}

GENERATED CODE TO AUDIT:
{code}

Audit this code adversarially now.
"""
        review_text = await self.router.request(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        status = "fail" if "status: fail" in review_text.lower() or "verification status: [fail]" in review_text.lower() else "success"

        return {
            "status": status,
            "critique": review_text,
        }
