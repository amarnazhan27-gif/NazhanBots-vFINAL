# termux_version/core/hunter.py
import requests
import re
import json
import os
import urllib.parse
from bs4 import BeautifulSoup
from .utils import get_sophisticated_headers

# HUNTER MODULE (v9)
# Auto-Discovers new OTP APIs using Google Dorks.

# HUNTER MODULE (v50 UNIVERSE)
# Use simulated browsing to find live API endpoints from search engines.

# HUNTER MODULE (v21000 PROMETHEUS)
# Auto-Discovers new OTP APIs using AI-Generated Dorks.

try:
    from .ai_core import generate_smart_dorks
except ImportError:
    generate_smart_dorks = None

def search_new_apis(dork=None):
    if dork:
        dorks = [dork]
    else:
        # v21000: AI Generated Dorks
        if generate_smart_dorks:
            print("🧠 [AI] Generating Advanced Dorks via Gemini...")
            dorks = generate_smart_dorks() or ["inurl:api/otp", "inurl:send_otp"]
            print(f"🧠 [AI] Generated {len(dorks)} strategies.")
        else:
             dorks = ["inurl:api/otp", "inurl:send_otp"]

    print(f"🏹 [HUNTER] Starting Hunt with {len(dorks)} Dorks...")
    headers = get_sophisticated_headers()
    
    # Fix: Define search_url
    target_dork = dorks[0]
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(target_dork)}"
    
    try:
        print(f"    🔎 Querying: {search_url[:60]}...")
        resp = requests.get(search_url, headers=headers, timeout=10)
        
        # v35000: Anti-Ban Check
        if resp.status_code == 429:
            print("⚠️ [HUNTER] Google detected us. Backing off.")
            return

        if resp.status_code != 200:
             return

        soup = BeautifulSoup(resp.text, 'html.parser')
        
        found_links = []
        for link in soup.find_all('a', class_='result__a'):
            href = link.get('href')
            if href and "http" in href:
                found_links.append(href)
                print(f"👁️ [HUNTER] Sighted: {href}")
                
        # 2. Verify Targets
        valid_apis = []
        for url in found_links[:5]: # Check top 5
             # Simple heuristical check
             if "api" in url or "otp" in url:
                 valid_apis.append({
                     "name": f"Hunter-{len(valid_apis)+1}",
                     "url": url,
                     "method": "POST",
                     "data": {"phone": "{number}"},
                     "provider": "autodiscovered"
                 })
                 
        # Save results
        if valid_apis:
             print(f"✅ [HUNTER] Captured {len(valid_apis)} new entities.")
             path = os.path.join(os.path.dirname(__file__), '../config/discovered_apis.json')
             with open(path, 'w') as f:
                 json.dump(valid_apis, f, indent=2)
        else:
             print("❌ [HUNTER] No viable targets found in this sector.")
             
    except Exception as e:
        print(f"⚠️ [HUNTER] Network Failure: {e}")
