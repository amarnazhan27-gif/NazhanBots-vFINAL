#!/bin/bash
# v55 SERVER DAEMON STARTER
# Keeps the bot running 24/7 even if phone sleeps.

echo -e "\e[1;36m🔋 STARTING SERVER MODE (DAEMON)...\e[0m"

# 1. Acquire Wake Lock (Prevent CPU Sleep)
termux-wake-lock
echo -e "\e[1;32m✅ Wake-Lock Acquired (Anti-Sleep)\e[0m"

# 2. Run in Background (Auto-Restart Loop)
echo -e "\e[1;33m🔄 Auto-Restart Module Active.\e[0m"

while true; do
    echo "Starting process..." >> logs/sys.log
    python main.py >> logs/sys.log 2>&1
    echo "⚠️ Process crashed. Restarting in 5s..." >> logs/sys.log
    sleep 5
done &

PID=$!

echo -e "\e[1;32m✅ Daemon Process ID: $PID\e[0m"
echo -e "\e[1;33m👉 Check logs: tail -f logs/sys.log\e[0m"
echo -e "\e[1;31m👉 To Stop: kill $PID\e[0m"
