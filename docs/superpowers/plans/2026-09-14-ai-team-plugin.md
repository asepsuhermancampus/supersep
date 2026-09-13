# AI-Team Plugin & Dual-Phase Multi-Agent Engine Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a reusable, token-optimized Antigravity plugin and dual-phase multi-agent engine (`ai-team`) with project-scoped memory, Active-5 lean debate, assembly-line coding execution, and curated self-learning.

**Architecture:** A dual-phase architecture where Phase 1 (Council) coordinates all 5 agents using micro-briefs and matrix debate to establish a locked architectural plan, and Phase 2 (Assembly Line) produces code through specialized pipelines (UI Spec ➔ Architecture Types ➔ Senior Dev implementation ➔ Adversarial QA). Scoped project memory is automatically detected from the workspace parent directory name, and new knowledge is distilled with an explicit user approval gate.

**Tech Stack:** Python 3.10+, `httpx`, `dotenv`, `pyyaml`, Antigravity Plugin & Custom Skills SDK.

**Spec:** [docs/superpowers/specs/2026-09-14-ai-team-plugin-design.md](file:///c:/Users/asep.suherman/SETTUP%20TESTING/Build%20Project%20In%20Here/IDE/ai-team-gemini-3.8_flash/docs/superpowers/specs/2026-09-14-ai-team-plugin-design.md)

## Global Constraints
- Target 9Router Combo: `MODEL=5_gemini_3.8_flash_by_antigravity`.
- Strict Token Budgets: Round 1 Micro-Briefs <= 200 tokens per agent; Round 2 Matrix Critiques <= 200 tokens per agent.
- All 5 agents must remain active in Phase 1 (no sleep/skipping).
- In Phase 2, `agent_4` (Senior Developer) is the sole code generator; `agent_5` is the adversarial reviewer; `agent_2` & `agent_3` provide component and data specs.
- Project memory is isolated under `memory/projects/<parent_dir_name>/` and must never overwrite unrelated project records.
- Learning updates must prompt for user confirmation before writing to markdown files.

---

### Task 1: Project-Scoped Memory & Workspace Detector (`orchestrator/triage.py`)

**Files:**
- Create: `orchestrator/triage.py`
- Create: `tests/test_triage.py`

**Interfaces:**
- Produces: `WorkspaceDetector.detect_project(cwd: str | Path) -> dict`
- Produces: `ProjectMemory.load(project_name: str) -> dict`
- Produces: `ProjectMemory.save_context(project_name: str, context: dict) -> None`
- Produces: `ProjectMemory.append_decision(project_name: str, decision: str) -> None`

- [ ] **Step 1: Write failing unit test for WorkspaceDetector and ProjectMemory**

Create `tests/test_triage.py`:
```python
import tempfile
from pathlib import Path
import pytest
from orchestrator.triage import WorkspaceDetector, ProjectMemory

def test_detect_project_extracts_folder_name():
    path = Path("C:/Users/asep/Projects/HariKita - Web App/subfolder")
    detector = WorkspaceDetector()
    project_info = detector.detect(path)
    assert project_info["name"] == "HariKita - Web App"
    assert project_info["safe_name"] == "HariKita-Web-App"

def test_project_memory_create_and_load():
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(base_dir=Path(tmpdir))
        memory.save_context("Test-Project", {"tech_stack": ["Next.js", "Tailwind"]})
        loaded = memory.load("Test-Project")
        assert loaded["context"]["tech_stack"] == ["Next.js", "Tailwind"]

def test_project_memory_append_decision():
    with tempfile.TemporaryDirectory() as tmpdir:
        memory = ProjectMemory(base_dir=Path(tmpdir))
        memory.append_decision("Test-Project", "Use cookie-based auth")
        loaded = memory.load("Test-Project")
        assert "Use cookie-based auth" in loaded["decisions"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_triage.py`
Expected: FAIL (ModuleNotFoundError or ImportError)

- [ ] **Step 3: Implement `orchestrator/triage.py`**

```python
import json
import re
from pathlib import Path
from typing import Dict, Any

class WorkspaceDetector:
    def __init__(self, root_dir: Path | None = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent

    def detect(self, current_path: Path | str | None = None) -> Dict[str, str]:
        if current_path is None:
            current_path = Path.cwd()
        else:
            current_path = Path(current_path)

        # Detect the top-level project folder (e.g. parent of IDE or immediate workspace)
        project_name = current_path.name
        # Sanitize name for filesystem
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '-', project_name).strip('-')

        return {
            "name": project_name,
            "safe_name": safe_name,
            "path": str(current_path),
        }

class ProjectMemory:
    def __init__(self, base_dir: Path | None = None):
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "memory"
        self.base_dir = base_dir
        self.projects_dir = self.base_dir / "projects"
        self.projects_dir.mkdir(parents=True, exist_ok=True)

    def _get_project_dir(self, safe_name: str) -> Path:
        pdir = self.projects_dir / safe_name
        pdir.mkdir(parents=True, exist_ok=True)
        return pdir

    def load(self, safe_name: str) -> Dict[str, Any]:
        pdir = self._get_project_dir(safe_name)
        ctx_file = pdir / "context.json"
        decisions_file = pdir / "decisions.md"

        context = {}
        if ctx_file.exists():
            try:
                context = json.loads(ctx_file.read_text(encoding="utf-8"))
            except Exception:
                context = {}

        decisions = ""
        if decisions_file.exists():
            decisions = decisions_file.read_text(encoding="utf-8")

        return {
            "project": safe_name,
            "context": context,
            "decisions": decisions,
        }

    def save_context(self, safe_name: str, context: Dict[str, Any]) -> None:
        pdir = self._get_project_dir(safe_name)
        ctx_file = pdir / "context.json"
        ctx_file.write_text(json.dumps(context, indent=2), encoding="utf-8")

    def append_decision(self, safe_name: str, decision: str) -> None:
        pdir = self._get_project_dir(safe_name)
        decisions_file = pdir / "decisions.md"
        with open(decisions_file, "a", encoding="utf-8") as f:
            f.write(f"\n- {decision.strip()}\n")
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_triage.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add orchestrator/triage.py tests/test_triage.py
git commit -m "feat(triage): add workspace detector and project-scoped memory"
```

---

### Task 2: Active-5 Lean Protocol Implementation (`orchestrator/agent_runner.py` & `council.py`)

**Files:**
- Modify: `orchestrator/agent_runner.py`
- Modify: `orchestrator/council.py`
- Create: `tests/test_lean_council.py`

**Interfaces:**
- Consumes: `GeminiRouter` in `orchestrator/router.py`
- Produces: `AgentRunner.run_micro_briefs(task: str, project_context: str) -> list[dict]`
- Produces: `Council.matrix_debate(micro_briefs: list[dict]) -> list[dict]`
- Produces: `Council.synthesize_blueprint(task: str, micro_briefs: list[dict], debate: list[dict]) -> str`

- [ ] **Step 1: Write test for Micro-Brief and Matrix Debate prompt format**

Create `tests/test_lean_council.py`:
```python
import pytest
from orchestrator.council import Council

def test_build_lean_matrix():
    council = Council()
    mock_briefs = [
        {
            "agent_id": "agent_1",
            "directives": ["Direct A"],
            "constraints": ["Const A"],
            "red_flags": ["Risk A"],
        },
        {
            "agent_id": "agent_2",
            "directives": ["Direct B"],
            "constraints": ["Const B"],
            "red_flags": ["Risk B"],
        }
    ]
    matrix = council.build_lean_matrix(mock_briefs)
    assert "[agent_1]" in matrix
    assert "Direct A" in matrix
    assert "[agent_2]" in matrix
    assert len(matrix) < 2000  # Enforce lean token size
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_lean_council.py`
Expected: FAIL with AttributeError (`build_lean_matrix`)

- [ ] **Step 3: Update `orchestrator/agent_runner.py` with Micro-Brief extraction**

Update `AgentRunner.run_micro_briefs`:
- Inject concise structured system instructions capping output to 200 tokens:
```python
MICRO_BRIEF_PROMPT = """
You are participating in Round 1: Micro-Briefs.
Analyze the task strictly from your role. Do NOT write prose or essays.
You MUST output strictly in this YAML format (maximum 150 words):

directives:
  - "Core directive 1"
  - "Core directive 2"
  - "Core directive 3"
constraints:
  - "Technical constraint 1"
  - "Technical constraint 2"
red_flags:
  - "Critical risk 1"
  - "Critical risk 2"
"""
```

- [ ] **Step 4: Update `orchestrator/council.py` with Matrix Debate & Blueprint Synthesis**

Implement in `Council`:
- `build_lean_matrix(briefs)`: Formats all 5 micro-briefs into a concise compact table (~600-800 tokens).
- `critique_matrix_agent(agent_id, role_prompt, matrix)`: Runs focused debate with strict schema:
  - `endorse`: Agreement with specific directive.
  - `objection`: Specific counter-arguments.
  - `consensus_vote`: Final recommendation.
- `synthesize_blueprint(task, briefs, debate)`: Runs single master synthesis (Round 3) producing:
  1. System Architecture & Tech Stack
  2. Data Contracts & Interfaces
  3. UI Component Hierarchy
  4. Phased Implementation Checklist

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_lean_council.py`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add orchestrator/agent_runner.py orchestrator/council.py tests/test_lean_council.py
git commit -m "feat(council): implement active-5 lean protocol and blueprint synthesis"
```

---

### Task 3: Dual-Phase Assembly Line Engine (`orchestrator/assembly.py`)

**Files:**
- Create: `orchestrator/assembly.py`
- Create: `tests/test_assembly.py`

**Interfaces:**
- Consumes: `GeminiRouter` from `orchestrator/router.py`
- Produces: `AssemblyLine.generate_ui_spec(blueprint: str) -> str` (Agent 2)
- Produces: `AssemblyLine.generate_data_spec(blueprint: str) -> str` (Agent 3)
- Produces: `AssemblyLine.implement_code(task: str, ui_spec: str, data_spec: str) -> str` (Agent 4)
- Produces: `AssemblyLine.adversarial_review(code: str, requirements: str) -> dict` (Agent 5)

- [ ] **Step 1: Write unit test for AssemblyLine workflow**

Create `tests/test_assembly.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from orchestrator.assembly import AssemblyLine

@pytest.mark.asyncio
async def test_assembly_line_structure():
    mock_router = MagicMock()
    mock_router.request = AsyncMock(return_value="OK")
    assembly = AssemblyLine(router=mock_router)
    
    res = await assembly.generate_ui_spec("blueprint")
    assert res == "OK"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_assembly.py`
Expected: FAIL (ModuleNotFoundError)

- [ ] **Step 3: Implement `orchestrator/assembly.py`**

Implement `AssemblyLine`:
- Links the specialized roles in Phase 2:
  - `agent_2` creates the UI Component & CSS spec.
  - `agent_3` creates TypeScript / Data Model contracts.
  - `agent_4` takes UI Spec + Data Spec and writes production-ready code.
  - `agent_5` executes adversarial code review (flags security issues, edge cases, regression risks).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_assembly.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add orchestrator/assembly.py tests/test_assembly.py
git commit -m "feat(assembly): add dual-phase code generation and adversarial review"
```

---

### Task 4: Curated Knowledge Distiller (`orchestrator/learner.py`)

**Files:**
- Create: `orchestrator/learner.py`
- Create: `tests/test_learner.py`

**Interfaces:**
- Consumes: `ProjectMemory` from `orchestrator/triage.py`
- Produces: `KnowledgeDistiller.extract_learnings(transcript: str) -> list[dict]`
- Produces: `KnowledgeDistiller.apply_approved_learnings(safe_project_name: str, approvals: list[dict]) -> None`

- [ ] **Step 1: Write test for KnowledgeDistiller**

Create `tests/test_learner.py`:
```python
import tempfile
from pathlib import Path
import pytest
from orchestrator.learner import KnowledgeDistiller
from orchestrator.triage import ProjectMemory

def test_apply_learnings_writes_to_project_and_global():
    with tempfile.TemporaryDirectory() as tmpdir:
        base = Path(tmpdir)
        memory = ProjectMemory(base_dir=base)
        distiller = KnowledgeDistiller(memory=memory, agents_dir=base / "agents")
        
        # Test appending to project memory
        approvals = [
            {"scope": "project", "target": "Test-Project", "rule": "Use Redis for cache"},
        ]
        distiller.apply(approvals)
        loaded = memory.load("Test-Project")
        assert "Use Redis for cache" in loaded["decisions"]
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_learner.py`
Expected: FAIL

- [ ] **Step 3: Implement `orchestrator/learner.py`**

Implement:
- `extract_learnings(session_summary: str)`: Identifies new conventions/rules.
- `format_proposal(learnings: list)`: Formats clean CLI or chat approval menu:
  `[1] Project Rule: ...`
  `[2] Global Rule for agent_3: ...`
- `apply(approved_items: list)`: Appends approved rules strictly to `decisions.md` or the `## Learned Knowledge` section of `agentX.md` without overwriting prior contents.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_learner.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add orchestrator/learner.py tests/test_learner.py
git commit -m "feat(learner): add curated knowledge distiller with approval gate"
```

---

### Task 5: End-to-End Pipeline Orchestration (`orchestrator/pipeline.py`)

**Files:**
- Modify: `orchestrator/pipeline.py`
- Modify: `orchestrator/main.py`
- Create: `tests/test_pipeline.py`

**Interfaces:**
- Produces: `Pipeline.run(task: str, project_path: str | Path | None = None, mode: str = "council") -> dict`

- [ ] **Step 1: Write integration test for Pipeline**

Create `tests/test_pipeline.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from orchestrator.pipeline import UnifiedPipeline

@pytest.mark.asyncio
async def test_pipeline_round1_and_round2():
    with patch("orchestrator.pipeline.GeminiRouter") as mock_router_cls:
        mock_router = mock_router_cls.return_value
        mock_router.request = AsyncMock(return_value="directives:\n  - rule 1\nconstraints:\n  - c1\nred_flags:\n  - r1")
        
        pipeline = UnifiedPipeline()
        result = await pipeline.run_council(task="Test task", project_name="MockProject")
        assert "blueprint" in result
        assert result["status"] == "success"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_pipeline.py`
Expected: FAIL

- [ ] **Step 3: Implement `orchestrator/pipeline.py` and `main.py`**

Build `UnifiedPipeline`:
- Reads workspace path & loads `ProjectMemory`.
- Runs Phase 1 (Council: Round 1 Micro-Briefs ➔ Round 2 Matrix Debate ➔ Round 3 Master Blueprint).
- Optionally triggers Phase 2 (Assembly Line) if execution mode is requested.
- Distills proposed learning items and returns structured JSON/Markdown results.
- `main.py` exposes CLI arguments (`--task`, `--project`, `--mode`, `--json`).

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_pipeline.py`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add orchestrator/pipeline.py orchestrator/main.py tests/test_pipeline.py
git commit -m "feat(pipeline): wire end-to-end unified council and assembly pipeline"
```

---

### Task 6: Antigravity Plugin Packaging & Skill Manifest

**Files:**
- Create: `plugin.json`
- Create: `skills/ai-team/SKILL.md`

**Interfaces:**
- Exposes Antigravity skill `ai-team` accessible via `/ai-team <task>` from any IDE chat window.

- [ ] **Step 1: Create `plugin.json`**

```json
{
  "name": "ai-team",
  "version": "1.0.0",
  "description": "Token-optimized 5-agent engineering council and assembly line for architectural design and code execution",
  "author": "Antigravity",
  "skills": ["skills/ai-team"]
}
```

- [ ] **Step 2: Create `skills/ai-team/SKILL.md`**

With complete YAML frontmatter, execution instructions for Antigravity subagents, commands to invoke `python orchestrator/pipeline.py`, and result rendering into user artifacts.

- [ ] **Step 3: Commit**

```bash
git add plugin.json skills/ai-team/SKILL.md
git commit -m "feat(plugin): package ai-team as global Antigravity plugin and skill"
```

---

### Task 7: Full System Verification & Token Benchmark

- [ ] **Step 1: Run all unit and integration tests**
Run: `pytest tests/ -v`
Expected: All tests PASS.

- [ ] **Step 2: Run live dry-run benchmark**
Run: `python orchestrator/main.py --task "Build a high-performance shopping cart checkout with Redis session and Stripe webhook" --project "HariKita - Web App"`
Expected: Complete Phase 1 output under 15,000 tokens with clean blueprint and zero 429/503 errors.

- [ ] **Step 3: Final Git Commit and status check**
Ensure working directory is clean and all files are committed.
