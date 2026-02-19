# termux_version/core/ai_core.py
import requests
import json
import os
import random

# v21000: PROMETHEUS AI (Google Gemini Integration)
# Uses Large Language Models to optimize finding targets.

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')

def get_api_key():
    try:
        with open(CONFIG_PATH, 'r') as f:
            cfg = json.load(f)
            return cfg.get("GEMINI_API_KEY")
    except: return None

CACHE_FILE = os.path.join(os.path.dirname(__file__), '../config/ai_cache.json')

def load_cache():
    if not os.path.exists(CACHE_FILE): return {}
    try:
        with open(CACHE_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_cache(cache):
    try:
        with open(CACHE_FILE, 'w') as f: json.dump(cache, f)
    except: pass

def ask_gemini(prompt):
    # v30000: AI CACHING (Speed)
    cache = load_cache()
    # Simple hash
    key = str(hash(prompt))
    if key in cache:
        # print("⚡ [AI] Cache Hit.")
        return cache[key]

    api_key = get_api_key()
    if not api_key or "YOUR" in api_key:
        return None
        
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        if response.status_code == 200:
            result = response.json()
            text = result['candidates'][0]['content']['parts'][0]['text']
            
            # Save to cache
            cache[key] = text
            save_cache(cache)
            
            return text
        else:
            print(f"⚠️ [AI] Error: {response.text}")
            return None
    except Exception as e:
        print(f"⚠️ [AI] Connection Failed: {e}")
        return None

def generate_smart_dorks():
    prompt = """
    Create 10 advanced Google Dorks to find public API endpoints for OTP or SMS sending in Indonesia.
    Format: Just the list of dorks, one per line.
    Do not explain.
    Focus on: "api/v1/send-otp", "auth/verify", "kirim_otp".
    """
    
    response = ask_gemini(prompt)
    if response:
        dorks = [line.strip() for line in response.splitlines() if line.strip() and "inurl" in line or "site" in line]
        return dorks
    
    # Fallback
    return [
        "inurl:api/v1/send-otp",
        "inurl:auth/login_otp",
        "site:id inurl:kirim_kode"
    ]

# v22000: NLP Command Processor
def interpret_command(text):
    """
    Converts natural language into JSON executable orders.
    """
    prompt = f"""
    You are the Command Interface for a script. Interpret this user request into a JSON Action.
    User: "{text}"
    
    Supported Actions:
    1. ATTACK -> {{"action": "attack", "target": "08xxx", "mode": "mix/sms/wa"}}
    2. STOP -> {{"action": "stop"}}
    3. STATUS -> {{"action": "status"}}
    4. REPORT -> {{"action": "report"}}
    5. RESET -> {{"action": "reset"}}
    6. TOR_NEW -> {{"action": "tor_new"}}
    
    Reply ONLY with the JSON. If unsure, reply {{"action": "unknown"}}.
    """
    
    response = ask_gemini(prompt)
    if not response: return {"action": "unknown"}
    
    try:
        # Clean markdown
        clean = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"action": "unknown"}

    try:
        # Clean markdown
        clean = response.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return {"action": "unknown"}
