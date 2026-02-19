# termux_version/core/resolver.py
import requests
import socket
import json
import random

# v8000 OMNIPOTENT: DNS OVER HTTPS (DoH)
# Bypasses ISP Censorship (Nawala/Internet Positif)

DOH_PROVIDERS = [
    "https://cloudflare-dns.com/dns-query",
    "https://dns.google/resolve",
    "https://dns.quad9.net/dns-query", # Quad9
    "https://doh.opendns.com/dns-query", # OpenDNS
    "https://dns.adguard.com/dns-query", # AdGuard
]

DNS_CACHE = {}

def resolve_domain(domain):
    global DNS_CACHE
    if domain in DNS_CACHE:
        return DNS_CACHE[domain]
        
    # Try DoH first
    for provider in DOH_PROVIDERS:
        try:
            params = {"name": domain, "type": "A"}
            headers = {"Accept": "application/dns-json"}
            
            r = requests.get(provider, params=params, headers=headers, timeout=2)
            if r.status_code == 200:
                data = r.json()
                if "Answer" in data:
                    ip = data["Answer"][0]["data"]
                    DNS_CACHE[domain] = ip
                    # print(f"🛡️ [DoH] Resolved {domain} -> {ip}")
                    return ip
        except:
            continue
            
    # Fallback to system DNS
    try:
        ip = socket.gethostbyname(domain)
        return ip
    except:
        return None

def patch_url(url):
    # Replaces domain in URL with IP, sets Host header
    try:
        from urllib.parse import urlparse, urlunparse
        parsed = urlparse(url)
        domain = parsed.netloc
        
        ip = resolve_domain(domain)
        if ip:
            # Reconstruct URL with IP
            new_netloc = ip
            new_url = list(parsed)
            new_url[1] = new_netloc
            final_url = urlunparse(new_url)
            return final_url, domain # Return patched URL and original Host
    except:
        pass
    return url, None
