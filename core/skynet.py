# termux_version/core/skynet.py
import threading
import time
import random
import os
from .hunter import search_new_apis
from .cleaner import self_clean

# v25000: SKYNET (Autonomous Life Cycle)
# The system manages itself.
# 1. HUNTS for new targets.
# 2. CLEANS its own mess.
# 3. EVOLVES strategies.

RUNNING = True

def life_cycle_loop():
    print("🌌 [SKYNET] Online. Autonomous Phase Initiated.")
    while RUNNING:
        try:
            # Phase 1: Hunt (Every 1 hour)
            if random.random() < 0.05: # 5% chance every loop
                print("🌌 [SKYNET] Phase: HUNT")
                search_new_apis()

            # Phase 2: Hygiene (Every 10 mins)
            if random.random() < 0.1:
                print("🌌 [SKYNET] Phase: HYGIENE")
                self_clean()
                
            # Phase 4 (v27000): OMEGA Optimization (Rare)
            if random.random() < 0.02:
                from .optimizer import run_optimizer
                run_optimizer()
                
            # Phase 5 (vFINALITY): The Grim Reaper (Rare - 1% chance)
            if random.random() < 0.01:
                try:
                    from .validator import cleanup_dead_apis
                    cleanup_dead_apis()
                except: pass
                
            # Phase 3: Sleep to save battery
            time.sleep(60) 
            
        except Exception as e:
            print(f"🌌 [SKYNET] Glitch: {e}")
            time.sleep(10)

def activate_skynet():
    t = threading.Thread(target=life_cycle_loop)
    t.daemon = True
    t.start()
