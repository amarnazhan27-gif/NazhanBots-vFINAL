# termux_version/core/integrity.py
import hashlib
import os
import json
import sys

# v10000 FINALITY: SELF-AWARE INTEGRITY
# Ensures code has not been tampered with.

CHECKSUM_FILE = os.path.join(os.path.dirname(__file__), '../config/checksums.enc')

def calculate_file_hash(filepath):
    sha256 = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(65536)
                if not data: break
                sha256.update(data)
        return sha256.hexdigest()
    except: return None

def generate_checksums():
    print("🛡️ [INTEGRITY] Generating Golden Hashes...")
    hashes = {}
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Scan Core and Config (Skipping logs and dynamic dbs)
    for root, dirs, files in os.walk(base_dir):
        if "logs" in root or "__pycache__" in root: continue
        
        for file in files:
            if file.endswith(".py") or file.endswith(".sh") or file.endswith(".json"):
                if "checksums" in file or "brain_db" in file: continue
                
                path = os.path.join(root, file)
                rel_path = os.path.relpath(path, base_dir)
                hashes[rel_path] = calculate_file_hash(path)
                
    # Save Encrypted (Simple Obfuscation so users don't just edit it easily)
    # We use our cryptographer if available
    try:
        from .cryptographer import get_cipher_key, xor_cipher
        import base64
        
        json_str = json.dumps(hashes)
        key = get_cipher_key()
        encrypted = xor_cipher(json_str, key)
        encoded = base64.b64encode(encrypted.encode()).decode()
        
        with open(CHECKSUM_FILE, 'w') as f: f.write(encoded)
        print(f"✅ [INTEGRITY] System Sealed. ({len(hashes)} files hashed)")
    except Exception as e:
        print(f"❌ [INTEGRITY] Generation Failed: {e}")

def verify_integrity():
    if not os.path.exists(CHECKSUM_FILE):
        print("⚠️ [INTEGRITY] Checksum file missing. First run?")
        # generate_checksums() # Optional: Auto-generate on first run?
        # Dangerous if attacker deletes it. better to fail or warn.
        return True 

    print("🛡️ [INTEGRITY] Verifying System Identity...")
    try:
        from .cryptographer import get_cipher_key, xor_cipher
        import base64
        
        with open(CHECKSUM_FILE, 'r') as f: encoded = f.read()
        
        key = get_cipher_key()
        decoded = base64.b64decode(encoded).decode()
        json_str = xor_cipher(decoded, key)
        golden_hashes = json.loads(json_str)
        
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        violation = False
        for rel_path, golden_hash in golden_hashes.items():
            full_path = os.path.join(base_dir, rel_path)
            
            if not os.path.exists(full_path):
                print(f"❌ [INTEGRITY] MISSING FILE: {rel_path}")
                violation = True
                continue
                
            current_hash = calculate_file_hash(full_path)
            if current_hash != golden_hash:
                print(f"❌ [INTEGRITY] MODIFIED FILE: {rel_path}")
                violation = True
                
        if violation:
            print("\n🚨 [SYSTEM COMPROMISED] CRITICAL INTEGRITY FAILURE")
            print("⚠️ UNAUTHORIZED MODIFICATION DETECTED.")
            print("⚠️ INITIATING DATA FACTORY RESET...")
            
            # Aggressive Defense: Delete Configs or Logs?
            # Or just exit.
            # v9000: Shred config
            try:
                from .shredder import secure_delete
                secure_delete(os.path.join(base_dir, 'config/config.json'))
            except: pass
            
            sys.exit(1)
            
        print("✅ [INTEGRITY] System Clean. Identity Verified.")
        return True
        
    except Exception as e:
        print(f"❌ [INTEGRITY] Verification Error: {e}")
        # Fail safe
        return False
