# AI-Team Plugin & Dual-Phase Multi-Agent Engine Specification

- **Date:** 2026-09-14
- **Target Project:** `ai-team-gemini-3.8_flash`
- **Plugin Name:** `ai-team` (Antigravity Global Plugin / Skill)
- **Status:** Draft for Review

---

## 1. Executive Summary & Goals

The `ai-team` system is an autonomous, token-optimized multi-agent architecture designed to act as an on-demand software engineering council and execution engine across any project in the user's workspace.

### Core Objectives
1. **Universal Reusability (Antigravity Plugin):** Can be installed globally or called across any workspace via `/ai-team <task>` without duplicating Python scripts into every new project repository.
2. **Dual-Phase Engine (Council ➔ Assembly Line):** Clear separation of concerns between *Deliberation / Architecture Planning (Phase 1)* and *Code Generation & Quality Control (Phase 2)*.
3. **Active-5 Lean Protocol (Token Optimization):** All 5 agents remain 100% active in every decision (avoiding blind spots and costly 5-7x re-prompting cycles), while token consumption is reduced by ~85% via structured Micro-Briefs and Matrix Debates instead of verbose prose.
4. **Project-Scoped Memory:** Automatically detects the active workspace's parent directory (e.g., `HariKita - Web App`) to load and store project-specific context, conventions, and architectural decisions without cross-project pollution.
5. **Adaptive Self-Learning (Curated):** Identifies novel patterns and constraints during tasks, proposing concise rules to be saved into project memory or global `agent.md` files **only upon explicit user approval**.

---

## 2. System Architecture

```
                                [ User Prompt / Task ]
                                          │
                                          ▼
                         ┌─────────────────────────────────┐
                         │   Workspace & Project Detector  │
                         │   (Reads Parent Directory Name) │
                         └────────────────┬────────────────┘
                                          │
                                          ▼
                         ┌─────────────────────────────────┐
                         │      Project Memory Loader      │
                         │  (memory/projects/<name>/)      │
                         └────────────────┬────────────────┘
                                          │
                                          ▼
┌──────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: THE COUNCIL (Deliberation & Architectural Blueprint)                    │
│                                                                                  │
│  [Round 1: Micro-Briefs]                                                         │
│   5 Agents run in parallel (Strict budget: ~150-200 tokens per agent)            │
│   Output: Directives, Constraints, Red Flags                                     │
│                                                                                  │
│  [Round 2: Matrix Debate]                                                        │
│   5 Agents evaluate the combined ~800 token brief matrix                         │
│   Output: Endorsements, Critical Objections, Consensus Votes                     │
│                                                                                  │
│  [Round 3: Master Blueprint Synthesis]                                           │
│   Single consolidated specification: Architecture, Contracts, Task Checklist     │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼ [User Reviews & Approves Plan]
┌──────────────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: THE ASSEMBLY LINE (Execution & Code Production)                         │
│                                                                                  │
│  1. Agent 2 (UI Specialist)   ➔ Component Hierarchy, CSS/Tokens, Wireframe Spec  │
│  2. Agent 3 (Architect)       ➔ Data Models, TypeScript Interfaces, API Specs    │
│  3. Agent 4 (Senior Dev)      ➔ CORE IMPLEMENTER: Writes production code         │
│  4. Agent 5 (Reviewer)        ➔ ADVERSARIAL QA: Security, Edge cases, Bug audit  │
│  5. Antigravity IDE Engine    ➔ Writes files to workspace & runs verification    │
└─────────────────────────────────────────┬────────────────────────────────────────┘
                                          │
                                          ▼
                         ┌─────────────────────────────────┐
                         │   Knowledge Distiller (Learn)   │
                         │   - Identifies new rules        │
                         │   - Prompts User for Approval   │
                         │   - Appends to Memory / AgentMD │
                         └─────────────────────────────────┘
```

---

## 3. Agent Roles & Specifications

| Agent ID | Name | Core Phase 1 (Council) Role | Core Phase 2 (Assembly Line) Role |
| :--- | :--- | :--- | :--- |
| **`agent_1`** | **Requirement Analyst** | User stories, acceptance criteria, scope boundaries, non-goals. | Validates acceptance criteria against generated output. |
| **`agent_2`** | **Visual UI Specialist** | UI layout, UX ergonomics, micro-copy, responsiveness. | Generates UI component specifications, design tokens, CSS rules. |
| **`agent_3`** | **Software Architect** | System topology, state management, API routes, data flow. | Generates data schemas, DB models, typed interfaces. |
| **`agent_4`** | **Senior Developer** | Technical feasibility, dependency footprint, implementation traps. | **Primary Coder:** Merges UI + Architecture specs into production code. |
| **`agent_5`** | **Adversarial Reviewer** | Security vulnerabilities, failure modes, scalability bottlenecks. | **Gatekeeper / QA:** Adversarial code audit, security & regression checks. |

> **Critical Constraint:** Agents 1, 2, 3, and 5 DO NOT write mixed ad-hoc code in Phase 2. Agent 4 is the sole Code Synthesizer, preventing file collisions and fragmented code styles.

---

## 4. Active-5 Lean Protocol (Token Optimization)

### 4.1 Round 1: Micro-Brief Format
Each agent must output exactly the following JSON or YAML schema, capped at 200 tokens:
```yaml
agent_id: agent_x
directives:
  - "Key directive 1"
  - "Key directive 2"
  - "Key directive 3"
constraints:
  - "Hard constraint 1"
  - "Hard constraint 2"
red_flags:
  - "Identified risk 1"
  - "Identified risk 2"
```

### 4.2 Round 2: Matrix Debate Format
Input to each agent is the aggregated table of 5 micro-briefs (~800 tokens). Each agent outputs:
```yaml
agent_id: agent_x
endorse: "Agree with Agent Y's directive on Z"
objection: "Strongly challenge Agent W's proposal on Q because of R"
consensus_vote: "Adopt Approach A with Condition B"
```

### 4.3 Round 3: Synthesis
The master synthesizer consolidates consensus items, resolves objections, and outputs the final markdown plan with:
- System Overview & Tech Stack
- Data Flow & API Contracts
- Component Architecture
- Step-by-Step Task Checklist for Phase 2

---

## 5. Project-Scoped Memory Architecture

### 5.1 Storage Hierarchy
Located in `memory/`:
```
memory/
├── projects/
│   └── <parent_dir_name>/
│       ├── context.json       # Tech stack, framework versions, core paths
│       └── decisions.md       # Chronological ledger of approved council decisions
└── global/
    └── common_rules.md        # Organization-wide conventions
```

### 5.2 Context Detection
`orchestrator/triage.py` executes:
1. Read current working directory or target directory provided in request.
2. Extract project name: `project_name = Path(target_dir).name`.
3. If `memory/projects/<project_name>/context.json` exists:
   - Load metadata and inject into agent system prompts as a compact 100-token `<project_context>` block.
4. If it does not exist:
   - Create initial profile on user confirmation.

---

## 6. Knowledge Distillation & User Approval Protocol

At the completion of a council or assembly session:
1. `orchestrator/learner.py` analyzes the session transcript for new rules, library conventions, or architectural caveats.
2. It generates a draft recommendation:
   ```markdown
   ### Proposed Learning Items:
   1. [Project: HariKita - Web App] -> agent_3 (Architect):
      "Use TanStack Query with staleTime: 60_000 for user listing."
   2. [Global Rule] -> agent_4 (Senior Developer):
      "Always configure AbortController signal when writing async search inputs."
   ```
3. Prompt presented to user:
   - `[A] Approve all`
   - `[E] Edit selections`
   - `[D] Discard`
4. On approval, entries are appended to `decisions.md` or `agentX.md` under `## Learned Knowledge` without overwriting existing guidelines.

---

## 7. Antigravity Plugin & Slash Command Integration

### 7.1 Plugin Layout
```
ai-team-gemini-3.8_flash/
├── plugin.json
├── skills/
│   └── ai-team/
│       └── SKILL.md
├── agents/
│   ├── agent1.md ... agent5.md
├── memory/
│   └── projects/
└── orchestrator/
    ├── router.py
    ├── triage.py
    ├── agent_runner.py
    ├── council.py
    ├── assembly.py
    ├── learner.py
    └── pipeline.py
```

### 7.2 Slash Command
Invoked via `/ai-team <task description>`:
- The skill loads the pipeline.
- Antigravity coordinates execution, passing the workspace path.
- Results stream back directly into the chat conversation.

---

## 8. Verification Plan

1. **Token Budget Verification:** Run benchmark comparing raw verbose council vs. Active-5 Lean Protocol on the same task. Target: >= 80% reduction in total token footprint.
2. **Project Scoped Memory Test:** Run test from `HariKita - Web App` and verify that `memory/projects/HariKita-Web-App/` is created and read correctly without touching other projects.
3. **Dual-Phase Hand-off Test:** Run end-to-end task from Council debate -> Blueprint generation -> Assembly line code production -> Adversarial review pass.
4. **Approval Gate Test:** Ensure `learner.py` never modifies any markdown file without explicit user confirmation.
