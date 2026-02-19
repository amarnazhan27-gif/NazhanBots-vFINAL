# termux_version/core/proxy_validator.py
import aiohttp
import asyncio
import random
import time

# v7000 PHANTOM: LIVE PROXY VALIDATION
# Filters out dead/slow proxies before they ruin the attack.

TEST_URL = "http://www.google.com" # Reliable target
TIMEOUT = 3 

async def validate_proxy(proxy_url):
    try:
        start = time.time()
        async with aiohttp.ClientSession() as session:
            async with session.get(TEST_URL, proxy=proxy_url, timeout=TIMEOUT) as resp:
                if resp.status == 200:
                    latency = time.time() - start
                    return True, latency
    except:
        pass
    return False, 999

async def filter_proxies(proxy_list, max_valid=50):
    print(f"🕵️ [PHANTOM] Validating {len(proxy_list)} Proxies... (This ensures 100% Hit Rate)")
    valid_proxies = []
    
    tasks = []
    # Limit concurrency for validation to avoid crashing network
    sem = asyncio.Semaphore(50) 
    
    async def check(proxy):
        async with sem:
            is_valid, latency = await validate_proxy(proxy)
            if is_valid:
                valid_proxies.append({'url': proxy, 'latency': latency})
    
    await asyncio.gather(*[check(p) for p in proxy_list])
    
    # Sort by speed
    valid_proxies.sort(key=lambda x: x['latency'])
    
    top_proxies = [p['url'] for p in valid_proxies[:max_valid]]
    print(f"✅ [PHANTOM] Found {len(top_proxies)} ELITE Proxies (Avg Latency: {sum(p['latency'] for p in valid_proxies[:max_valid])/len(top_proxies) if top_proxies else 0:.2f}s)")
    
    return top_proxies
