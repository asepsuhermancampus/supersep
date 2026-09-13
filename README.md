# SuperSep ⚡

> **SuperSep** is a token-optimized, dual-phase multi-agent software engineering council and execution engine for Antigravity IDE.

Turn vague ideas into robust, battle-tested software through an elite council of 5 specialized AI agents — without getting bogged down by blind spots or burning thousands of dollars in token thrashing.

---

## 🚀 Three Commands (Persis Seperti Superpowers)

Begitu SuperSep terpasang, Anda mendapatkan **3 perintah slash** yang dapat digunakan langsung di percakapan chat IDE pada workspace mana pun:

### 1. `/mikirsep <ide / kebutuhan>` (Phase 1: Deliberation Council)
Mengumpulkan dewan 5 agen AI untuk brainstorming, mendiskusikan pro-kontra, menguji kontradiksi, dan menyusun **Master Architecture Blueprint**.
* **Round 1 (Micro-Briefs):** Anggaran token ketat (~150-200 token per agen).
* **Round 2 (Matrix Debate):** Saling sanggah dan *consensus voting*.
* **Round 3 (Blueprint Synthesis):** Dokumen spesifikasi arsitektur final yang solid.

### 2. `/gassep <task / blueprint>` (Phase 2: Assembly Line Coding)
Mengeksekusi cetak biru perencanaan menjadi kode produksi nyata tanpa tumpang tindih file:
* `agent_2` (UI Specialist): Spesifikasi komponen UI, CSS layout, dan design tokens.
* `agent_3` (Software Architect): Interface TypeScript, model data, dan kontrak API.
* `agent_4` (Senior Developer): **Juru Koding Utama** yang merakit kode produksi bersih.
* `agent_5` (Adversarial Reviewer): **Gatekeeper / QA** yang mengaudit kode dari celah keamanan dan bug sebelum diterapkan.

### 3. `/commitsep [pesan opsional]` (Git Commit & Push Automation)
Mengotomatiskan alur kerja Git dengan standar profesional:
* Memeriksa `git status` dan memverifikasi keamanan file sensitif (`.env` tidak akan ter-commit).
* Menganalisis perubahan kode dan menyusun pesan **Conventional Commits** (`feat:`, `fix:`, dll.) secara otomatis.
* Mengeksekusi staging (`git add`), commit, dan langsung `git push` ke branch remote.

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

- **Active-5 Lean Protocol:** Seluruh 5 agen tetap 100% aktif dalam setiap perancangan, tetapi penggunaan token dipangkas hingga **~85%** menggunakan schema *Micro-Briefs*.
- **Project-Scoped Memory:** Otomatis mendeteksi nama direktori induk workspace aktif Anda (misal `HariKita - Web App`), menyimpan riwayat arsitektur di `memory/projects/<nama>/` tanpa tercampur ke proyek lain.
- **Adaptive Self-Learning:** Menemukan pola/aturan baru dan memintakan konfirmasi persetujuan user (`[A] Approve, [D] Discard`) sebelum disimpan ke memori atau aturan agen.
- **Antigravity Global Plugin:** Sekali dipasang, langsung aktif di semua project dan workspace pada IDE Anda.

---

## 🛠️ Cara Kerja & Panduan Instalasi (Untuk User Lain)

Antigravity IDE secara otomatis memindai dan memuat plugin dari direktori:
* **Windows:** `C:\Users\<username>\.gemini\config\plugins\`
* **Linux / macOS:** `~/.gemini/config/plugins/`

### Opsi A: 1-Click Installer (Paling Mudah)

**Di Windows (PowerShell):**
```powershell
git clone https://github.com/asepsuhermancampus/supersep.git
cd supersep
.\install.ps1
```

**Di Linux / macOS (Terminal):**
```bash
git clone https://github.com/asepsuhermancampus/supersep.git
cd supersep
chmod +x install.sh && ./install.sh
```

### Opsi B: Clone Manual ke Folder Plugin Global

Cukup clone repository ini langsung ke folder plugin Antigravity Anda:
```bash
# Windows
git clone https://github.com/asepsuhermancampus/supersep.git "$env:USERPROFILE\.gemini\config\plugins\supersep"

# Linux / macOS
git clone https://github.com/asepsuhermancampus/supersep.git ~/.gemini/config/plugins/supersep
```
Setelah itu salin `.env.example` menjadi `.env` di dalam folder plugin tersebut dan masukkan API Key atau Router Base URL Anda.

Selesai! Buka Antigravity IDE di workspace mana pun, ketik `/` di chat, dan Anda akan langsung melihat:
* `/mikirsep`
* `/gassep`
* `/commitsep`

---

## 🧪 Testing

Jalankan pengujian otomatis untuk memverifikasi modul:
```bash
pytest tests/ -v
```

---

## 📄 License
MIT License. Created with ❤️ by Asep Suherman.
