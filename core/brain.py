# termux_version/core/brain.py
import time
import threading
import json
import os
import random
try:
    from .hunter import search_new_apis
    from .validator import validate_apis
except ImportError:
    pass

# v6000 GOD'S EYE: ADAPTIVE INTELLIGENCE
# Tracks API performance and optimizes target selection.

DB_PATH = os.path.join(os.path.dirname(__file__), '../config/brain_db.json')

def load_db():
    if not os.path.exists(DB_PATH):
        return {}
    try:
        with open(DB_PATH, 'r') as f: return json.load(f)
    except: return {}

def save_db(db):
    try:
        with open(DB_PATH, 'w') as f: json.dump(db, f, indent=2)
    except: pass

def feedback(api_name, provider, status):
    # status: True (Success) / False (Fail)
    db = load_db()
    
    key = f"{api_name}|{provider}"
    if key not in db:
        db[key] = {"success": 0, "fail": 0, "score": 100}
        
    if status is True:
        db[key]["success"] += 1
    else:
        db[key]["fail"] += 1
        
    # Recalculate Score (Simple Weight)
    total = db[key]["success"] + db[key]["fail"]
    if total > 5: # Learning threshold
        ratio = db[key]["success"] / total
        db[key]["score"] = int(ratio * 100)
        
    save_db(db)

# v30000: HYPER-LEARNING
def get_api_score(api_name, provider):
    db = load_db()
    key = f"{api_name}|{provider}"
    if key not in db: return 100 # New = High Hopes
    return db[key].get("score", 50)

def should_use_api(api_name, provider):
    """
    Returns True/False based on Reinforcement Learning Score.
    Higher score = Higher chance of being picked.
    """
    score = get_api_score(api_name, provider)
    
    # Epsilon-Greedy Strategy
    # 10% chance to Explore (Random)
    if random.random() < 0.1: return True
    
    # 90% chance to Exploit (Score)
    # If score is 80, we have 80% chance to return True
    return random.randint(0, 100) <= score

# Autonomous Orchestration of Discovery -> Validation -> Integration

def brain_loop():
    print("🧠 [SINGULARITY] AI Core Online. Autonomy Engaged.")
    
    DORKS = [
        "inurl:api/otp", 
        "inurl:send_otp", 
        "inurl:auth/code",
        "inurl:verification/send",
        "site:id inurl:otp",
        "site:com inurl:api/sms"
    ]
    
    while True:
        try:
            # 1. HUNT
            current_dork = random.choice(DORKS)
            print(f"🧠 [BRAIN] Initiating Hunt Sequence: '{current_dork}'")
            search_new_apis(current_dork) 
            
            # 2. VALIDATE
            new_weapons = validate_apis()
            
            # 3. ARM (Integrate)
            if new_weapons:
                apis_path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
                
                # Load existing
                current_apis = []
                if os.path.exists(apis_path):
                    with open(apis_path, 'r') as f: current_apis = json.load(f)
                
                # Merge (Avoid duplicates)
                existing_urls = [a['url'] for a in current_apis]
                added_count = 0
                
                for weapon in new_weapons:
                    if weapon['url'] not in existing_urls:
                        # Normalize name
                        weapon['name'] = f"Auto-{random.randint(1000,9999)}"
                        current_apis.append(weapon)
                        added_count += 1
                        
                        # v31000: SWARM BROADCAST
                        # Share discovery with the Hive
                        try:
                            from .telepathy import broadcast_via_http
                            broadcast_via_http(weapon)
                        except: pass
                
                # Save
                if added_count > 0:
                    with open(apis_path, 'w') as f: json.dump(current_apis, f, indent=2)
                    print(f"🚀 [SINGULARITY] Arsenal Upgraded: +{added_count} New APIs.")
                else:
                    print("💤 [BRAIN] No new unique targets found.")
            else:
                print("💤 [BRAIN] Validation yield zero results.")
                
        except Exception as e:
            print(f"⚠️ [BRAIN] Glitch: {e}")
            
        # Cooldown between Hunts (Standard: 30 minutes, Jittered)
        sleep_time = random.randint(1800, 3600)
        print(f"🧠 [BRAIN] Standby for {sleep_time}s...")
        time.sleep(sleep_time)

def start_brain():
    t = threading.Thread(target=brain_loop)
    t.daemon = True
    t.start()
