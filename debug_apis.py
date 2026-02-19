import json
import requests
import os
import time

# Load APIs
try:
    # Try multiple paths to be safe
    override_path = os.path.join(os.path.dirname(__file__), 'config/apis.json')
    if os.path.exists(override_path):
        path = override_path
    else:
        path = 'config/apis.json'
        
    with open(path, 'r') as f:
        apis = json.load(f)
except:
    print("❌ Cannot load apis.json")
    exit()

# Helper: Clear Screen
os.system('cls' if os.name == 'nt' else 'clear')

print(f"🕵️  NAZHAN BOTS: API DIAGNOSTIC TOOL")
print(f"=========================================")

target = input("👉 Enter target number (e.g. 0812xxxx): ")
if target.startswith("0"): formatted = "62" + target[1:]
else: formatted = target

print(f"\n🚀 Scanning {len(apis)} APIs... Please wait.")
print(f"📄 Detailed logs will be saved to: debug_report.txt")
print(f"=========================================\n")

results = []
headers_base = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

with open("debug_report.txt", "w") as log_file:
    log_file.write(f"DIAGNOSTIC REPORT - {time.ctime()}\nTARGET: {target}\n\n")

    for api in apis:
        name = api['name']
        url = api['url']
        method = api.get('method', 'POST')
        data_template = api.get('data')
        
        # Process Data
        if isinstance(data_template, dict):
            data = json.dumps(data_template).replace("{phone}", target).replace("{formatted}", formatted)
            json_data = json.loads(data)
            data_arg = None
        else:
            data = str(data_template).replace("{phone}", target).replace("{formatted}", formatted)
            json_data = None
            data_arg = data

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
            
            # Outcome
            if status == 200:
                icon = "✅"
                color_code = "\033[92m" # Green
            elif status == 429:
                icon = "⚠️"
                color_code = "\033[93m" # Yellow
            else:
                icon = "❌"
                color_code = "\033[91m" # Red
                
            reset_code = "\033[0m"
            
            # Print Short to Terminal
            print(f"{icon} {name:<20} [{status}] {latency}s")
            
            # Log Full to File
            try: resp_trunc = response.text[:200].replace("\n", " ") 
            except: resp_trunc = "Binary/Error"
            
            log_entry = f"[{icon} {status}] {name}\nURL: {url}\nResp: {resp_trunc}\n{'-'*30}\n"
            log_file.write(log_entry)
            
        except Exception as e:
            print(f"❌ {name:<20} [ERROR]")
            log_file.write(f"[ERROR] {name}: {str(e)}\n{'-'*30}\n")
            
print(f"\n=========================================")
print(f"✅ SCAN COMPLETE. Check 'debug_report.txt' for details.")
