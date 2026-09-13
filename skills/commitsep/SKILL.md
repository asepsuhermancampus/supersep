---
name: commitsep
description: "Sesi otomatisasi git commit dan push ke remote repository. Gunakan /commitsep [pesan opsional] untuk menganalisis diff, menghasilkan pesan conventional commit cerdas, mengamankan file sensitif, melakukan commit, dan push ke branch remote."
---

# /commitsep — Git Commit & Push Automation

Gunakan `/commitsep` untuk melakukan commit dan push kode produksi dengan standar git profesional secara otomatis tanpa harus mengetik perintah git berulang kali.

## Alur Kerja Asisten Saat /commitsep Dipanggil

### 1. Verifikasi Status & Keamanan Git
Jalankan pemeriksaan status di workspace aktif:
```bash
git status
git diff --stat
```
**Safety Gate:** Pastikan file sensitif (seperti `.env`, credentials, secret keys, file `.venv/` atau `node_modules/`) TIDAK masuk ke staging. Jika file `.env` belum ada di `.gitignore`, tambahkan ke `.gitignore` terlebih dahulu!

### 2. Analisis Diff & Pembentukan Pesan Commit
Periksa perubahan kode dengan `git diff` untuk merumuskan pesan commit berstandar **Conventional Commits**:
- `feat(...)`: Fitur baru yang dibangun
- `fix(...)`: Perbaikan bug atau penyesuaian error
- `refactor(...)`: Perapian struktur kode tanpa mengubah fungsi
- `docs(...)`: Pembaruan dokumentasi atau spesifikasi
- `test(...)`: Penambahan atau penyesuaian pengujian

*(Jika pengguna menyertakan pesan khusus setelah `/commitsep <pesan>`, gabungkan atau gunakan pesan tersebut sebagai acuan utama).*

### 3. Eksekusi Staging, Commit & Push
Jalankan perintah commit dan push:
```bash
git add -A
git commit -m "<tipe>(<scope>): <deskripsi ringkas dan padat>"
git push -u origin <current_branch>
```

### 4. Laporan Konfirmasi ke Pengguna
Sajikan laporan ringkas di chat:
- **Commit Hash:** ID commit yang baru dibuat
- **Branch & Remote:** Nama branch tujuan push
- **Daftar Berkas:** Ringkasan file yang berhasil di-push
