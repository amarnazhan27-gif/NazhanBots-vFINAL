# termux_version/core/security.py
import json
import os
import subprocess

# v65 OVERLORD: SECURITY CORE
# Manages Access Control and Restricted Operations (Shell).

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')

def get_config():
    try:
        from .cryptographer import load_encrypted_json
        return load_encrypted_json(CONFIG_PATH)
    except:
        return {}

# v3000 SENTINEL: AUTH OTP SYSTEM
import random
import string

OTP_FILE = os.path.join(os.path.dirname(__file__), 'auth_otp.txt')

def generate_otp():
    otp = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    with open(OTP_FILE, 'w') as f:
        f.write(otp)
    print(f"\n🔐 [SENTINEL] AUTH REQUIRED! Send this code to bot: /claim {otp}")
    return otp

def verify_claim(user_id, token, platform="telegram"):
    if not os.path.exists(OTP_FILE): return False
    
    with open(OTP_FILE, 'r') as f: real_otp = f.read().strip()
    
    if token.strip() == real_otp:
        # Save Owner
        config = get_config()
        key = "OWNER_ID" if platform == "telegram" else "DISCORD_OWNER_ID"
        config[key] = str(user_id)
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
            
        # Delete OTP to prevent reuse
        os.remove(OTP_FILE)
        return True
    return False

def is_owner(user_id, platform="telegram"):
    config = get_config()
    owner_id = config.get("OWNER_ID") if platform == "telegram" else config.get("DISCORD_OWNER_ID")
    
    # v3000: STRICT MODE
    if not owner_id or str(owner_id) == "0":
        return False # DENY ALL until claimed.
        
    return str(user_id) == str(owner_id)

def run_shell(command):
    # DANGEROUS: Executes terminal commands
    try:
        # Timeout to prevent hanging
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, timeout=30)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e:
        return f"❌ Command Failed:\n{e.output.decode('utf-8')}"
    except subprocess.TimeoutExpired:
        return "❌ Timeout: Command took too long."
    except Exception as e:
        return f"❌ Error: {e}"

# v31000: SCORCHED EARTH PROTOCOL
def scorched_earth():
    """
    NUCLEAR OPTION: Deletes all sensitive data and self-destructs.
    Triggered by extreme integrity violation or remote kill switch.
    """
    print("☢️ [SECURITY] SCORCHED EARTH INITIATED. WIPING DATA...")
    try:
        if os.path.exists(CONFIG_PATH): os.remove(CONFIG_PATH)
        if os.path.exists(OTP_FILE): os.remove(OTP_FILE)
        apis_path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
        if os.path.exists(apis_path): os.remove(apis_path)
        
        # Corrupt self
        with open(__file__, 'w') as f: f.write("# WIPE")
        
        print("☠️ SYSTEM DEAD.")
        os._exit(0)
    except:
        os._exit(0)
