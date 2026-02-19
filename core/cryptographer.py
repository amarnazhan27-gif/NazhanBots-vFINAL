# termux_version/core/cryptographer.py
import json
import os
import base64
import subprocess

# v9000 TRANSCENDENCE: CONFIDENTIALITY
# Encrypts config files binded to Device ID.

SECRET_KEY = None

def get_device_id():
    # Attempt to get a unique ID from Termux/Android
    try:
        # Try getting Android ID via termux-telephony-deviceinfo or simple file ID
        # Fallback: generating a mostly-persistent ID based on install path + username
        raw_id = os.popen('whoami').read().strip() + os.getcwd()
        return raw_id
    except:
        return "generic_device_id"

def get_cipher_key():
    global SECRET_KEY
    if SECRET_KEY: return SECRET_KEY
    
    # Simple XOR Key generation based on Device ID
    # (In real world, use proper KDF like Argon2, but for Termux python only...)
    device_id = get_device_id()
    SECRET_KEY = device_id
    return SECRET_KEY

def xor_cipher(text, key):
    # Basic XOR encryption (Sufficient to stop casual snooping)
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(text))

def encrypt_file(filepath):
    if not os.path.exists(filepath): return
    
    try:
        with open(filepath, 'r') as f: content = f.read()
        
        # Check if already encrypted (Magic Header)
        if content.startswith("ENC::"): return
        
        key = get_cipher_key()
        encrypted = xor_cipher(content, key)
        encoded = base64.b64encode(encrypted.encode()).decode()
        
        final_content = f"ENC::{encoded}"
        
        with open(filepath, 'w') as f: f.write(final_content)
        print(f"🔒 [CRYPTO] Encrypted {os.path.basename(filepath)}")
    except Exception as e:
        print(f"❌ [CRYPTO] Encrypt Fail: {e}")

def load_encrypted_json(filepath):
    if not os.path.exists(filepath): return {}
    
    try:
        with open(filepath, 'r') as f: content = f.read()
        
        if not content.startswith("ENC::"):
            # It's plain text, return it and maybe encrypt it for next time
            data = json.loads(content)
            encrypt_file(filepath) # Auto-Encrypt on load
            return data
            
        encoded = content.split("ENC::")[1]
        decoded = base64.b64decode(encoded).decode()
        key = get_cipher_key()
        decrypted = xor_cipher(decoded, key)
        return json.loads(decrypted)
        
    except Exception as e:
        print(f"❌ [CRYPTO] Decrypt Fail: {e}")
        # Backup?
        return {}
