# termux_version/core/shredder.py
import os
import random

# v9000 TRANSCENDENCE: FORENSIC DESTRUCTION
# Securely wipes files prevents recovery.

def secure_delete(filepath, passes=3):
    if not os.path.exists(filepath): return
    
    try:
        size = os.path.getsize(filepath)
        
        with open(filepath, "bw") as f:
            # Pass 1: Zeros
            f.seek(0)
            f.write(b'\x00' * size)
            f.flush()
            
            # Pass 2: Ones
            if passes > 1:
                f.seek(0)
                f.write(b'\xFF' * size)
                f.flush()
                
            # Pass 3: Random
            if passes > 2:
                f.seek(0)
                f.write(os.urandom(size))
                f.flush()
                
        os.remove(filepath)
        print(f"🗑️ [SHREDDER] Securely obliterated: {os.path.basename(filepath)}")
        
    except Exception as e:
        print(f"⚠️ [SHREDDER] Failed: {e}")
        # Fallback
        if os.path.exists(filepath): os.remove(filepath)
