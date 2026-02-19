# termux_version/core/response_analyzer.py
# v16000: CONTENT-AWARE DETECTION
# Inspects HTTP Bodies for Anti-Bot signatures.

BAD_KEYWORDS = [
    "captcha",
    "challenge",
    "cloudflare",
    "security check",
    "human verification",
    "access denied",
    "rate limit",
    "403 forbidden",
    "too many requests",
    "firewall"
]

def analyze_response(status_code, text):
    """
    Returns (is_success, reason)
    """
    text = text.lower()
    
    # 1. Hard Failures
    if status_code in [403, 429, 503]:
        return False, f"HTTP {status_code}"
        
    # 2. Content Inspection
    for keyword in BAD_KEYWORDS:
        if keyword in text:
            return False, f"Detected: {keyword}"
            
    # 3. Soft Failures (JSON errors)
    if "error" in text and "message" in text:
        # Crude check for JSON error responses
        return False, "API Error Message"
        
    # 4. Success Indicators?
    if status_code in [200, 201, 202]:
        # v21000: PROMETHEUS DEEP SCAN
        # If generic 200 OK, but we want to be sure it's not a soft-block explanation
        # Only check small responses to save token/time (text < 500 chars)
        if len(text) < 500 and "{" not in text: # Suspicious if not JSON
            try:
                from .ai_core import ask_gemini
                prompt = f"Analyze this HTTP response. Is it a success or failure? Reply with only 'SUCCESS' or 'FAIL'. Response: {text}"
                # Only use AI occasionally to prevent rate limits
                if random.random() < 0.1: 
                    ai_verdict = ask_gemini(prompt)
                    if ai_verdict and "FAIL" in ai_verdict.upper():
                        return False, "AI Detected Soft-Block"
            except: pass
            
        return True, "OK"
        
    return False, f"Unknown Status {status_code}"
