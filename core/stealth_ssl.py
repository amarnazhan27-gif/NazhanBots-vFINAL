# termux_version/core/stealth_ssl.py
import ssl
import random

# STEALTH SSL MODULE (v10000 ETERNAL)
# Morphs TLS Fingerprints to bypass WAFs that block "Python".

def create_stealth_context():
    context = ssl.create_default_context()
    
    # List of modern ciphers used by Chrome/Firefox
    # We shuffle them to create a unique fingerprint per request
    ciphers = [
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "DHE-RSA-AES128-GCM-SHA256",
        "DHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-AES128-SHA256", # Fallback
        "ECDHE-RSA-AES128-SHA256",
        "ECDHE-ECDSA-AES256-SHA384",
        "ECDHE-RSA-AES256-SHA384",
        "AES128-GCM-SHA256", # TLS 1.3
        "AES256-GCM-SHA384",
        "CHACHA20-POLY1305-SHA256"
    ]
    
    random.shuffle(ciphers)
    cipher_string = ":".join(ciphers)
    
    try:
        context.set_ciphers(cipher_string)
        context.set_ecdh_curve("prime256v1")
        # Randomize options if possible, though restricted in standard lib
        context.options |= ssl.OP_NO_SSLv2
        context.options |= ssl.OP_NO_SSLv3
    except:
        pass # Fallback to default if system doesn't support specific ciphers
        
    return context
