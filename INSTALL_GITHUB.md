# PANDUAN INSTALASI (VIA GITHUB)

**Target Repository**: `https://github.com/amarnazhan27-gif/NazhanBots-vFINAL`
**Platform**: Termux (Android)

---

### **LANGKAH 1: PERSIAPAN TERMUX**
Buka Termux dan jalankan perintah wajib ini (satu per satu):

```bash
# 1. Update Sistem & Install Git
pkg update && pkg upgrade -y
pkg install python git -y

# 2. Hapus Versi Lama (Agar tidak bentrok)
cd ~
rm -rf NazhanBots-vFINAL
```

---

### **LANGKAH 2: DOWNLOAD (CLONE)**
Ambil kode terbaru langsung dari GitHub Anda:

```bash
# Clone Repository
git clone https://github.com/amarnazhan27-gif/NazhanBots-vFINAL

# Masuk ke Folder
cd NazhanBots-vFINAL
```

---

### **LANGKAH 3: INSTALL & JALANKAN**
Sekarang, aktifkan sistemnya.

```bash
# Beri Izin & Setup
chmod +x *.sh
bash setup.sh

# JALANKAN (Pilih Salah Satu):

# A. Mode Cepa (Lite) - DISARANKAN
bash start_lite.sh

# B. Mode Server (24/7)
bash start_server.sh
```

---

**CATATAN PENTING:**
Jika Anda mengubah kode di Laptop dan meng-update GitHub, di Termux cukup ketik:
```bash
cd ~/NazhanBots-vFINAL
git pull
```
Ini akan otomatis meng-update bot Anda ke versi terbaru tanpa perlu install ulang.
