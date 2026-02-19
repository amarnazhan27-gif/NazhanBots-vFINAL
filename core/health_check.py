# termux_version/core/health_check.py
import json
import os
import aiohttp
import asyncio

# DOCTOR MODULE (v40 Immortal)
# Prunes Dead APIs from the arsenal.

APIS_PATH = os.path.join(os.path.dirname(__file__), '../config/apis.json')

async def check_api_health():
    print("🩺 [DOCTOR] Checking API Health...")
    try:
        with open(APIS_PATH, 'r') as f:
            apis = json.load(f)
    except:
        return

    healthy_apis = []
    dead_count = 0
    
    async with aiohttp.ClientSession() as session:
        for api in apis:
            url = api.get("url")
            try:
                # Lightweight check (HEAD or GET)
                async with session.head(url, timeout=3) as resp:
                    if resp.status < 500: # 404 might be valid endpoint but wrong method, strictly 5xx is dead
                        healthy_apis.append(api)
                    else:
                        dead_count += 1
            except:
                # Connection error = Dead
                dead_count += 1

    if dead_count > 0:
        print(f"⚰️ [DOCTOR] Pruned {dead_count} Dead APIs.")
        with open(APIS_PATH, 'w') as f:
            json.dump(healthy_apis, f, indent=2)
    else:
        print("💚 [DOCTOR] All APIs Healthy.")

if __name__ == "__main__":
    asyncio.run(check_api_health())
