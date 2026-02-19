# PANDUAN INSTALASI & EKSEKUSI (Termux)
**Codename**: NazhanBots vREBORN (The Phoenix)
**Target Platform**: Android (Termux)

---

### 1. PERSIAPAN TERMINAL
Buka aplikasi **Termux** dan jalankan perintah sakti ini (Satu per satu):

```bash
# Update Repo & Upgrade System
pkg update && pkg upgrade -y

# Install Python & Git
pkg install python git -y

# Install Tools Tambahan (Optional tapi Bagus)
pkg install rust binutils -y
```

---

### 2. DEPLOY SYSTEM
Jika Anda memiliki file ZIP (`NazhanBots_vREBORN_Termux.zip`):

1.  Buka File Manager, ekstrak ZIP tersebut ke folder `Download`.
2.  Kembali ke Termux, masuk ke folder tersebut:

```bash
# Masuk ke folder hasil ekstrak
cd /sdcard/Download/NazhanBots_vREBORN_Termux/termux_version

# ATAU jika folder ada di Home Termux
cd ~/NazhanBots_vREBORN_Termux/termux_version
```

---

### 3. INSTALASI DEPENDENSI (OTOMATIS)
Kami telah menyediakan script `setup.sh` yang akan mengurus semuanya (Install Library, Cek Koneksi, Verifikasi File).

```bash
# Beri izin eksekusi untuk SEMUA file script
chmod +x *.sh

# Jalankan Setup
bash setup.sh
```

*Tunggu hingga proses selesai. Script akan otomatis mendownload library Python yang dibutuhkan.*

---

### 4. JALANKAN SENJATA (MODE LITE - DISARANKAN)
Untuk performa maksimal di HP (Hemat Baterai & Kuota, tapi Serangan Brutal):

```bash
bash start_lite.sh
```

**Fitur Lite Mode:**
-   🚀 **Turbo Speed**: Interface ringan, fokus ke kecepatan tembak.
-   🔋 **Battery Saver**: Mematikan animasi berat.
-   🛡️ **Phantom Mode**: Otomatis mengaktifkan Stealth SSL.

---

### 5. JALANKAN SENJATA (MODE FULL - KEREN)
Jika HP Anda spek dewa dan ingin melihat grafik Matrix/Cyberpunk:

```bash
python main.py
```

---

### 🛠️ TROUBLESHOOTING (JIKA ERROR)

**A. API Error / Connection Refused**
Jalankan pengecekan jaringan:
```bash
python check_api.py
```
*Jika banyak yang mati, biarkan saja. Bot akan otomatis menghapus yang mati saat berjalan.*

**B. "Module Not Found"**
Install ulang library secara manual:
```bash
pip install -r requirements.txt
```

**C. Lupa Perintah?**
Cukup ketik:
```bash
python main.py --help
```

---

**⚠️ PERINGATAN KERAS**
Gunakan tools ini hanya untuk **PENGETESAN KEAMANAN (PENETRATION TESTING)** pada nomor Anda sendiri. Developer tidak bertanggung jawab atas penyalahgunaan.

*Selamat Berburu, Komandan.* 🐧💎
