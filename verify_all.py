import os
import sys
import json
import time
import socket

# Force Color
G = "\033[92m"
R = "\033[91m"
Y = "\033[93m"
W = "\033[0m"

def log(status, msg):
    if status == "OK":
        print(f"[{G}OK{W}] {msg}")
    elif status == "WARN":
        print(f"[{Y}WARN{W}] {msg}")
    elif status == "FAIL":
        print(f"[{R}FAIL{W}] {msg}")

print(f"{G}========================================")
print(f"   NAZHAN BOTS - SYSTEM INTEGRITY CHECK")
print(f"========================================{W}")

# 1. Environment Check
log("OK", f"Python Version: {sys.version.split()[0]}")
log("OK", f"Working Directory: {os.getcwd()}")

# 2. Dependency Check
params = [
    ("requests", "Network Module"),
    ("telebot", "Telegram Module"),
    ("psutil", "System Monitor"),
    ("rich", "UI Library"),
    ("aiohttp", "Async Network"),
]

for lib, name in params:
    try:
        __import__(lib)
        log("OK", f"{name} ({lib}) Installed")
    except ImportError:
        log("FAIL", f"{name} ({lib}) MISSING. Run: pip install -r requirements.txt")

# 3. Path Resolution
# Try to find root directory by looking for 'main.py'
current = os.path.abspath(os.getcwd())
root_dir = None
if os.path.exists(os.path.join(current, "main.py")):
    root_dir = current
elif os.path.exists(os.path.join(current, "termux_version", "main.py")):
    root_dir = os.path.join(current, "termux_version")
elif "termux_version" in current:
    # We might be inside deep folder
    # traverse up until we find main.py or config
    temp = current
    while len(temp) > 5:
        if os.path.exists(os.path.join(temp, "main.py")):
            root_dir = temp
            break
        temp = os.path.dirname(temp)

if not root_dir:
    # Last ditch: assume we are in the folder where this script is, and main.py is next to it
    script_dir = os.path.dirname(os.path.abspath(__file__))
    if os.path.exists(os.path.join(script_dir, "main.py")):
        root_dir = script_dir
    else:
        log("FAIL", "Could not locate Project Root (main.py not found)")
        sys.exit(1)

log("OK", f"Project Root Detected: {root_dir}")

# 4. Config Check
config_path = os.path.join(root_dir, "config", "config.json")
apis_path = os.path.join(root_dir, "config", "apis.json")

if os.path.exists(config_path):
    try:
        with open(config_path, "r") as f:
            cfg = json.load(f)
            token = cfg.get("TELEGRAM_BOT_TOKEN", "")
            chat_id = cfg.get("TELEGRAM_CHAT_ID", "")
            
            if ":" in token:
                log("OK", f"Telegram Token Format Valid ({token[:5]}...)")
            else:
                log("FAIL", "Telegram Token Invalid!")
                
            if chat_id and str(chat_id) != "0":
                log("OK", f"Telegram Chat ID Set ({chat_id})")
            else:
                log("WARN", "Telegram Chat ID not set or 0")
    except Exception as e:
        log("FAIL", f"Config Corrupt: {e}")
else:
    log("FAIL", f"Config Missing: {config_path}")

if os.path.exists(apis_path):
    try:
        with open(apis_path, "r") as f:
            apis = json.load(f)
            log("OK", f"APIs Loaded: {len(apis)} endpoints")
            
            # Sub-check
            valid = 0
            for a in apis:
                if "url" in a and "name" in a: valid += 1
            log("OK", f"Valid API Structures: {valid}/{len(apis)}")
    except Exception as e:
        log("FAIL", f"APIs Corrupt: {e}")
else:
    log("FAIL", f"APIs Missing: {apis_path}")

# 5. Network Check
try:
    socket.create_connection(("8.8.8.8", 53), timeout=3)
    log("OK", "Internet Connection Active")
except:
    log("FAIL", "No Internet Connection")

# 6. Core Module Import
sys.path.append(root_dir)
try:
    from core.attacker import start_async_attack
    log("OK", "Core: Attacker Module Valid")
except ImportError as e:
    log("FAIL", f"Core: Attacker Import Failed ({e})")

try:
    from core.telegram_c2 import start_bot
    log("OK", "Core: Telegram C2 Valid")
except ImportError as e:
    log("FAIL", f"Core: Telegram C2 Import Failed ({e})")

print(f"\n{G}========================================")
print(f"   VERIFICATION COMPLETE")
print(f"========================================{W}")
print("If you see any [FAIL], please fix before running.")
print("If all are [OK], you are ready to launch.")
