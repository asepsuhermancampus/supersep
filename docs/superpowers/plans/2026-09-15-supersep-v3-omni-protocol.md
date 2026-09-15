# SuperSep v3.0 — Omni Protocol Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Redesign SuperSep dari specialist 10-agent menjadi omniscient 10-agent dengan Full Parallel Omni Protocol (3-Round: full solutions → cross-critique → merged master) plus Self-Healing Council dan reliability improvements.

**Architecture:** Setiap agent punya knowledge identik (full-stack omniscient), dibedakan oleh thinking style/persona unik. Round 1: semua 10 hasilkan full solution simultan. Round 2: semua 10 cross-critique simultan. Round 3: synthesizer merge jadi Merged Master Output. Self-Healing: checkpoint + agent substitution jika 2+ agent gagal.

**Tech Stack:** Python 3.13, asyncio, httpx, dataclasses, PyYAML, python-dotenv, pytest, pytest-asyncio

**Spec:** `Dokumentasi/2026-09-15-supersep_v3.md`

## Global Constraints

- Python 3.13+ — gunakan `X | Y` union syntax
- Semua agent berjalan via `asyncio.gather(*tasks, return_exceptions=False)` — TIDAK sequential
- `AGENT_TIMEOUT_SECONDS=300`, `SYNTHESIS_TIMEOUT_SECONDS=600`, `RETRY_MAX_ATTEMPTS=5`
- `COUNCIL_QUORUM=9` — jika < 9 sukses, aktifkan Self-Healing (BUKAN stop)
- Jangan hapus backward compat untuk `--mode council/assembly/full` di `main.py`
- Semua config via `.env` — tidak ada magic number di kode
- Setiap fungsi publik wajib docstring
- Run `.venv\Scripts\python.exe -m pytest tests/ -v` setelah setiap task — wajib green
- Commit setelah setiap task selesai

---

## Task 1: Redesign 10 Agent Persona Files

**Files:** Modify `agents/agent1.md` through `agents/agent10.md`

**Interfaces:**
- Produces: agent persona strings di-load oleh `agent_runner.py:load_agent_prompt(path)`
- Format: Markdown — dibaca as-is sebagai system_prompt prefix

### Persona yang harus diimplementasikan:

Setiap file harus dimulai dengan header, diikuti blok **Omniscient Knowledge** yang identik untuk semua 10 agent, diikuti section **Cognitive Persona** yang unik.

**Blok Omniscient Knowledge (sama untuk semua 10 agent):**
```
You are a world-class full-stack engineer with complete mastery of:
routing, state management, form validation, UI/UX design, Tailwind CSS, animations,
Zod schemas, TypeScript, API routes, Server Actions, Prisma ORM, PostgreSQL,
Redis caching, Next.js App Router, authentication, authorization, OWASP security,
input sanitization, error handling, Docker, CI/CD, GitHub Actions, Vercel/Cloudflare,
Vitest, Playwright e2e, MSW, accessibility (WCAG 2.1), ARIA, performance optimization,
PWA, Web Vitals — and everything in modern web/application development.
```

**10 Persona Unik:**

| Agent | Persona | Core Thinking Style |
|---|---|---|
| agent1.md | The Conservative Guardian | Risk-averse: "Apa yang bisa rusak? Apa rollback-nya?" Pilih proven patterns. |
| agent2.md | The Innovator | Bleeding-edge: "Apa solusi paling modern?" Challenge konvensi. |
| agent3.md | The Adversarial Skeptic | Assume everything breaks. Devil's advocate. Security holes hunter. |
| agent4.md | The Pragmatist | Deadline-first. MVP mindset. YAGNI. Cut scope yang tidak esensial. |
| agent5.md | The Perfectionist | Clean code. SOLID. DRY. Zero tech debt. Naming > comments. |
| agent6.md | The Scalability Architect | 1M+ users mindset. Bottleneck hunter. Edge-first. Distributed. |
| agent7.md | The DX Champion | Team velocity. Fast CI. Test coverage. "Onboard dalam 1 hari?" |
| agent8.md | The User Advocate | Empathy-driven. WCAG 2.1. Real users. "Apakah user nyata bisa pakai ini?" |
| agent9.md | The Data Whisperer | Database-first. N+1 hunter. Query optimization. Migration safety. |
| agent10.md | The Synthesis Master | Meta-thinking. Arbitrator konflik. Sees the whole. Final quality gate. |

Setiap file diakhiri dengan section **Chain-of-Thought Protocol** berisi 5 pertanyaan khas persona tersebut.

- [ ] **Step 1: Rewrite agents/agent1.md** (The Conservative Guardian)
- [ ] **Step 2: Rewrite agents/agent2.md** (The Innovator)
- [ ] **Step 3: Rewrite agents/agent3.md** (The Adversarial Skeptic)
- [ ] **Step 4: Rewrite agents/agent4.md** (The Pragmatist)
- [ ] **Step 5: Rewrite agents/agent5.md** (The Perfectionist)
- [ ] **Step 6: Rewrite agents/agent6.md** (The Scalability Architect)
- [ ] **Step 7: Rewrite agents/agent7.md** (The DX Champion)
- [ ] **Step 8: Rewrite agents/agent8.md** (The User Advocate)
- [ ] **Step 9: Rewrite agents/agent9.md** (The Data Whisperer)
- [ ] **Step 10: Rewrite agents/agent10.md** (The Synthesis Master)

- [ ] **Step 11: Verify semua 10 file ada dan mulai dengan header yang benar**

```powershell
for ($i = 1; $i -le 10; $i++) { $h = (Get-Content "agents\agent$i.md")[0]; Write-Host "agent$i: $h" }
```

Expected: masing-masing `# Agent N — [Persona Name]`

- [ ] **Step 12: Run tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

Expected: 8 passed

- [ ] **Step 13: Commit**

```
git add agents/
git commit -m "feat(agents): redesign all 10 agent personas to omniscient full-stack with unique thinking styles"
```

---

## Task 2: Add Dataclasses + recovery.py

**Files:**
- Create: `orchestrator/models.py`
- Create: `orchestrator/recovery.py`
- Create: `tests/test_models.py`
- Create: `tests/test_recovery.py`

**Interfaces:**
- Produces:
  - `AgentSolution` dataclass (used by agent_runner, council, pipeline)
  - `AgentCritique` dataclass (used by council, pipeline)
  - `RecoveryManager` with: `save_checkpoint()`, `load_checkpoint()`, `cleanup_checkpoint()`, `get_failed_agents()`, `run_substitution()`

- [ ] **Step 1: Write failing tests — test_models.py**

```python
# tests/test_models.py
from orchestrator.models import AgentSolution, AgentCritique

def test_agent_solution_defaults():
    sol = AgentSolution(
        agent_id="agent_1", persona="The Conservative Guardian",
        status="success", solution="test", rationale="test",
        risks=[], improvements=[], artifacts="", raw=""
    )
    assert sol.error is None
    assert sol.status == "success"

def test_agent_solution_failed():
    sol = AgentSolution(
        agent_id="agent_1", persona="The Conservative Guardian",
        status="failed", solution="", rationale="",
        risks=[], improvements=[], artifacts="", raw="",
        error="TimeoutError"
    )
    assert sol.status == "failed"
    assert sol.error == "TimeoutError"

def test_agent_critique_defaults():
    crit = AgentCritique(
        agent_id="agent_3", persona="The Adversarial Skeptic",
        status="success",
        strengths_to_adopt=[{"from": "agent_1", "insight": "good"}],
        weaknesses_found=[{"in": "agent_2", "issue": "missing", "fix": "add"}],
        improvement_patches=["patch 1"],
        conflicts_to_resolve=[], raw=""
    )
    assert crit.error is None
    assert len(crit.strengths_to_adopt) == 1
```

Run: `.venv\Scripts\python.exe -m pytest tests/test_models.py -v` → FAIL expected

- [ ] **Step 2: Create orchestrator/models.py**

```python
"""
orchestrator/models.py — Shared dataclasses for SuperSep v3.0 Omni Protocol.
Replaces raw dict[str, Any] with typed, IDE-friendly dataclasses.
"""
from dataclasses import dataclass
from typing import Literal


@dataclass
class AgentSolution:
    """Output of a single agent in Round 1 (Full Parallel Solutions)."""
    agent_id: str
    persona: str
    status: Literal["success", "failed", "substituted"]
    solution: str
    rationale: str
    risks: list[str]
    improvements: list[str]
    artifacts: str
    raw: str
    error: str | None = None


@dataclass
class AgentCritique:
    """Output of a single agent in Round 2 (Cross-Agent Critique)."""
    agent_id: str
    persona: str
    status: Literal["success", "failed"]
    strengths_to_adopt: list[dict]
    weaknesses_found: list[dict]
    improvement_patches: list[str]
    conflicts_to_resolve: list[dict]
    raw: str
    error: str | None = None
```

- [ ] **Step 3: Run models tests → expect PASS**

```powershell
.venv\Scripts\python.exe -m pytest tests/test_models.py -v
```

- [ ] **Step 4: Write failing tests — test_recovery.py**

```python
# tests/test_recovery.py
import pytest
from pathlib import Path
from orchestrator.models import AgentSolution
from orchestrator.recovery import RecoveryManager

def make_sol(agent_id, status="success"):
    return AgentSolution(
        agent_id=agent_id, persona=f"Persona {agent_id}",
        status=status, solution="test", rationale="test",
        risks=[], improvements=[], artifacts="", raw="",
        error="timeout" if status == "failed" else None
    )

def test_save_and_load_checkpoint(tmp_path):
    mgr = RecoveryManager(checkpoint_base_dir=tmp_path)
    solutions = [make_sol(f"agent_{i}") for i in range(1, 11)]
    solutions[5].status = "failed"
    path = mgr.save_checkpoint("proj", solutions, task="build login")
    assert path.exists()
    loaded = mgr.load_checkpoint("proj")
    assert loaded["task"] == "build login"
    assert len(loaded["solutions"]) == 10

def test_cleanup_checkpoint(tmp_path):
    mgr = RecoveryManager(checkpoint_base_dir=tmp_path)
    solutions = [make_sol(f"agent_{i}") for i in range(1, 11)]
    mgr.save_checkpoint("proj", solutions, task="test")
    mgr.cleanup_checkpoint("proj")
    assert mgr.load_checkpoint("proj") is None

def test_get_failed_agents():
    mgr = RecoveryManager()
    solutions = [make_sol(f"agent_{i}") for i in range(1, 11)]
    solutions[2].status = "failed"
    solutions[7].status = "failed"
    failed = mgr.get_failed_agents(solutions)
    assert len(failed) == 2
    assert failed[0].agent_id == "agent_3"
```

Run: `.venv\Scripts\python.exe -m pytest tests/test_recovery.py -v` → FAIL expected

- [ ] **Step 5: Create orchestrator/recovery.py**

Key responsibilities:
- `save_checkpoint(project_name, solutions, task) -> Path` — JSON checkpoint ke `memory/projects/<name>/checkpoints/round1_partial_<ts>.json`
- `load_checkpoint(project_name) -> dict | None` — load checkpoint terbaru
- `cleanup_checkpoint(project_name) -> None` — hapus semua checkpoint setelah sukses
- `get_failed_agents(solutions) -> list[AgentSolution]` — filter status == "failed"
- `run_substitution(failed, available, task, task_type, router) -> list[AgentSolution]` — fire semua substitusi simultan via `asyncio.gather`

Substitution prompt template:
```
"You are stepping in as [persona of failed agent].
Think and respond EXACTLY as [persona name] would:
[persona description]
Produce a complete solution from this persona's perspective."
```

Output substituted agent: `AgentSolution(status="substituted")`

- [ ] **Step 6: Run all recovery tests → expect PASS**

```powershell
.venv\Scripts\python.exe -m pytest tests/test_models.py tests/test_recovery.py -v
```

- [ ] **Step 7: Run full suite**

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

Expected: all pass

- [ ] **Step 8: Commit**

```
git add orchestrator/models.py orchestrator/recovery.py tests/test_models.py tests/test_recovery.py
git commit -m "feat(core): add AgentSolution/AgentCritique dataclasses and RecoveryManager self-healing"
```

---

## Task 3: Upgrade router.py — Connection Pooling + Circuit Breaker

**Files:**
- Modify: `orchestrator/router.py`
- Modify: `.env`, `.env.example`

**Interfaces:**
- Produces: `GeminiRouter` with persistent `AsyncClient`, circuit breaker, `is_synthesis` flag

- [ ] **Step 1: Update .env dan .env.example**

Add these vars:
```env
AGENT_TIMEOUT_SECONDS=300
SYNTHESIS_TIMEOUT_SECONDS=600
RETRY_MAX_ATTEMPTS=5
COUNCIL_QUORUM=9
CHECKPOINT_DIR=memory/projects
MAX_SUBSTITUTION_ATTEMPTS=3
```

- [ ] **Step 2: Rewrite router.py**

Key changes:
1. **Persistent `AsyncClient`** — satu instance shared, `httpx.Limits(max_connections=10, max_keepalive_connections=10)`, bukan buat baru per request
2. **Circuit breaker** — class-level state: `_failure_count`, `_circuit_open_since`. Trip setelah 5 failures dalam 30s. Auto-reset setelah 60s. Raise `CircuitBreakerOpen` exception.
3. **Retry schedule** — `[0, 2, 5, 10, 20]` seconds delays (5 attempts total dari `RETRY_MAX_ATTEMPTS`)
4. **`is_synthesis` parameter** — `request(…, is_synthesis=False)`. Jika True gunakan `SYNTHESIS_TIMEOUT_SECONDS` untuk read timeout
5. **`async def close()`** — untuk cleanup `AsyncClient` saat done
6. **`_record_success()` / `_record_failure()`** — update circuit breaker state

```python
class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open (9Router appears to be down)."""
    pass

class GeminiRouter:
    _failure_count: int = 0            # class-level circuit breaker state
    _circuit_open_since: float | None = None
    _CIRCUIT_TRIP_THRESHOLD = 5
    _CIRCUIT_RESET_SECONDS = 60
```

- [ ] **Step 3: Run full tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

Expected: all pass

- [ ] **Step 4: Commit**

```
git add orchestrator/router.py .env .env.example
git commit -m "feat(router): persistent AsyncClient, circuit breaker, configurable timeouts, is_synthesis flag"
```

---

## Task 4: Redesign agent_runner.py — Round 1 Full Parallel Solutions

**Files:**
- Modify: `orchestrator/agent_runner.py`

**Interfaces:**
- Consumes: `AgentSolution` from `orchestrator.models`, `GeminiRouter`
- Produces:
  - `run_all_solutions(task, task_type, project_context) -> list[AgentSolution]` ← PRIMARY
  - `run_micro_briefs(...)` ← backward-compat wrapper (still works)

- [ ] **Step 1: Rewrite agent_runner.py**

Key structure:

```python
AGENT_PERSONAS = {
    "agent_1": "The Conservative Guardian",
    "agent_2": "The Innovator",
    # ... all 10
}

ROUND1_OUTPUT_FORMAT = """
Respond in JSON (no markdown fences):
{
  "solution": "Complete solution from your persona perspective...",
  "rationale": "Why you chose this approach...",
  "risks": ["Risk 1 with scenario...", "Risk 2..."],
  "improvements": ["What could be even better..."],
  "artifacts": "Code / design / plan relevant to the task..."
}"""

class AgentRunner:
    async def run_single_solution(self, agent_id, agent_file, task, task_type, project_context="") -> AgentSolution:
        """Round 1: single agent produces full solution. Catches all exceptions → returns status='failed'."""

    async def run_all_solutions(self, task, task_type="mixed", project_context="") -> list[AgentSolution]:
        """Round 1: asyncio.gather all 10 simultaneously. Logs success/fail counts."""

    async def run_micro_briefs(self, task, project_context="", stage_context="") -> list[dict]:
        """Backward-compat: calls run_all_solutions() and converts to v2.0 dict format."""
```

Round 1 prompt instruction to each agent:
```
## ROUND 1: FULL SOLUTION — OMNISCIENT COUNCIL PROTOCOL
You are participating in Round 1 of the SuperSep 10-agent Omniscient Council.
TASK TYPE: {task_type}
Your mission: Provide a COMPLETE, production-grade solution for the given task
from your unique cognitive persona. NOT a brief — your full expert answer.
```

JSON parse failure fallback: store raw response as `solution`, mark status `"success"` (model answered, just non-JSON).

- [ ] **Step 2: Run full tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

- [ ] **Step 3: Commit**

```
git add orchestrator/agent_runner.py
git commit -m "feat(runner): redesign Round 1 to full parallel solutions using AgentSolution dataclass"
```

---

## Task 5: Redesign council.py — Round 2 Cross-Critique + Round 3 Merged Master

**Files:**
- Modify: `orchestrator/council.py`

**Interfaces:**
- Consumes: `list[AgentSolution]`, `list[AgentCritique]` from `orchestrator.models`
- Produces:
  - `run_cross_critique(solutions) -> list[AgentCritique]` ← Round 2
  - `synthesize_merged_master(task, solutions, critiques, task_type, ...) -> str` ← Round 3
  - `build_lean_matrix()`, `matrix_debate()`, `synthesize_blueprint()` ← backward-compat

- [ ] **Step 1: Rewrite council.py**

**Round 2 prompt to each agent:**
```
## ROUND 2: CROSS-AGENT CRITIQUE & IMPROVEMENT
You have all 10 agents' Round 1 solutions. From your persona's lens, critique them.
1. Identify SPECIFIC strengths from other agents to adopt
2. Find SPECIFIC weaknesses/gaps with concrete fixes
3. Write CONCRETE improvement patches for the final output
4. Resolve CONFLICTS between agents with decisive reasoning
```

**Round 2 output format (JSON):**
```json
{
  "strengths_to_adopt": [{"from": "agent_X", "insight": "..."}],
  "weaknesses_found": [{"in": "agent_X", "issue": "...", "fix": "..."}],
  "improvement_patches": ["Patch 1...", "Patch 2..."],
  "conflicts_to_resolve": [{"between": ["agent_A", "agent_B"], "conflict": "...", "resolution": "..."}]
}
```

**Round 3 synthesizer non-negotiable rules (in system prompt):**
```
1. EVERY agent MUST contribute at least 1 element to the final output
2. EVERY weakness_found MUST be addressed
3. EVERY conflict_to_resolve MUST be resolved with explicit reasoning
4. EVERY improvement_patch evaluated and integrated if valid
5. ZERO GAPS — if a gap was identified, fill it completely
```

Round 3 uses `router.request(…, is_synthesis=True)` for extended timeout.

Task-type output instructions map:
```python
OUTPUT_INSTRUCTIONS = {
    "brainstorm": "Master Architecture Blueprint in Markdown",
    "ui_ux": "Design System Spec + Component Hierarchy",
    "slicing": "Complete component code + design tokens",
    "coding": "Production-ready merged code files. Zero placeholders.",
    "fix_error": "Root cause + complete fix + prevention strategy",
    "security": "Threat model + remediation + hardened code",
    "optimization": "Performance audit + optimized code + metrics",
    "mixed": "Comprehensive Markdown output covering all aspects",
}
```

Backward-compat methods:
- `build_lean_matrix(briefs)` — still works (returns string matrix)
- `matrix_debate()` — returns empty list (deprecated)
- `synthesize_blueprint(task, briefs, debates, ...)` — converts briefs → AgentSolution, calls `synthesize_merged_master`

- [ ] **Step 2: Run full tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

- [ ] **Step 3: Commit**

```
git add orchestrator/council.py
git commit -m "feat(council): Round 2 cross-critique + Round 3 merged master with zero-gap synthesis rules"
```

---

## Task 6: Wire Self-Healing into pipeline.py + Redesign ensemble_code_stage.py

**Files:**
- Modify: `orchestrator/pipeline.py`
- Modify: `orchestrator/stages/ensemble_code_stage.py`

**Interfaces:**
- Consumes: `RecoveryManager`, `AgentRunner.run_all_solutions()`, `Council.run_cross_critique()`, `Council.synthesize_merged_master()`

- [ ] **Step 1: Update pipeline.py council flow**

Replace call to `runner.run_micro_briefs()` + `council.matrix_debate()` with v3.0 flow:

```python
from orchestrator.recovery import RecoveryManager
import os

# Round 1
solutions = await runner.run_all_solutions(task=task, task_type=task_type, project_context=ctx)

# Self-healing check
failed = [s for s in solutions if s.status == "failed"]
quorum = int(os.getenv("COUNCIL_QUORUM", "9"))
recovery = RecoveryManager()
safe_name = triage.detect_project(target_path).safe_name if target_path else "default"

if len(failed) >= (10 - quorum + 1):  # 2+ failures triggers self-healing
    recovery.save_checkpoint(safe_name, solutions, task)
    available = [s for s in solutions if s.status == "success"]
    substituted = await recovery.run_substitution(failed, available, task, task_type, router)
    sol_map = {s.agent_id: s for s in solutions}
    for sub in substituted:
        sol_map[sub.agent_id] = sub
    solutions = list(sol_map.values())

# Round 2
critiques = await council.run_cross_critique(solutions)

# Round 3
blueprint = await council.synthesize_merged_master(
    task=task, solutions=solutions, critiques=critiques,
    task_type=task_type, project_context=ctx, stage_focus=stage_focus
)

# Cleanup
if len(failed) >= (10 - quorum + 1):
    recovery.cleanup_checkpoint(safe_name)
```

- [ ] **Step 2: Redesign ensemble_code_stage.py**

Replace 10-agent-section approach with Omni Protocol:

```python
async def run(self, task, safe_name, target_path, project_context=""):
    """Stage 3: 10-Agent Omni Coding — all agents write full implementations, synthesizer merges."""
    print("STAGE 3: ENSEMBLE CODING (10-AGENT OMNI PROTOCOL)")

    blueprint = self._load_blueprint(safe_name)
    full_task = f"{task}\n\nARCHITECTURE BLUEPRINT:\n{blueprint}" if blueprint else task

    # Round 1: all 10 write complete implementations
    solutions = await self.runner.run_all_solutions(
        task=full_task, task_type="coding", project_context=project_context
    )

    # Self-healing if needed
    # [same self-healing logic as pipeline.py]

    # Round 2: cross-critique
    critiques = await self.council.run_cross_critique(solutions)

    # Round 3: merged master code
    merged = await self.council.synthesize_merged_master(
        task=full_task, solutions=solutions, critiques=critiques,
        task_type="coding", project_context=project_context
    )

    # Write files to disk
    written = self._write_files_from_synthesis(merged, target_path)
    self.state_manager.advance(safe_name=safe_name, next_state="CODE_COMPLETED", ...)
    return {"stage": "ensemble_code", "status": "completed", "written_files": written}
```

Add `_write_files_from_synthesis(synthesis, target_path) -> list[str]`:
- Try parse JSON `{"files": [{"path": "...", "content": "..."}]}`
- Fallback: write entire synthesis as `SUPERSEP_IMPLEMENTATION.md`

- [ ] **Step 3: Run full tests**

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v
```

- [ ] **Step 4: Commit**

```
git add orchestrator/pipeline.py orchestrator/stages/ensemble_code_stage.py
git commit -m "feat(pipeline): wire v3.0 Omni Protocol + Self-Healing Council into pipeline and ensemble stage"
```

---

## Task 7: Update skills/mikirsep/SKILL.md + skills/gassep/SKILL.md

**Files:**
- Modify: `skills/mikirsep/SKILL.md`
- Modify: `skills/gassep/SKILL.md`

- [ ] **Step 1: Update mikirsep/SKILL.md — tambahkan section v3.0**

Tambahkan di atas section "Cara Menjalankan":
```markdown
## v3.0 — Omniscient 10-Agent Council Protocol

Semua 10 agent menghasilkan full solution simultan (bukan brief).

**Round 1:** 10 agents → full plans parallel (~15-30s)
**Round 2:** 10 agents → cross-critique parallel (~15-30s)
**Round 3:** Synthesizer → Merged Master Blueprint (~30-60s)
**Total: ~60-120 detik**

Self-Healing: jika 1 agent gagal → synthesizer kompensasi.
Jika 2+ gagal → agent substitution otomatis, checkpoint saved.
```

- [ ] **Step 2: Update gassep/SKILL.md — describe v3.0 coding**

Update deskripsi dari "Agent 1 tulis routing, Agent 2 tulis UI..." menjadi:
"Semua 10 agent menulis implementasi LENGKAP secara simultan, kemudian saling cross-critique, dan synthesizer menghasilkan merged production code terbaik dari semua 10 implementasi."

- [ ] **Step 3: Commit**

```
git add skills/
git commit -m "docs(skills): update mikirsep and gassep SKILL.md for v3.0 Omni Protocol"
```

---

## Task 8: Final Verification + Push

- [ ] **Step 1: Run complete test suite — must be 100% green**

```powershell
.venv\Scripts\python.exe -m pytest tests/ -v --tb=short
```

Expected: ALL tests pass, 0 errors, 0 failures

- [ ] **Step 2: Verify agent files**

```powershell
for ($i = 1; $i -le 10; $i++) {
    Write-Host "agent$i.md:" ((Get-Content "agents\agent$i.md")[0])
}
```

Expected: `# Agent N — [Persona Name]` untuk setiap file

- [ ] **Step 3: Verify .env completeness**

```powershell
Get-Content .env
```

Expected: semua 10 keys ada:
`ROUTER_BASE_URL`, `ROUTER_API_KEY`, `MODEL`, `ROUTER_CONCURRENCY`, `COUNCIL_QUORUM`, `AGENT_TIMEOUT_SECONDS`, `SYNTHESIS_TIMEOUT_SECONDS`, `RETRY_MAX_ATTEMPTS`, `CHECKPOINT_DIR`, `MAX_SUBSTITUTION_ATTEMPTS`

- [ ] **Step 4: Final commit dan push**

```bash
git add -A
git commit -m "feat(v3): SuperSep v3.0 Omniscient 10-Agent Omni Protocol — COMPLETE

- Task 1: 10 omniscient agent personas with unique thinking styles
- Task 2: AgentSolution + AgentCritique dataclasses + RecoveryManager
- Task 3: Router upgraded: connection pooling, circuit breaker, configurable timeouts
- Task 4: agent_runner.py redesigned for Round 1 full parallel solutions
- Task 5: council.py redesigned: Round 2 cross-critique + Round 3 merged master
- Task 6: pipeline.py + ensemble_code_stage.py wired with v3.0 Omni Protocol + self-healing
- Task 7: Skills updated for v3.0
All tests pass. Zero backward-compat breaks."

git push -u origin main
```

---

## Ringkasan Task Dependencies

```
Task 1 (agents) → independent
Task 2 (models + recovery) → independent
Task 3 (router) → independent
Task 4 (agent_runner) → needs Task 2 (models), Task 3 (router)
Task 5 (council) → needs Task 2 (models), Task 3 (router)
Task 6 (pipeline) → needs Task 4 + Task 5
Task 7 (skills) → needs Task 4 + Task 5 for content accuracy
Task 8 (verify) → needs all tasks
```

Tasks 1, 2, 3 dapat dikerjakan **paralel**. Tasks 4 & 5 dapat dikerjakan **paralel** setelah Task 2 & 3 selesai.

---

*Plan selesai. 8 tasks, coverage penuh dari spec `Dokumentasi/2026-09-15-supersep_v3.md`*
