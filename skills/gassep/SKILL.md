---
name: gassep
description: "Sesi eksekusi coding & perakitan kode produksi (Phase 2 Assembly Line). Gunakan /gassep <task atau referensi blueprint> untuk merakit kode produksi bersih berbasis cetak biru yang diaudit adversaris — dengan Self-Healing War Room otomatis."
---

# /gassep — Sesi Ensemble Coding & Self-Healing (Phase 2)

SuperSep v2.0 menghadirkan **5-Agent Mob Programming** dimana setiap agen menulis bagian spesialisasinya secara bersamaan — bukan single coder bottleneck. Dilanjutkan dengan **Self-Healing War Room** yang otomatis memperbaiki build errors.

## Alur Kerja v2.0

### STAGE 3+4: Ensemble Coding + Auto Self-Healing (`--stage gas`)

5 agen menulis kode secara kolaboratif, masing-masing sesuai spesialisasinya:
- `agent_1` → Routing logic, form validation, dialog copy, loading state orchestration
- `agent_2` → JSX/TSX components, Tailwind styling, micro-animations, design token constants
- `agent_3` → Zod schemas, Prisma schema, Server Actions / API routes, state stores
- `agent_4` → **Primary coder** — integrasi semua komponen, page-level code, utilities
- `agent_5` → Error Boundaries, security sanitization, unit/integration test suites

Semua file langsung ditulis ke **workspace target** (`--project`).

```powershell
& "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-supersep\.venv\Scripts\python.exe" `
  "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-supersep\orchestrator\main.py" `
  --stage gas --task "<TASK_ATAU_REFERENSI_BLUEPRINT>" --project "<PATH_WORKSPACE_AKTIF>"
```

### STAGE 4 Saja: Self-Healing Only (`--stage heal`)

Jika kode sudah ada dan hanya perlu diperbaiki:
```powershell
& "...\main.py" --stage heal --project "<PATH_WORKSPACE_AKTIF>"
```

---

## Self-Healing War Room — Auto-Fix Loop

Engine otomatis:
1. **Deteksi project type:** `package.json` → `npm run build` + `npm test` | `pyproject.toml` → `pytest -v`
2. **Run build/test** dan capture stack trace lengkap
3. **War Room:** Kelima agen mendiagnosis root cause dan menghasilkan patch
4. **Apply patch** langsung ke file yang bermasalah di workspace target
5. **Loop** hingga maksimal **5 cycles** atau sampai `BUILD CLEAN ✅`

---

## Output & Deliverables

- **Files kode** ditulis langsung ke struktur direktori proyek target
- **State** otomatis diperbarui ke `CODE_COMPLETED` → `HEALING_COMPLETED`
- **State file:** `memory/projects/<nama>/checkpoints/session_state.json`

---

## Prasyarat

Untuk hasil optimal, jalankan setelah `/mikirsep --stage arch` selesai:
- `memory/projects/<nama>/deliverables/master_architecture_blueprint.md` tersedia sebagai konteks
- `memory/projects/<nama>/deliverables/ui_design_system.md` tersedia untuk referensi visual

---

## Legacy Mode (Backward Compatible)

```powershell
& "...\main.py" --task "<TASK>" --project "<PATH>" --mode "full"
```
