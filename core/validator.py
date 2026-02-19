# termux_version/core/validator.py
import json
import os
import requests
from .utils import get_sophisticated_headers

# VALIDATOR MODULE (v60)
# Tests discovered APIs to see if they are actually alive.

# v15000: STRICT SANITIZATION
# Ensures no garbage inputs can crash the attack engine.
def validate_number(number):
    # Remove dashes, spaces, brackets
    clean = re.sub(r'[^0-9]', '', number)
    
    # Check length
    if len(clean) < 10 or len(clean) > 15:
        return None
        
    # Formatting
    if clean.startswith("62"):
        pass # Already good
    elif clean.startswith("08"):
        clean = "62" + clean[1:]
    elif clean.startswith("8"):
        clean = "62" + clean
    else:
        # Unknown format (e.g., international) allow but warn?
        # For Indo focus, assume 62
        clean = "62" + clean
        
    return clean

def validate_apis():
    # ... (Original discovery validation logic) ...
    pass

# vFINALITY: ARSENAL MAINTENANCE (Grim Reaper)
# Scans config/apis.json and REMOVES dead endpoints (404/Error)
# Keeps the weapon system clean and efficient.

def cleanup_dead_apis():
    api_path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
    if not os.path.exists(api_path): return
    
    try:
        with open(api_path, 'r') as f: 
            apis = json.load(f)
    except: return
    
    if not apis: return
    
    print(f"💀 [VALIDATOR] Grim Reaper scanning {len(apis)} targets...")
    alive_apis = []
    dead_count = 0
    
    headers = get_sophisticated_headers()
    
    for api in apis:
        url = api.get("url")
        name = api.get("name")
        
        try:
            # PING (Post with empty data usually triggers 400/403/405 if alive)
            r = requests.post(url, headers=headers, json={}, timeout=5)
            
            # If 404, it is LIKELY dead (endpoint changed)
            if r.status_code == 404:
                print(f"⚰️ [REAPER] Burying Dead API: {name} (404)")
                dead_count += 1
                continue
                
            # If Connection Error, it is DEAD (Server down) - handled in except
            
            # Otherwise (200, 400, 403, 405, 500, 502) -> It EXISTs.
            alive_apis.append(api)
            
        except Exception:
            # Network error = Unstable or Dead. We remove it to be safe?
            # Or keep it if it's just temp?
            # For "God Mode", we want reliability. Remove if unreachable.
            print(f"⚰️ [REAPER] Burying Unreachable API: {name}")
            dead_count += 1
            
    if dead_count > 0:
        with open(api_path, 'w') as f:
            json.dump(alive_apis, f, indent=2)
        print(f"💀 [REAPER] Purged {dead_count} weak links. Arsenal size: {len(alive_apis)}")
    else:
        print("💎 [REAPER] Arsenal is 100% Healthy.")
