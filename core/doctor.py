# termux_version/core/doctor.py
import os
import sys
import socket
import time

# DOCTOR MODULE (v999 OMEGA)
# Performs self-diagnostics before system launch to prevent crashes.

def check_internet():
    try:
        # Google DNS check
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False

def check_dependencies():
    missing = []
    try: import aiohttp
    except ImportError: missing.append("aiohttp")
    
    try: import requests
    except ImportError: missing.append("requests")
    
    try: import psutil
    except ImportError: missing.append("psutil")
    
    try: import rich
    except ImportError: missing.append("rich")
    
    try: import discord
    except ImportError: missing.append("discord")
    
    return missing

def check_config():
    config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
    if not os.path.exists(config_path):
        return False, "Config Missing"
    
    import json
    try:
        with open(config_path, 'r') as f:
            data = json.load(f)
            if "TELEGRAM_BOT_TOKEN" not in data: return False, "Token Missing"
    except:
        return False, "Config Corrupt"
        
    return True, "OK"

def diagnose():
    print("🩺 [DOCTOR] System Diagnostic Initiated...")
    
    # 1. Internet
    if not check_internet():
        print("⚠️ [DOCTOR] No Internet Connection. System might fail to sync.")
        # We don't exit, we just warn, because local features might work.
    else:
        print("✅ [DOCTOR] Connection: Stable")

    # 1.5 Binaries Check (v33000)
    import shutil
    binaries = ["tor", "termux-tts-speak", "git"]
    missing_bin = [b for b in binaries if not shutil.which(b)]
    if missing_bin:
        print(f"⚠️ [DOCTOR] Missing System Tools: {', '.join(missing_bin)}")
        print("   👉 Run: pkg install tor termux-api git")
    else:
        print("✅ [DOCTOR] System Tools: Ready")

    # 2. Dependencies
    missing_libs = check_dependencies()
    if missing_libs:
        print(f"❌ [DOCTOR] Critical Dependencies Missing: {', '.join(missing_libs)}")
        print("   👉 Run: pip install -r requirements.txt")
        # In OMEGA, we try to auto-fix?
        # Guardian should have fixed this, but if we are manually running python main.py...
        sys.exit(1)
    else:
        print("✅ [DOCTOR] Libraries: Intact")

    # 3. Config
    cfg_ok, cfg_msg = check_config()
    if not cfg_ok:
        print(f"⚠️ [DOCTOR] Configuration Issue: {cfg_msg}. Using Defaults/Environment.")
    else:
        print("✅ [DOCTOR] Config: Loaded")
        
    print("✅ [DOCTOR] Diagnostic Complete. System Healthy.")
