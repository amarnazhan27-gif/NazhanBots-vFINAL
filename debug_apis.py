import json
import requests
import os
import time

# Load APIs
try:
    with open('termux_version/config/apis.json', 'r') as f:
        apis = json.load(f)
except:
    print("❌ Cannot load apis.json")
    exit()

target = input("Enter target number (e.g. 0812xxxx): ")
if target.startswith("0"): formatted = "62" + target[1:]
else: formatted = target

print(f"🕵️ DEBUGGING {len(apis)} APIs on {target}...")

headers_base = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

for api in apis:
    name = api['name']
    url = api['url']
    method = api.get('method', 'POST')
    data_template = api.get('data')
    
    # Process Data
    if isinstance(data_template, dict):
        data = json.dumps(data_template).replace("{phone}", target).replace("{formatted}", formatted)
        # Convert back to dict for requests
        json_data = json.loads(data)
        data_arg = None
    else:
        # Form data?
        data = str(data_template).replace("{phone}", target).replace("{formatted}", formatted)
        json_data = None
        data_arg = data

    print(f"\n👉 Testing {name} [{method}]...")
    print(f"   URL: {url}")
    
    try:
        start = time.time()
        if method == "POST":
            if json_data:
                response = requests.post(url, json=json_data, headers=headers_base, timeout=10)
            else:
                response = requests.post(url, data=data_arg, headers=headers_base, timeout=10)
        else:
            response = requests.get(url, headers=headers_base, timeout=10)
            
        latency = round(time.time() - start, 2)
        
        status = response.status_code
        try:
            resp_json = response.json()
            # print(f"   Response JSON: {str(resp_json)[:100]}...") 
            msg = str(resp_json)[:50]
        except:
            msg = response.text[:50]
            
        print(f"   [{status}] {msg} ({latency}s)")
        
        if status == 200:
            print("   ✅ SUCCESS (Potentially)")
        elif status == 429:
            print("   ⚠️ RATELIMITED")
        else:
            print("   ❌ FAILED")
            
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
