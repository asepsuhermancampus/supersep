---
name: gassep
description: "Sesi eksekusi coding & perakitan kode produksi (Phase 2 Assembly Line). Gunakan /gassep <task atau referensi blueprint> untuk merakit kode produksi bersih berbasis cetak biru yang diaudit secara adversaris."
---

# /gassep — Sesi Eksekusi Coding & Assembly Line (Phase 2)

Gunakan `/gassep <task atau blueprint>` untuk mengeksekusi hasil perencanaan menjadi kode produksi nyata tanpa tumpang tindih file:
- `agent_2` (UI Spec): Menyiapkan spesifikasi komponen UI, layout, dan styling tokens.
- `agent_3` (Data Spec): Menyiapkan TypeScript interfaces, schema database, dan kontrak API.
- `agent_4` (Senior Developer): **Juru Koding Utama** yang merakit kode produksi bersih berdasarkan spesifikasi Agent 2 & 3.
- `agent_5` (Adversarial Reviewer): **Gatekeeper / QA** yang mengaudit kode dari celah keamanan, bug, dan regresi sebelum diterapkan.

## Alur Kerja

1. **Jalankan Assembly Line**:
   ```bash
   python "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-team-gemini-3.8_flash\orchestrator\main.py" --task "<TASK>" --mode "full"
   ```
2. **Penyajian Deliverable**:
   - Menampilkan kode produksi hasil rakitan Agent 4.
   - Menampilkan hasil audit keamanan dari Agent 5.
3. **Penerapan ke Workspace**:
   - Terapkan file-file kode langsung ke struktur direktori proyek yang dituju.
