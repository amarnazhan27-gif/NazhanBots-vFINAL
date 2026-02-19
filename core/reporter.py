# termux_version/core/reporter.py
import json
import os
import aiohttp
import asyncio

# REPORTER MODULE
# Logs success and counts statistics.

LOG_FILE = os.path.join(os.path.dirname(__file__), '../logs/success.txt')
STATS_FILE = os.path.join(os.path.dirname(__file__), '../logs/stats.json')

def get_stats():
    # Return total hits
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                data = json.load(f)
                return data.get("total_hits", 0)
        except:
            return 0
    return 0

def log_success(name, number, mode):
    # 1. Update Stats
    current_stats = {}
    if os.path.exists(STATS_FILE):
        try:
            with open(STATS_FILE, 'r') as f:
                current_stats = json.load(f)
        except: pass
    
    current_stats["total_hits"] = current_stats.get("total_hits", 0) + 1
    
    with open(STATS_FILE, 'w') as f:
        json.dump(current_stats, f)
        
    # 2. Append to Log
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {name} -> {number} ({mode})\n"
    
    # Ensure logs folder exists
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    with open(LOG_FILE, 'a') as f:
        f.write(entry)
