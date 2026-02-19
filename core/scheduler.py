# termux_version/core/scheduler.py
import json
import os
import time
import threading
import asyncio
from .attacker import start_async_attack

# v18000: OMEGA AUTOMATION
# Runs attacks automatically based on schedule.json

SCHEDULE_FILE = os.path.join(os.path.dirname(__file__), '../config/schedule.json')
APIS_FILE = os.path.join(os.path.dirname(__file__), '../config/apis.json')

def load_schedule():
    if not os.path.exists(SCHEDULE_FILE): return []
    try:
        with open(SCHEDULE_FILE, 'r') as f: return json.load(f)
    except json.JSONDecodeError:
        print("⚠️ [SCHEDULER] Corrupt schedule.json. Skipping.")
        return []
    except: return []

def load_apis():
    if not os.path.exists(APIS_FILE): return []
    try:
        with open(APIS_FILE, 'r') as f: return json.load(f)
    except: return []

def scheduler_loop():
    print("⏰ [SCHEDULER] Timekeeper Active.")
    while True:
        tasks = load_schedule()
        current_time = time.strftime("%H:%M")
        
        for task in tasks:
            # Task format: {"time": "14:30", "target": "081234", "duration": 60}
            if task.get("time") == current_time:
                # Check if already ran today? (Simple check: store last run date in memory)
                # For high-frequency bot logic, strict once-per-minute trigger is acceptable.
                
                print(f"⏰ [SCHEDULER] Triggering scheduled hit on {task['target']}...")
                
                apis = load_apis()
                if apis:
                    # Run in separate thread to not block scheduler
                    threading.Thread(target=run_async_wrapper, args=(apis, task['target'], task.get('duration', 60))).start()
                    
                # Sleep 60s to avoid double trigger in same minute
                time.sleep(60)
                
        time.sleep(10)

def run_async_wrapper(apis, target, duration):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_async_attack(apis, target, duration))
    loop.close()

def start_scheduler():
    t = threading.Thread(target=scheduler_loop, name="Nazhan_Scheduler")
    t.daemon = True
    t.start()
    return t
