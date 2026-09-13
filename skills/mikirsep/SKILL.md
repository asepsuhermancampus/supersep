---
name: mikirsep
description: "Sesi perencanaan, perumusan ide, dan debat arsitektur 5-agent council (Phase 1). Gunakan /mikirsep <ide/task> untuk membedah kebutuhan, menguji kontradiksi, dan menghasilkan Master Architecture Blueprint yang matang dan hemat token."
---

# /mikirsep — Sesi Perencanaan & Debat Dewan 5 Agen (Phase 1)

Gunakan `/mikirsep <ide/rancangan>` untuk mengumpulkan dewan 5 agen AI dalam merancang arsitektur perangkat lunak sebelum mulai ngoding:
- `agent_1` (Requirement Analyst): Membedah kebutuhan eksplisit, implisit, dan acceptance criteria.
- `agent_2` (Visual UI Specialist): Merancang hierarki UI, UX ergonomics, dan CSS tokens.
- `agent_3` (Software Architect): Merancang topologi sistem, kontrak API, dan schema data.
- `agent_4` (Senior Developer): Menilai kelayakan teknis dan perangkap implementasi.
- `agent_5` (Adversarial Reviewer): Menguji celah keamanan, failure modes, dan skalabilitas.

## Alur Kerja

1. **Deteksi Workspace**: Otomatis mendeteksi nama direktori induk proyek saat ini untuk memuat memori proyek dari `memory/projects/<nama-proyek>/`.
2. **Eksekusi 3-Round Lean Council**:
   ```bash
   python "C:\Users\asep.suherman\SETTUP TESTING\Build Project In Here\IDE\ai-team-gemini-3.8_flash\orchestrator\main.py" --task "<TASK>" --mode "council"
   ```
   - **Round 1 (Micro-Briefs):** Kelima agen mengeluarkan keputusan inti, batasan, dan risiko (~150-200 token per agen).
   - **Round 2 (Matrix Debate):** Kelima agen saling menguji, mendukung, dan membantah usulan agen lain.
   - **Round 3 (Master Blueprint):** Sintesis cetak biru arsitektur final yang lengkap dan terstruktur.
3. **Penyajian Deliverable**: Tampilkan Master Architecture Blueprint langsung di chat / dokumen artifact.
4. **Knowledge Distillation**: Menampilkan rekomendasi aturan baru untuk disetujui disimpan ke memori proyek.
