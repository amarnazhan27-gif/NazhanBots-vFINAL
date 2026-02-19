# check_api.py
import requests
import json
import os
from concurrent.futures import ThreadPoolExecutor

# vCHECKER: Verify "Life" of APIs without clicking them
# APIs expect POST requests with data, not Browser GETs.

def check_single(api):
    url = api.get("url")
    name = api.get("name")
    method = api.get("method", "POST")
    
    try:
        # We send a dummy POST request. 
        # - 200 OK: Alive & Working
        # - 400 Bad Request: Alive (Server got our request but rejected empty data) -> GOOD!
        # - 405 Method Not Allowed: Alive (Server exists) -> GOOD!
        # - 403 Forbidden: Alive (WAF Blocked us) -> GOOD (It exists!)
        # - 404 Not Found: DEAD (Endpoint changed) -> BAD.
        # - Connection Error: DEAD/Down.
        
        headers = {"User-Agent": "Mozilla/5.0"}
        r = requests.post(url, headers=headers, timeout=5)
        
        status = r.status_code
        
        if status in [404, 500, 502]:
            print(f"❌ {name}: DEAD (Status {status})")
        else:
            print(f"✅ {name}: ALIVE (Status {status} - Server Responded)")
            
    except Exception as e:
        print(f"⚠️ {name}: UNREACHABLE ({str(e)[:20]}...)")

def main():
    print("🔍 [CHECKER] PINGING ALL WARHEADS...")
    # Fix: Use absolute path relative to script location
    path = os.path.join(os.path.dirname(__file__), 'config/apis.json')
    if not os.path.exists(path):
        print(f"❌ config/apis.json not found at {path}")
        return
        
    with open(path) as f:
        apis = json.load(f)
        
    print(f"📋 Checking {len(apis)} APIs...")
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(check_single, apis)
        
    print("\n💡 NOTE: Status 400/403/405 means the API is ALIVE.")
    print("❌ Only Status 404 means it might be dead.")

if __name__ == "__main__":
    main()
