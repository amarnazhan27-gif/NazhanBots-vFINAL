#!/bin/bash
# LITE MODE LAUNCHER
# Runs NazhanBots in High-Performance Mode

echo -e "\e[1;33m⚡ STARTING NAZHAN BOTS: LIGHT SPEED MODE\e[0m"
echo -e "\e[1;30m(Disabling UI, Voice, Discord for MAX RAM)\e[0m"

# 0. Kill Zombie Processes (Resolve Conflict 409)
echo -e "\e[1;31m💀 Purging Zombie Bots...\e[0m"
pkill -f "python main.py" || true
pkill -f "bash guardian.sh" || true
pkill -f "python3 main.py" || true
sleep 1

# 1. Acquire Wake Lock
termux-wake-lock

# 2. Run with --lite and Python Optimization
# -O: Remove assert
# -OO: Remove docstrings
# -u: Unbuffered output
export PYTHONUNBUFFERED=1
python -u main.py --lite
