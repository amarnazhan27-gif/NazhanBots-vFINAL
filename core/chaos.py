# termux_version/core/chaos.py
import random
import time
import asyncio

# v28000: CHAOS ENGINEERING (Human Simulation)
# To bypass AI WAFs, we must behave like a flawed human, not a perfect machine.

def get_chaos_delay(base_delay):
    """
    Returns a deeper, more human-like delay.
    Sometimes humans get distracted (long pause).
    Sometimes humans act fast (short pause).
    """
    chance = random.random()
    
    # 5% chance of "distraction" (user checks notification)
    if chance < 0.05:
        print("🧘 [CHAOS] User distracted... pausing.")
        return base_delay + random.uniform(5.0, 12.0)
        
    # 10% chance of "rage mode" (fast clicks)
    if chance < 0.15:
        return base_delay * 0.1
        
    # Normal variance
    return base_delay * random.uniform(0.8, 1.5)

def inject_typo(text):
    """
    Simulates fat-finger typos in non-critical fields (like names).
    Not to be used on phone numbers!
    """
    if len(text) < 4: return text
    
    if random.random() > 0.1: return text # 90% accuracy
    
    # Swap two chars
    idx = random.randint(0, len(text)-2)
    chars = list(text)
    chars[idx], chars[idx+1] = chars[idx+1], chars[idx]
    return "".join(chars)

def should_misclick():
    """
    1% chance to 'miss' the button (send request to wrong endpoint then cancel).
    Used to generate noise that confuses behavioral analysis.
    """
    return random.random() < 0.01
