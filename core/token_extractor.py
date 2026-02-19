# termux_version/core/token_extractor.py
import re

# HUNTER MODULE
# Extracts hidden tokens from HTML for bypass.

def extract_csrf_token(html):
    # Django / Laravel style
    patterns = [
        r'name="csrf-token" content="([^"]+)"',
        r'name="_token" value="([^"]+)"',
        r'id="csrf_token" value="([^"]+)"'
    ]
    
    for p in patterns:
        match = re.search(p, html)
        if match:
            return match.group(1)
            
    return None

def extract_api_keys(html):
    # Common JS keys
    patterns = [
        r'api_key\s*:\s*["\']([^"\']+)["\']',
        r'apiKey\s*=\s*["\']([^"\']+)["\']'
    ]
    
    for p in patterns:
        match = re.search(p, html)
        if match:
            return match.group(1)
            
    return None
