---
name: mikirsep
description: "Sesi perencanaan, perumusan ide, dan debat arsitektur 5-agent council (Phase 1). Gunakan /mikirsep <ide/task> untuk membedah kebutuhan, menguji kontradiksi, dan menghasilkan Master Architecture Blueprint yang matang — dengan kedalaman reasoning setara model frontier."
---

# /mikirsep — Sesi Perencanaan & Debat Dewan 5 Agen (Phase 1)

SuperSep v2.0 menghadirkan **5 Senior Engineer multifungsi** dengan cognitive lenses yang saling melengkapi — bukan agent kaku, tapi pemikir yang bisa beradaptasi ke setiap tahap proyek.

## 5 Cognitive Lenses

| Agent | Lensa | Spesialisasi |
|-------|-------|-------------|
| `agent_1` | Product Strategist & UX Flow | User journey, implicit requirements, acceptance criteria, 5-state UX |
| `agent_2` | Design Systems & Visual Craftsman | Design tokens, atomic components, WCAG, micro-animations, Tailwind |
| `agent_3` | Systems Architect & State/Data | Prisma schema, Zod validation, API contracts, 5-state responses |
| `agent_4` | Principal Engineer & Code Rigor | Zero-placeholder policy, Next.js 15, clean architecture, performance |
| `agent_5` | Adversarial QA, Security & Resilience | OWASP Top 10, race conditions, accessibility, severity classification |

Setiap agen dilengkapi **Chain-of-Thought Protocol wajib** dan referensi standar industri (Stripe, Vercel, Linear, Apple HIG).

---

## Alur Kerja v2.0

### STAGE 1: UI/UX Discovery (`--stage ui`)
5 agen berkolaborasi mendesain sistem visual. Menghasilkan:
- `ui_design_system.md` — token warna, tipografi, komponen hierarchy, spacing grid
- `preview.html` — prototipe interaktif mandiri berbasis Tailwind CDN

```powershell
& "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-supersep\.venv\Scripts\python.exe" `
  "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-supersep\orchestrator\main.py" `
  --stage ui --task "<TASK>" --project "<PATH_WORKSPACE_AKTIF>"
```

Dengan referensi screenshot/mockup (multimodal):
```powershell
& "...\main.py" --stage ui --task "<TASK>" --project "<PATH>" --image "<PATH_SCREENSHOT>"
```

### STAGE 2: System Architecture (`--stage arch`)
5 agen merancang arsitektur teknis berbasis Design System yang sudah disetujui. Menghasilkan:
- `master_architecture_blueprint.md` — schema Prisma, Zod schemas, API contracts, folder structure

```powershell
& "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-supersep\.venv\Scripts\python.exe" `
  "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-supersep\orchestrator\main.py" `
  --stage arch --task "<TASK>" --project "<PATH_WORKSPACE_AKTIF>"
```

### Cek Status Pipeline

```powershell
& "...\main.py" --stage status --project "<PATH_WORKSPACE_AKTIF>"
```

---

## Legacy Mode (Backward Compatible)

Mode council lama masih bisa digunakan untuk planning cepat tanpa deliverable files:
```powershell
& "...\main.py" --task "<TASK>" --project "<PATH>" --mode "council"
```

---

## Proses 3-Round Council

1. **Round 1 (Micro-Briefs):** Kelima agen menganalisis task dari lensa kognitif masing-masing — tanpa batas token, mendalam, konkret.
2. **Round 2 (Matrix Debate):** Kelima agen saling menguji, mendukung, dan menantang directives agen lain dengan alasan teknis spesifik.
3. **Round 3 (Master Blueprint):** Sintesis cetak biru arsitektur final yang production-grade, zero placeholder, zero ambiguity.

State checkpoint otomatis disimpan ke:
`memory/projects/<nama-proyek>/checkpoints/session_state.json`

---

## Knowledge Distillation

Setiap sesi mengekstrak 1-3 engineering rules yang ditemukan dan menawarkan untuk disimpan ke:
- **Project memory:** `memory/projects/<nama>/decisions.md`
- **Global agent rules:** `agents/agentX.md` (bagian "Learned Knowledge")
