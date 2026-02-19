# verify_integrity.py
import os
import json
import sys

# GOD MODE INTEGRITY CHECKER
# Verifies that every single atom of Project Superior is present.

REQUIRED_FILES = [
    "main.py",
    "requirements.txt",
    "core/__init__.py",
    "core/attacker.py",
    "core/breaker.py",
    "core/cleaner.py",
    "core/health_check.py",
    "core/hunter.py",
    "core/proxy_scraper.py",
    "core/reporter.py",
    "core/telegram_c2.py",
    "core/token_extractor.py",
    "core/utils.py",
    "config/apis.json",
    "config/config.json",
    "config/proxies.txt",
    "config/whitelist.json",
    "config/schedule.json",
    "config/discovered_apis.json",
    "templates/index.html",
    "templates/login.html",
    "logs/.gitkeep"
]

def check_integrity():
    print("🛡️ [GOD MODE] INITIATING SYSTEM INTEGRITY SCAN...")
    missing = []
    
    for rel_path in REQUIRED_FILES:
        full_path = os.path.join(os.path.dirname(__file__), rel_path)
        if not os.path.exists(full_path):
            missing.append(rel_path)
            print(f"❌ MISSING: {rel_path}")
        else:
            print(f"✅ OK: {rel_path}")
            
    # Check JSON validity
    json_files = [f for f in REQUIRED_FILES if f.endswith(".json")]
    for jf in json_files:
        try:
            with open(os.path.join(os.path.dirname(__file__), jf), 'r') as f:
                json.load(f)
        except json.JSONDecodeError:
            print(f"❌ CORRUPTED JSON: {jf}")
            missing.append(f"{jf} (Corrupted)")

    print("-" * 30)
    if missing:
        print(f"💀 CRITICAL FAILURE: {len(missing)} FILES MISSING/CORRUPT.")
        print("DO NOT DEPLOY. REDOWNLOAD SOURCE.")
        sys.exit(1)
    else:
        print("💎 INTEGRITY 100%. SYSTEM IS GOD-TIER.")
        print("READY FOR DEPLOYMENT.")
        sys.exit(0)

if __name__ == "__main__":
    check_integrity()
