"""
orchestrator/stages/ensemble_code_stage.py — Stage 3: 10-Agent Mob Coding & Direct File Writer
SuperSep v2.0

Triggered by: /gassep (--stage gas)
Pipeline state: ARCH_COMPLETED → CODE_COMPLETED

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
except ImportError:
    from router import GeminiRouter
    from state import CheckpointStateManager
    from triage import ProjectMemory


class EnsembleCodeStage:
    def __init__(
        self,
        router: GeminiRouter | None = None,
        state_manager: CheckpointStateManager | None = None,
    ):
        self.router = router or GeminiRouter()
        self.state_manager = state_manager or CheckpointStateManager()
        self.agents_dir = Path(__file__).resolve().parent.parent.parent / "agents"

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
                return content[:12000] + "\n\n[... truncated — see full blueprint file ...]"
            return content
        return ""

    async def run(
        self,
        task: str,
        safe_name: str,
        target_path: Path,
        project_context: str = "",
    ) -> dict[str, Any]:
        """
        Execute Stage 3: 5-Agent Ensemble Coding.

        Each agent contributes their specialized section.
        All generated files are written directly to target_path on disk.

        Args:
            task: The implementation task description.
            safe_name: Sanitized project name.
            target_path: Absolute path to the target project workspace.
            project_context: Stack conventions and decisions from memory.
        """
        print("\n" + "="*55)
        print("STAGE 3: ENSEMBLE CODING (10-AGENT MOB PROGRAMMING)")
        print("="*55)

        blueprint = self._load_blueprint(safe_name)
        if not blueprint:
            print("[Ensemble] Warning: No architecture blueprint found. Using task description only.")
            blueprint = f"Task: {task}"

        all_files: dict[str, str] = {}

        # Agent 1: Interaction logic, routing, form validation, dialog copy
        print("\n[Agent 1] Writing interaction logic, routing & micro-copy...")
        agent1_files = await self._run_agent_coding(
            agent_file="agent1.md",
            agent_id="agent_1",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 1 — Product Strategist & UX Flow):
Write the following code sections:
- Client-side routing logic and navigation handlers
- Form validation logic (client-side, using Zod on client)
- Dialog/modal state management and confirmation flows
- Error message copy and user-facing notification text
- Loading state orchestration (when to show skeletons vs spinners)
Output as JSON: {"files": [{"path": "relative/path/file.tsx", "content": "...full code..."}]}""",
        )
        all_files.update(agent1_files)

        # Agent 2: JSX layout, Tailwind styling, micro-animations
        print("\n[Agent 2] Writing JSX layout, Tailwind styling & animations...")
        agent2_files = await self._run_agent_coding(
            agent_file="agent2.md",
            agent_id="agent_2",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 2 — Design Systems & Visual Craftsman):
Write the following code sections:
- All UI component JSX/TSX files with complete Tailwind class specifications
- CSS module files for custom animations not achievable with Tailwind alone
- Responsive layout containers and grid systems
- Micro-animation CSS transitions (use Tailwind transition utilities)
- Design token constants file (colors, spacing, typography as JS/TS constants)
Output as JSON: {"files": [{"path": "relative/path/file.tsx", "content": "...full code..."}]}""",
        )
        all_files.update(agent2_files)

        # Agent 3: Zod schemas, API routes, data stores
        print("\n[Agent 3] Writing Zod schemas, Server Actions & data stores...")
        agent3_files = await self._run_agent_coding(
            agent_file="agent3.md",
            agent_id="agent_3",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 3 — Systems Architect & State/Data):
Write the following code sections:
- All Zod validation schemas (lib/schemas/*.ts)
- TypeScript interfaces and type definitions inferred from Zod
- Prisma schema additions/modifications (prisma/schema.prisma)
- Server Actions or API route handlers (app/api/**/route.ts or actions.ts)
- Global state stores if needed (zustand/jotai stores)
Output as JSON: {"files": [{"path": "relative/path/file.ts", "content": "...full code..."}]}""",
        )
        all_files.update(agent3_files)

        # Agent 4: Core computation logic, component integration (PRIMARY CODER)
        print("\n[Agent 4] Writing core production implementation (Primary Coder)...")
        agent4_files = await self._run_agent_coding(
            agent_file="agent4.md",
            agent_id="agent_4",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 4 — Principal Engineer, PRIMARY CODER):
You are the lead implementer. Your job is to:
1. Integrate all components from Agent 1, 2, and 3 into cohesive, working page-level code
2. Write the main page components (app/**/page.tsx)
3. Write shared utility functions (lib/utils/*.ts)
4. Write server-side data fetching functions with proper caching
5. Write the main layout files if needed (app/layout.tsx)
6. Ensure ALL imports reference the correct file paths
7. Zero placeholders. Zero TODOs. Every function must be complete.
Output as JSON: {"files": [{"path": "relative/path/file.tsx", "content": "...full code..."}]}""",
        )
        all_files.update(agent4_files)

        # Agent 5: Error boundaries, input sanitization, unit tests
        print("\n[Agent 5] Writing Error Boundaries, security sanitization & test suites...")
        agent5_files = await self._run_agent_coding(
            agent_file="agent5.md",
            agent_id="agent_5",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 5 — Adversarial QA, Security & Resilience):
Write the following code sections:
- Error Boundary components (app/**/error.tsx) for every route segment
- Input sanitization utilities (lib/security/sanitize.ts)
- Rate limiting middleware if needed (middleware.ts additions)
- Unit test files (*.test.ts / *.spec.ts) for critical business logic
- Integration test outlines for API routes
Output as JSON: {"files": [{"path": "relative/path/file.tsx", "content": "...full code..."}]}""",
        )
        all_files.update(agent5_files)

        # Agent 6: Infrastructure, deployment config, edge middleware
        print("\n[Agent 6] Writing infrastructure config, deployment & edge middleware...")
        agent6_files = await self._run_agent_coding(
            agent_file="agent6.md",
            agent_id="agent_6",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 6 — Cloud Infrastructure & Edge Scalability):
Write the following code sections:
- next.config.js / next.config.ts with edge runtime, image domains, and security headers
- Dockerfile and docker-compose.yml for containerized deployment
- GitHub Actions CI/CD workflow (.github/workflows/deploy.yml)
- Vercel / Cloudflare configuration files (vercel.json or wrangler.toml if applicable)
- Environment variable schema validation (lib/env.ts using zod or t3-env)
- Edge middleware for geo-routing, auth guards, or rate limiting (middleware.ts core logic)
Output as JSON: {"files": [{"path": "relative/path/file", "content": "...full code..."}]}""",
        )
        all_files.update(agent6_files)

        # Agent 7: Developer experience, automated testing infrastructure
        print("\n[Agent 7] Writing DX tooling, test infrastructure & mock handlers...")
        agent7_files = await self._run_agent_coding(
            agent_file="agent7.md",
            agent_id="agent_7",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 7 — Developer Experience & Automated Testing):
Write the following code sections:
- Vitest configuration (vitest.config.ts) and test setup files
- Playwright e2e test specs (e2e/*.spec.ts) for critical user flows
- MSW (Mock Service Worker) handlers for API mocking in tests (src/mocks/handlers.ts)
- Testing utilities and custom render helpers (test/utils.tsx)
- ESLint config (.eslintrc.json) and Prettier config (.prettierrc) for DX consistency
- package.json scripts for test, lint, build, and type-check commands
Output as JSON: {"files": [{"path": "relative/path/file", "content": "...full code..."}]}""",
        )
        all_files.update(agent7_files)

        # Agent 8: Accessibility, semantic HTML, ARIA, keyboard navigation
        print("\n[Agent 8] Writing accessibility layer, ARIA semantics & focus management...")
        agent8_files = await self._run_agent_coding(
            agent_file="agent8.md",
            agent_id="agent_8",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 8 — Accessibility, a11y & Cross-Platform UX):
Write the following code sections:
- Accessible component wrappers with complete ARIA attributes (role, aria-label, aria-describedby)
- Focus management utilities (lib/a11y/focus-trap.ts, lib/a11y/focus-visible.ts)
- Skip-navigation links and landmark regions (components/SkipNav.tsx)
- Keyboard navigation handlers for custom interactive components
- Screen reader announcements utility (lib/a11y/live-region.ts)
- Color contrast token verification and high-contrast mode CSS overrides
- WCAG 2.1 AA compliance checklist comments inline with relevant components
Output as JSON: {"files": [{"path": "relative/path/file.tsx", "content": "...full code..."}]}""",
        )
        all_files.update(agent8_files)

        # Agent 9: Database optimization, query performance, migrations
        print("\n[Agent 9] Writing database optimizations, migrations & query performance layer...")
        agent9_files = await self._run_agent_coding(
            agent_file="agent9.md",
            agent_id="agent_9",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 9 — Database Optimization & Query Performance):
Write the following code sections:
- Prisma migration files (prisma/migrations/) for any schema changes
- Optimized Prisma query helpers with proper select/include to avoid N+1 (lib/db/queries/*.ts)
- Database connection pooling configuration (lib/db/client.ts with PgBouncer or Prisma Accelerate)
- Database seed script (prisma/seed.ts) with realistic test data
- Indexes and constraints as SQL comments in schema or migration files
- Caching layer utilities (lib/cache/redis.ts or lib/cache/memory.ts) for expensive queries
Output as JSON: {"files": [{"path": "relative/path/file.ts", "content": "...full code..."}]}""",
        )
        all_files.update(agent9_files)

        # Agent 10: Holistic QA audit, integration checklist, release notes
        print("\n[Agent 10] Writing QA integration audit, release checklist & final synthesis...")
        agent10_files = await self._run_agent_coding(
            agent_file="agent10.md",
            agent_id="agent_10",
            task=task,
            blueprint=blueprint,
            project_context=project_context,
            assignment="""YOUR CODING ASSIGNMENT (Agent 10 — Holistic QA Gatekeeper & Release Readiness):
Write the following documents/code sections:
- RELEASE_CHECKLIST.md: Pre-launch quality gate checklist covering security, performance, a11y, API contracts, DB migrations
- INTEGRATION_AUDIT.md: Cross-agent integration review — identify any missing wiring between components from agents 1-9
- scripts/pre-flight.sh: Shell script that runs type-check, lint, test, and build in sequence and reports pass/fail
- docs/API_CONTRACTS.md: Final authoritative API contracts derived from the blueprint and agent 3's implementation
- docs/KNOWN_GAPS.md: Honest list of what was not implemented in this session and why (scope, complexity)
Output as JSON: {"files": [{"path": "relative/path/file", "content": "...full content..."}]}""",
        )
        all_files.update(agent10_files)

        # Write all files directly to target workspace
        written_files = self._write_files_to_workspace(all_files, target_path)

        # Advance pipeline state
        self.state_manager.advance(
            safe_name=safe_name,
            next_state="CODE_COMPLETED",
            metadata={
                "code_files_written": len(written_files),
                "target_path": str(target_path),
            },
        )

        print(f"\n✓ Ensemble coding complete. {len(written_files)} files written to {target_path}")

        return {
            "stage": "ensemble_code",
            "status": "completed",
            "files": all_files,
            "written_files": written_files,
            "target_path": str(target_path),
        }

    async def _run_agent_coding(
        self,
        agent_file: str,
        agent_id: str,
        task: str,
        blueprint: str,
        project_context: str,
        assignment: str,
    ) -> dict[str, str]:
        """Run a single agent's coding session. Returns {relative_path: content} dict."""
        role_prompt = self._load_agent_prompt(agent_file)

        system_prompt = f"""{role_prompt}

## PHASE 2: ASSEMBLY LINE — PRODUCTION CODING

You are now in the coding phase. The architecture has been approved.
Your mission: Write complete, production-ready code for your assigned section.

ZERO-PLACEHOLDER RULE: Every function you write must be complete. No TODO, no TBD, no "...".
If a function is too complex to complete in this response, break it into smaller, complete functions.

OUTPUT FORMAT (strictly JSON — no markdown fences):
{{"files": [{{"path": "relative/path/to/file.ext", "content": "complete file content here"}}]}}

If no code is needed for your assignment (rare), output: {{"files": []}}
"""

        user_prompt = f"""TASK: {task}

ARCHITECTURE BLUEPRINT:
{blueprint}

PROJECT CONTEXT:
{project_context or 'Standard Next.js 15 App Router with TypeScript, Tailwind CSS, Prisma ORM.'}

{assignment}

Write your assigned production code now. Output JSON only.
"""

        try:
            raw = await self.router.request(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
            )

            # Strip markdown code fences (model sometimes wraps in ```json)
            clean = re.sub(r"^```(?:json)?\n|```$", "", raw.strip(), flags=re.MULTILINE)

            parsed = json.loads(clean)
            files = parsed.get("files", [])

            result = {}
            for f in files:
                path = f.get("path", "").strip()
                content = f.get("content", "").strip()
                if path and content:
                    result[path] = content

            print(f"  [{agent_id}] Generated {len(result)} file(s)")
            return result

        except json.JSONDecodeError as e:
            print(f"  [{agent_id}] JSON parse error: {e}. Raw response stored as debug.")
            # Save raw response for debugging
            return {f"_debug_{agent_id}_raw.txt": raw}
        except Exception as e:
            print(f"  [{agent_id}] Coding ERROR: {type(e).__name__}: {e}")
            return {}

    def _write_files_to_workspace(
        self,
        files: dict[str, str],
        target_path: Path,
    ) -> list[str]:
        """Write all generated files to the target workspace. Returns list of written paths."""
        written = []
        target_path = Path(target_path)

        for relative_path, content in files.items():
            # Skip debug files
            if relative_path.startswith("_debug_"):
                debug_dir = Path(__file__).resolve().parent.parent.parent / "memory" / "_debug"
                debug_dir.mkdir(parents=True, exist_ok=True)
                (debug_dir / relative_path).write_text(content, encoding="utf-8")
                continue

            # Sanitize path — prevent directory traversal
            try:
                full_path = (target_path / relative_path).resolve()
                if not str(full_path).startswith(str(target_path.resolve())):
                    print(f"  [Security] Skipping suspicious path: {relative_path}")
                    continue
            except Exception:
                print(f"  [Warning] Invalid path: {relative_path}, skipping.")
                continue

            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            written.append(str(full_path))
            print(f"  ✓ Written: {relative_path}")

        return written
