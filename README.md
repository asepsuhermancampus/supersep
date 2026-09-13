# SuperSep ⚡

> **SuperSep** is a token-optimized, dual-phase multi-agent software engineering council and execution engine for Antigravity IDE.

Turn vague ideas into robust, battle-tested software through an elite council of 5 specialized AI agents — without getting bogged down by blind spots or burning thousands of dollars in token thrashing.

---

## 🚀 Two Commands

SuperSep simplifies your workflow into two clean slash commands:

### 1. `/mikirsep <ide / kebutuhan>` (Phase 1: Deliberation Council)
Gathers the 5-agent council to brainstorm, debate trade-offs, identify edge cases, and produce an authoritative **Master Architecture Blueprint**.
* **Round 1 (Micro-Briefs):** Strict token budgets (~150-200 tokens per agent).
* **Round 2 (Matrix Debate):** Cross-critique and consensus voting.
* **Round 3 (Blueprint Synthesis):** Single unified specification.

### 2. `/gassep <task / blueprint>` (Phase 2: Assembly Line Coding)
Executes the approved blueprint into production-grade code without messy file collisions or fragmented styles:
* `agent_2` (UI Specialist): Layout, CSS tokens, and component specifications.
* `agent_3` (Software Architect): Data models, interfaces, and API contracts.
* `agent_4` (Senior Developer): **Lead Implementer** who merges specs into clean code.
* `agent_5` (Adversarial Reviewer): **QA Gatekeeper** auditing security, bugs, and edge cases.

---

## 👥 The 5-Agent Council

| Agent | Role | Focus |
| :--- | :--- | :--- |
| `agent_1` | **Requirement Analyst** | Explicit & implicit scope, edge cases, acceptance criteria. |
| `agent_2` | **Visual UI Specialist** | UI/UX hierarchy, typography, responsiveness, micro-copy. |
| `agent_3` | **Software Architect** | System topology, state flow, DB schema, API interfaces. |
| `agent_4` | **Senior Developer** | Implementation feasibility, code synthesis, zero placeholders. |
| `agent_5` | **Adversarial Reviewer** | Security vulnerabilities, failure modes, scalability traps. |

---

## 🧠 Key Features

- **Active-5 Lean Protocol:** All 5 agents remain 100% active in every decision while reducing token consumption by ~85% using schema-enforced Micro-Briefs.
- **Project-Scoped Memory:** Automatically detects the parent directory name of your active workspace (e.g. `HariKita - Web App`), storing project decisions in `memory/projects/<name>/` without cross-project pollution.
- **Adaptive Self-Learning:** Extracts reusable patterns and proposes them to you for explicit approval before appending to memory or agent rules.
- **Antigravity Global Plugin:** Ready to use across any workspace or project directly from the chat interface.

---

## 🛠️ Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone git@github.com:asepsuhermancampus/supersep.git
   cd supersep
   ```
2. **Install dependencies:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. **Configure Environment:**
   Copy `.env.example` to `.env` and set your 9Router or API gateway details:
   ```env
   ROUTER_BASE_URL=http://localhost:20128/v1
   ROUTER_API_KEY=your_key_here
   MODEL=5_gemini_3.8_flash_by_antigravity
   ```

---

## 🧪 Testing

Run the automated test suite:
```bash
pytest tests/ -v
```

---

## 📄 License
MIT License. Created with ❤️ by Asep Suherman.
