#!/bin/bash
# LITE MODE LAUNCHER
# Runs NazhanBots in High-Performance Mode

echo -e "\e[1;33m⚡ STARTING NAZHAN BOTS: LIGHT SPEED MODE\e[0m"
echo -e "\e[1;30m(Disabling UI, Voice, Discord for MAX RAM)\e[0m"

# 1. Acquire Wake Lock
termux-wake-lock

# 2. Run with --lite and Python Optimization
# -O: Remove assert
# -OO: Remove docstrings
export PYTHONOPTIMIZE=2
python main.py --lite
