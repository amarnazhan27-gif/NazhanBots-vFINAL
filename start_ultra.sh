#!/bin/bash
echo -e "\e[1;31m🚀 STARTING ULTRA-LITE MODE (NO LIMITS)\e[0m"

# Kill everything else
pkill -f python || true

# Run Ultra Script
python -u ultra.py
