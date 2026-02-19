# termux_version/core/breaker.py
import os
import sys

# BREAKER MODULE (v13)
# Solves CAPTCHAs using Tesseract OCR.

try:
    import pytesseract
    from PIL import Image
    import io
except ImportError:
    pass

def solve_captcha(image_bytes):
    print("🔓 [BREAKER] Attempting to crack CAPTCHA...")
    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Preprocessing (Grayscale, Threshold)
        image = image.convert('L') 
        image = image.point(lambda x: 0 if x < 128 else 255, '1')
        
        text = pytesseract.image_to_string(image).strip()
        if text:
            print(f"✅ [BREAKER] Solved: {text}")
            return text
        else:
            print("❌ [BREAKER] Failed to recognize text.")
            return None
    except Exception as e:
        print(f"⚠️ [BREAKER] OCR Error: {e}")
        return None

def solve_turnstile(site_key, page_url):
    # v80: Cloudflare Turnstile Bypass
    # Requires CF_API_KEY in config.json
    try:
        from .security import get_config
        import requests
        import time
        
        cfg = get_config()
        api_key = cfg.get("CF_API_KEY")
        
        if not api_key or "YOUR" in api_key:
            print("⚠️ [BREAKER] No CAPTCHA Key found.")
            return None
            
        print("🔓 [BREAKER] Bypassing Cloudflare Turnstile...")
        
        # 1. Create Task (CapMonster Example)
        task_payload = {
            "clientKey": api_key,
            "task": {
                "type": "TurnstileTask",
                "websiteURL": page_url,
                "websiteKey": site_key
            }
        }
        
        r = requests.post("https://api.capmonster.cloud/createTask", json=task_payload)
        if r.json().get("errorId") != 0:
            return None
            
        task_id = r.json().get("taskId")
        
        # 2. Poll Result
        for _ in range(30):
            time.sleep(1)
            res = requests.post("https://api.capmonster.cloud/getTaskResult", json={"clientKey": api_key, "taskId": task_id})
            if res.json().get("status") == "ready":
                token = res.json().get("solution", {}).get("token")
                print(f"✅ [BREAKER] Turnstile Solved!")
                return token
                
        return None
    except Exception as e:
        print(f"❌ [BREAKER] Solver Error: {e}")
        return None
