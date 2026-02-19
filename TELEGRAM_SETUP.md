# PANDUAN REMOTE CONTROL TELEGRAM 📡

Untuk mengendalikan bot ini dari jarak jauh (Telegram), Anda perlu mendapatkan **Bot Token** dan memasukkannya ke konfigurasi.

### LANGKAH 1: BUAT BOT BARU (DI TELEGRAM)
1.  Buka aplikasi Telegram.
2.  Cari akun: **@BotFather** (yang ada centang biru).
3.  Ketik: `/newbot`
4.  Beri nama bot (bebas, misal: `KutuKupretBot`).
5.  Beri username (harus unik & akhiran `bot`, misal: `KutuKupret_999_bot`).
6.  BotFather akan memberi **TOKEN API**.
    *Contoh: `123456789:ABCdefGHIjklMNOpqrSTUvwxYZ`*
    👉 **SALIN TOKEN INI.**

### LANGKAH 2: CARI ID ANDA
1.  Cari akun: **@userinfobot** di Telegram.
2.  Klik **Start**.
3.  Dia akan membalas dengan `Id: 123456789`.
    👉 **SALIN ID INI.**

### LANGKAH 3: MASUKKAN KE SYSTEM (TERMUX)
Di Termux, ketik perintah ini untuk mengedit konfigurasi:

```bash
# Buka config dengan Nano text editor
nano config/config.json
```

Ubah bagian ini:
```json
"TELEGRAM_BOT_TOKEN": "PASTE_TOKEN_DISINI",
"TELEGRAM_CHAT_ID": "PASTE_ID_DISINI",
```
*(Gunakan tombol volume bawah + V untuk paste di Termux, atau tekan lama layar).*

**Simpan:**
1.  Tekan `CTRL + X` (di keyboard hacker) atau `Volume Bawah + X`.
2.  Tekan `Y` (Yes).
3.  Tekan `Enter`.

### LANGKAH 4: JALANKAN
Restart botnya:
```bash
bash start_lite.sh
```

Sekarang coba chat ke bot Anda di Telegram:
ketik `/status` atau `/help`.

**SELAMAT MENIKMATI KEKUASAAN JARAK JAUH!** 🍷
