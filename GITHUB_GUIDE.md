# PANDUAN UPLOAD KE GITHUB

Karena saya (AI) tidak memiliki akses password GitHub Anda, Anda harus melakukan "Push" manual.

### LANGKAH 1: BUAT REPO DI GITHUB
1.  Buka [GitHub.com](https://github.com/new).
2.  Buat Repository baru.
3.  Beri nama: `NazhanBots-vFINAL`.
4.  Pastikan pilih **Public** (agar mudah di-clone) atau **Private**.
5.  Jangan centang "Add README" (karena kita sudah punya).
6.  Klik **Create Repository**.

### LANGKAH 2: HUBUNGKAN & UPLOAD
Salin perintah ini dan jalankan di terminal laptop/komputer ini (di folder `termux_version`):

```bash
# Ganti URL_REPO_ANDA dengan link dari GitHub (misal: https://github.com/User/NazhanBots-vFINAL.git)
git remote add origin URL_REPO_ANDA

# Upload kode
git push -u origin main
```

### LANGKAH 3: INSTALL DI TERMUX (HP)
Setelah berhasil di-upload, buka Termux di HP Anda dan ketik:

```bash
# 1. Update
pkg update && pkg upgrade -y
pkg install python git -y

# 2. Clone (Download)
git clone URL_REPO_ANDA

# 3. Jalankan
cd NazhanBots-vFINAL
chmod +x *.sh
bash setup.sh
bash start_lite.sh
```
