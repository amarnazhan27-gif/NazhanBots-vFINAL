# termux_version/core/syncer.py
import requests
import json
import os

# SYNCER MODULE (v110 INFINITY)
# Connects to the Global Hive Mind to fetch new APIs.

MASTER_REPO_URL = "https://raw.githubusercontent.com/amarnazhan-official/superior-db/main/apis.json"

def sync_from_hive():
    print("☁️ [INFINITY] Syncing with Global Hive Mind...")
    try:
        r = requests.get(MASTER_REPO_URL, timeout=10)
        if r.status_code != 200:
            print("⚠️ [INFINITY] Hive Unreachable.")
            return

        new_data = r.json()
        
        # Merge logic
        local_path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
        if os.path.exists(local_path):
            with open(local_path, 'r') as f: local_data = json.load(f)
        else:
            local_data = []
            
        existing_urls = [a['url'] for a in local_data]
        added = 0
        
        for api in new_data:
            if api['url'] not in existing_urls:
                local_data.append(api)
                added += 1
                
        if added > 0:
            with open(local_path, 'w') as f: json.dump(local_data, f, indent=2)
            print(f"✅ [INFINITY] Absorbed {added} new APIs from Hive.")
        else:
            print("💤 [INFINITY] Local Database is up to date.")
            
    except Exception as e:
        print(f"⚠️ [INFINITY] Sync Error: {e}")
