#!/bin/bash
# AUTOMASI UPLOAD KE GITHUB

echo -e "\e[1;32m🐙 GITHUB AUTO-DEPLOYER\e[0m"
echo "Pastikan Anda sudah membuat Repository KOSONG di GitHub.com"
echo "-----------------------------------------------------------"

# 1. URL Repository (Otomatis dari Chat)
REPO_URL="https://github.com/amarnazhan27-gif/NazhanBots-vFINAL"
echo "✅ Target Repo: $REPO_URL"

# if [ -z "$REPO_URL" ]; then... (Removed manual input)

# 2. Reset Remote (Jaga-jaga jika sudah ada)
git remote remove origin 2>/dev/null

# 3. Setting Remote
git remote add origin "$REPO_URL"
echo "✅ Remote set to: $REPO_URL"

# 4. Push
echo -e "\e[1;36m🚀 Sedang meng-upload... (Masukkan Username & Password/Token jika diminta)\e[0m"
git branch -M main
git push -u origin main

echo "-----------------------------------------------------------"
if [ $? -eq 0 ]; then
    echo -e "\e[1;32m✅ SUKSES! Kode sudah ada di GitHub Anda.\e[0m"
else
    echo -e "\e[1;31m❌ GAGAL. Cek koneksi atau password Anda.\e[0m"
    echo "Tips: Jika password gagal, gunakan 'Personal Access Token' sebagai password."
fi
