# termux_version/core/proxy_scraper.py
import requests
import os
import random

# vInfinity: RESILIENT PROXY ENGINE (MULTI-SOURCE)
# Scrapes from 10+ robust repositories to ensure we always have fuel.

PROXY_FILE = os.path.join(os.path.dirname(__file__), '../config/proxies.txt')

# Backup list (Known good public proxies - Expanded)
STATIC_FALLBACKS = [
    "http://20.210.113.32:8123", "http://45.192.152.170:8080",
    "http://203.24.166.242:80", "http://103.152.112.162:80",
    "http://128.199.237.57:8080", "http://167.172.84.156:3128", 
    "http://159.203.84.241:3128", "http://198.199.86.11:3128",
    "http://188.166.215.127:3128", "http://138.68.161.14:3128"
]

SOURCES = [
    "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
    "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
    "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt",
    "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt"
]

def scrape_proxies():
    print("🌍 [PROXY] Scavenging Global Proxies (Deep Web)...")
    proxies = set()
    
    # 1. Try Scrape
    for url in SOURCES:
        try:
            print(f"   Searching: {url.split('/')[2]}...")
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                count = 0
                for line in r.text.splitlines():
                    if ":" in line and "#" not in line:
                        clean = line.strip()
                        if not clean.startswith("http"): clean = f"http://{clean}"
                        proxies.add(clean)
                        count += 1
                # print(f"   -> Found {count}")
        except:
            continue
            
    # 2. Mix in Fallbacks
    for p in STATIC_FALLBACKS:
        proxies.add(p)
        
    # 3. Save
    if len(proxies) > 0:
        with open(PROXY_FILE, "w") as f:
            f.write("\n".join(proxies))
        print(f"✅ [PROXY] Updated Repository: {len(proxies)} Active Nodes.")
    else:
        print("⚠️ [PROXY] Network Down. Using Emergency Backup.")
        with open(PROXY_FILE, "w") as f:
            f.write("\n".join(STATIC_FALLBACKS))
            
def get_random_proxy():
    if not os.path.exists(PROXY_FILE):
        scrape_proxies()
        
    try:
        with open(PROXY_FILE, "r") as f:
            lines = f.readlines()
            if not lines: return None
            return random.choice(lines).strip()
    except:
        return random.choice(STATIC_FALLBACKS)
