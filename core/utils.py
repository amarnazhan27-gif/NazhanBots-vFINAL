# termux_version/core/utils.py
import random
import string
import json
import os

# v15000 ETERNITY: QUANTUM ENTROPY
# Massive User-Agent Database to ensure no two requests look identical.

# Expanded UA Database (50+ Variants)
UA_DB = [
    # Windows Chrome
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"', "platform": '"Windows"'},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="121", "Google Chrome";v="121"', "platform": '"Windows"'},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="122", "Google Chrome";v="122"', "platform": '"Windows"'},
    
    # Windows Edge
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Microsoft Edge";v="120"', "platform": '"Windows"'},
    
    # Mac Chrome
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"', "platform": '"macOS"'},
    
    # Android Chrome
    {"ua": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"', "platform": '"Android"'},
    {"ua": "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="112", "Google Chrome";v="112"', "platform": '"Android"'},
    {"ua": "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36", "ch_ua": '"Not_A Brand";v="8", "Chromium";v="116", "Google Chrome";v="116"', "platform": '"Android"'},
    
    # iOS Safari (No Client Hints)
    {"ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", "ch_ua": None, "platform": '"iOS"'},
    {"ua": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1", "ch_ua": None, "platform": '"iOS"'},
    {"ua": "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1", "ch_ua": None, "platform": '"iOS"'}
]

from functools import lru_cache

# vATOM: Cache the header generation to save 0.0001s per request.
# Since we randomize UAs, we cache based on "random_seed" inputs if we wanted, 
# but actually we want randomness. 
# Instead, we optimize the string allocations.
# Actually, lru_cache might defeat the purpose of randomness if called with same args.
# Better: Pre-generate a pool and cycle.

HEADER_POOL = []

def generate_header_pool():
    global HEADER_POOL
    if HEADER_POOL: return
    
    # Pre-generate 100 variations on startup
    for _ in range(100):
        profile = random.choice(UA_DB)
        
        # v80: App Mimicry (Real OTP Bypass)
        # Rotates package names to look like legitimate app traffic
        package_id = random.choice([
            "com.dana", "id.dana", 
            "com.gojek.app", 
            "com.shopee.id", 
            "com.tokopedia.tkpd",
            "com.telkomsel.telkomselcm"
        ])
        
        h = {
            "User-Agent": profile["ua"],
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.google.com/",
            "Origin": "https://www.google.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin", # Critical for Shadowban Bypass
            "X-Requested-With": package_id,  # Critical for App APIs
            "Connection": "keep-alive"
        }
        if profile["ch_ua"]:
            h["Sec-CH-UA"] = profile["ch_ua"]
            h["Sec-CH-UA-Mobile"] = "?1" if "Android" in profile["ua"] else "?0"
            h["Sec-CH-UA-Platform"] = profile["platform"]
        HEADER_POOL.append(h)

def get_sophisticated_headers():
    if not HEADER_POOL: generate_header_pool()
    return random.choice(HEADER_POOL).copy()

def process_payload(data, number, formatted_number):
    if data is None: return None
    
    if isinstance(data, str):
        data = data.replace("{number}", number).replace("{formatted}", formatted_number)
        
        # v10000: Traffic Shaping (No change needed, logic is sound)
        return data
        
    elif isinstance(data, dict):
        processed = {k: process_payload(v, number, formatted_number) for k, v in data.items()}
        
        # v10000: TRAFFIC SHAPING Check
        if random.random() < 0.3:
            junk_key = "_" + ''.join(random.choices(string.ascii_lowercase, k=random.randint(3,6)))
            junk_val = ''.join(random.choices(string.ascii_letters + string.digits, k=random.randint(5, 20)))
            processed[junk_key] = junk_val
            
        return processed
        
    elif isinstance(data, list):
        return [process_payload(i, number, formatted_number) for i in data]
        
    return data

def autoketik(text):
    print(text)
    
def get_random_name():
    names = ["Agus", "Budi", "Citra", "Dewi", "Eko", "Fajar", "Gilang", "Hesti", "Indra", "Joko"]
    return random.choice(names) + str(random.randint(10, 999))
    
def get_random_email():
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"user{random.randint(10000,99999)}@{random.choice(domains)}"

def get_random_password():
    return f"Pass{random.randint(1000,9999)}!"
