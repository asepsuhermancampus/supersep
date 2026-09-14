# SuperSep v2.0: Collaborative Puzzle Ensemble & Autonomous Lifecycle Specification

- **Date:** 2026-09-14
- **Target Project:** `ai-supersep` (SuperSep Global Plugin for Antigravity IDE)
- **Status:** Approved Architecture Specification
- **Author:** Asep Suherman & Antigravity AI Engineering Council

---

## 1. Executive Summary & Core Objectives

SuperSep v2.0 merevolusi engine multi-agent dari model pembagian tugas kaku (*siloed single-role*) menjadi **Dewan 5 Insinyur Multifungsi (The Puzzle Ensemble)** yang bekerja bersama-sama di seluruh tahapan rekayasa perangkat lunak — mulai dari analisis UI/UX, perancangan arsitektur, penulisan kode produksi bersama (*ensemble coding*), perbaikan error mandiri (*self-healing war room*), hingga optimasi dan rilis publish ke Git.

### Tujuan Utama:
1. **True Collaborative Ensemble (No Bystanders):** Kelima agen 100% aktif dan setara di setiap tahap (Tahap 1 s/d 4). Tidak ada lagi agen yang bekerja sendirian (*no single-coder bottleneck*).
2. **Unconstrained Cognitive Reasoning:** Menghapus seluruh batasan token buatan (<150 kata) dan format ringkas kaku. Memberikan kebebasan penuh bagi model Gemini untuk menyitir dokumentasi, referensi desain industri nyata (*Stripe, Linear, Apple, Vercel*), dan menghasilkan kode utuh tanpa terpotong.
3. **Modular Staged Lifecycle with Human Approval Gates:** Alur terstruktur menjadi perintah modular eksplisit (`/mikir-ui`, `/mikir-arch`, `/gassep`, `/commitsep`, `/statussep`) dengan checkpoint jeda persetujuan pengguna (*human-in-the-loop*).
4. **The Elite Engineering Protocol (Zero-Slop Standard):** Mengadopsi standar kedalaman rekayasa model reasoning papan atas (DeepSeek R1, Claude 3.7, GPT-4o): haram placeholder/TODO, haram tipe malas `any`, wajib 5-state UI handling (Idle, Loading, Success, Empty, Error), dan validasi skema data Zod ketat.
5. **Direct File Assembly & Autonomous Self-Healing:** Penulisan berkas langsung ke workspace proyek target, verifikasi build otomatis (`npm run build`, `npm test`, `pytest`), dan loop perbaikan mandiri otomatis (3–5 siklus) jika ditemukan error.
6. **Project-Scoped Checkpoint Persistence:** Menyimpan status sesi di `memory/projects/<safe_name>/checkpoints/session_state.json` agar pekerjaan dapat dijeda dan dilanjutkan kapan saja.

---

## 2. Definisi 5 Lensa Kognitif Multifungsi (The 5 Multifunctional Lenses)

Kelima agen bertransformasi dari sekadar deskripsi peran kaku menjadi **Senior Full-Stack Engineers** dengan sudut pandang analitis (*cognitive lenses*) yang saling melengkapi:

| Agen ID | Nama Lensa Kognitif | Peran di Tahap 1 (UI/UX) | Peran di Tahap 2 (Arsitektur) | Peran di Tahap 3 (Coding Ensemble) | Peran di Tahap 4 (Self-Healing & Launch) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`agent_1`** | **Product Strategist & UX Flow** | Memetakan user journey, ergonomi, mental model, & micro-copy ramah. | Memvalidasi integritas business logic, skenario edge case, & navigasi. | Menulis logika interaksi pengguna, routing, form validation, & dialog konfirmasi. | Mendiagnosis error alur UX, form bugs, & menyusun release notes rilis. |
| **`agent_2`** | **Design Systems & Visual Craftsman** | Menentukan tokens warna, tipografi, Bento grid, & komponen Shadcn/Tailwind. | Merancang hierarki komponen UI & CSS modularitas tokens. | Menulis JSX/HTML layout, styling Tailwind responsif, & transisi/animasi mikro. | Mendiagnosis error CSS, layout breaks, & responsivitas mobile. |
| **`agent_3`** | **Systems Architect & State/Data** | Menentukan state UI (skeleton, optimistic UI, empty state). | Merancang topologi sistem, database schema, kontrak API, & Zod schemas. | Menulis Zod validation schemas, global state stores, API routes, & ORM queries. | Mendiagnosis error tipe data, schema mismatch, & state mutations. |
| **`agent_4`** | **Principal Engineer & Code Rigor** | Menilai kelayakan rendering DOM & framework conventions. | Menentukan arsitektur folder, modularitas berkas, & decoupling dependencies. | Menulis algoritma komputasi inti, integrasi komponen, performa rendering, & zero placeholders. | Mendiagnosis error komputasi, runtime crash, & optimasi bundle. |
| **`agent_5`** | **Adversarial QA, Security & Resilience** | Menguji kontras warna WCAG AA, navigasi keyboard, & responsive traps. | Menguji celah keamanan (OWASP, auth bypass, injection), race conditions, & failure modes. | Menulis Error Boundaries, sanitasi input security, & **Unit/Integration Test Suites**. | Mendiagnosis unhandled exceptions, security vulnerabilities, & memverifikasi build hijau. |

---

## 3. Arsitektur Router & Infrastruktur LLM

Diperbarui pada `orchestrator/router.py`:
- **Unconstrained Output Window:** Menghapus batas `max_tokens` kecil, mendukung respons panjang dan menyeluruh.
- **Concurrency Rate Limiter:** Memasang `asyncio.Semaphore(3)` agar pemanggilan simultan kelima agen tidak memicu HTTP 429 pada 9Router.
- **Exponential Backoff with Jitter:** Otomatis mencoba ulang (*retry*) hingga 3x jika koneksi timeout atau router overload (HTTP 503/429).
- **Multimodal Vision Integration:** Mendukung input URL gambar atau path screenshot lokal (PNG/JPG) yang di-encode ke format base64/URL untuk dianalisis oleh kapabilitas penglihatan Gemini 3.8 Flash.

---

## 4. Rincian Siklus Hidup Modular (The 4-Stage Lifecycle)

```
                            [ User Input / Task ]
                                      │
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │ STAGE 1: UI/UX Discovery & Visual Design System  │
             │ [/mikir-ui <input/url/screenshot>]               │
             │ - 5 Agen Kolaborasi Desain & Benchmarking        │
             │ - Deliverables: Design System, HTML, Mockup      │
             └────────────────────────┬─────────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ USER CHECKPOINT 1:        │
                        │ [Approve] / [Revisi]      │
                        └─────────────┬─────────────┘
                                      │ (Approved)
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │ STAGE 2: System Architecture & Data Contracts    │
             │ [/mikir-arch]                                    │
             │ - 5 Agen Kolaborasi Database, API, Zod Schemas   │
             │ - Deliverables: master_architecture_blueprint.md │
             └────────────────────────┬─────────────────────────┘
                                      │
                                      ▼
                        ┌───────────────────────────┐
                        │ USER CHECKPOINT 2:        │
                        │ [Approve] / [Revisi]      │
                        └─────────────┬─────────────┘
                                      │ (Approved)
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │ STAGE 3 & 4: Ensemble Coding & Self-Healing Loop │
             │ [/gassep]                                        │
             │ - 5 Agen Merakit Kode Bersama Langsung ke Disk   │
             │ - Automated Build & Test Run                     │
             │ - Self-Healing War Room (Fix Loop 3-5x)          │
             └────────────────────────┬─────────────────────────┘
                                      │ (100% Zero Error / Tests Pass)
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │ STAGE 5 & 6: Launch to Publish & Git Release     │
             │ [/commitsep [pesan]]                             │
             │ - Proteksi .env, Conventional Commits, Push      │
             │ - Knowledge Distillation ke Memory Proyek        │
             └──────────────────────────────────────────────────┘
```

### 4.1 Tahap 1: UI/UX & Visual Design System (`/mikir-ui`)
- **Input:** URL web kompetitor/lama, screenshot UI lokal, atau deskripsi teks konsep.
- **Proses 5 Agen:**
  - Diskusi terbuka tanpa batasan token. Menyitir referensi industri kelas dunia (*Stripe, Linear, Apple, Vercel*).
  - Merancang sistem desain atomik, skala tipografi responsif, palet warna semantik, dan micro-animations.
- **Tiga Deliverable Wajib:**
  1. `ui_design_system.md`: Panduan token warna, tipografi, margin, dan komponen.
  2. `preview.html`: Prototipe interaktif mandiri berbasis Tailwind CSS yang bisa dibuka langsung di browser.
  3. `mockup.png`: Gambar render visual estetika antarmuka.
- **Checkpoint Gate:** Status sesi dicatat sebagai `UI_COMPLETED`. Pengguna mengetik `approve` untuk mengesahkan menjadi `UI_APPROVED` atau `revisi <detail>` untuk perbaikan.

### 4.2 Tahap 2: System Architecture & Data Contracts (`/mikir-arch`)
- **Prasyarat:** Status harus `UI_APPROVED`.
- **Proses 5 Agen:**
  - Mengambil desain UI yang disetujui sebagai acuan mutlak.
  - Merumuskan: Database schema (Prisma/Drizzle/SQL), State management flow, Zod schemas terperinci, REST/Server Action endpoints, dan struktur modular folder.
  - Memastikan penanganan 5-state (Idle, Loading, Success, Empty, Error) di setiap endpoint.
- **Deliverable:** `master_architecture_blueprint.md`.
- **Checkpoint Gate:** Pengguna mengetik `approve` untuk mengesahkan status menjadi `ARCH_APPROVED`.

### 4.3 Tahap 3 & 4: Ensemble Coding & Autonomous Self-Healing (`/gassep`)
- **Prasyarat:** Status harus `ARCH_APPROVED`.
- **Proses 5-Agent Mob Programming:**
  - `agent_1` menulis alur interaksi dan micro-copy.
  - `agent_2` menulis komponen UI JSX dan class Tailwind semantik.
  - `agent_3` menulis Zod validation schemas dan data stores.
  - `agent_4` menulis komputasi logika inti dan integrasi komponen.
  - `agent_5` menulis Error Boundaries dan unit test suites.
- **Direct File Writer:** Kode langsung dituliskan dan diperbarui ke struktur folder workspace aktif pengguna.
- **Autonomous Self-Healing Loop:**
  - Engine otomatis menjalankan perintah verifikasi proyek (`npm run build`, `npm test`, atau `pytest`).
  - Jika terjadi error kompilasi, tipe data, atau runtime crash:
    1. Tangkap stack trace dan pesan error lengkap.
    2. Kelima agen masuk ke *War Room* untuk mendiagnosis akar masalah.
    3. Menerapkan patch perbaikan langsung ke berkas terkait.
    4. Menjalankan pengujian ulang (loop hingga maksimal 3–5 siklus) sampai **BUILD BERSIH / 100% GREEN**.

### 4.4 Tahap 5 & 6: Git Release & Knowledge Distillation (`/commitsep`)
- **Security Gate:** Memastikan file rahasia (`.env`, secrets, node_modules) tidak ter-stage.
- **Conventional Commits:** Menganalisis diff untuk membuat pesan commit cerdas berstandar industri.
- **Push ke Remote:** Menjalankan `git push` dan menyajikan konfirmasi rilis.
- **Adaptive Learning:** `orchestrator/learner.py` mengekstrak pelajaran dan pola arsitektur baru dari sesi dan menyimpannya ke `memory/projects/<safe_name>/decisions.md`.

---

## 5. Struktur Berkas & Modul Baru

```text
orchestrator/
├── router.py                  # Router diperkuat (Semaphore, Retries, Vision Multimodal)
├── triage.py                  # WorkspaceDetector & ProjectMemory
├── state.py                   # [NEW] CheckpointStateManager (session_state.json)
├── agent_runner.py            # Runner kolaboratif unconstrained
├── council.py                 # Konsensus & synthesis engine
├── assembly.py                # Direct file writer & test executor
├── learner.py                 # Knowledge Distiller
├── pipeline.py                # Unified Modular Lifecycle Pipeline
├── main.py                    # CLI controller (--stage ui, arch, gas, status)
└── stages/                    # [NEW] Modul terisolasi per tahap
    ├── ui_stage.py            # Logika Tahap 1 (UI/UX, HTML preview, Mockup)
    ├── arch_stage.py          # Logika Tahap 2 (Architecture & Data Contracts)
    ├── ensemble_code_stage.py # Logika Tahap 3 (5-Agent Mob Coding)
    └── healing_stage.py       # Logika Tahap 4 (War Room & Self-Healing Loop)
```

---

## 6. Rencana Verifikasi & Uji Sistem

1. **Uji Router Ketahanan:** Verifikasi bahwa pemanggilan paralel dengan `asyncio.Semaphore(3)` berjalan mulus tanpa error 429 saat dibebani request besar.
2. **Uji Checkpoint State:** Verifikasi bahwa sesi dapat berhenti di `UI_APPROVED`, menyimpan state ke disk, dan dilanjutkan oleh perintah `/mikir-arch` tanpa kehilangan riwayat.
3. **Uji Ensemble Coding:** Verifikasi bahwa berkas kode yang dihasilkan memiliki kontribusi dari kelima agen dan langsung tertulis di disk workspace.
4. **Uji Self-Healing:** Simulasikan file dengan syntax error buatan dan buktikan bahwa engine menangkap error, memperbaikinya secara otomatis, dan mengembalikan build hijau.
5. **Uji Regresi Pytest:** Seluruh suite pengujian `pytest tests/ -v` harus lulus 100%.
