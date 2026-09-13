---
name: ai-team
description: "Token-optimized 5-agent engineering council and assembly line for architectural design, deliberation, and production code execution. Use when the user requests multi-agent architecture review, design dewan, or project implementation via /ai-team."
---

# AI-Team Multi-Agent Engine

Execute comprehensive architectural deliberation and dual-phase code implementation through a specialized 5-agent council:
- `agent_1`: Requirement Analyst (Scope, edge cases, acceptance criteria)
- `agent_2`: Visual UI Specialist (Component layout, tokens, micro-interactions)
- `agent_3`: Software Architect (Topology, data contracts, state flow)
- `agent_4`: Senior Developer (Lead implementer, clean production code)
- `agent_5`: Adversarial Reviewer (Gatekeeper, security, performance, regression audit)

## When to Use

Invoke this skill whenever the user asks to:
- Deliberate, design, or review a software system using the 5-agent team (`/ai-team`).
- Solve complex engineering tasks without suffering from single-agent blind spots or context thrashing.
- Produce an authoritative, consensus-tested architectural blueprint or production implementation.

## Workflow

### Step 1: Detect Target Workspace
Identify the current workspace or project path the user is working on (e.g. `C:\Users\...\HariKita - Web App`).

### Step 2: Invoke Engine
Run the `UnifiedPipeline` CLI:
```bash
python "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-team-gemini-3.8_flash\orchestrator\main.py" --task "<USER_TASK>" --project "<PROJECT_PATH>" --mode "council" --json
```

Mode options:
- `council`: Phase 1 only (Micro-Briefs, Matrix Debate, Master Blueprint Synthesis).
- `assembly`: Phase 2 code implementation from an established blueprint.
- `full`: Phase 1 deliberation followed immediately by Phase 2 production code generation and adversarial audit.

### Step 3: Present Deliverables as an Artifact
Create an artifact markdown file in the conversation brain displaying:
1. Master Architecture Blueprint
2. UI Component & Data Contract specifications
3. Production Code and Adversarial Review (if Phase 2 requested)

### Step 4: Knowledge Distillation & Approval
If the engine identifies new reusable rules (`learnings` array in JSON output):
Present the proposed rules to the user in chat:
> "Dewan agen merekomendasikan pelajaran baru untuk disimpan ke memori proyek:
> - `[Kategori]`: `[Aturan]`
> Apakah Anda menyetujui penyimpanan ini ke memori proyek?"
Upon confirmation, append the rule to `memory/projects/<safe_project_name>/decisions.md`.
