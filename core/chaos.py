# termux_version/core/chaos.py
import random
import time
import asyncio

# v28000: CHAOS ENGINEERING (Human Simulation)
# To bypass AI WAFs, we must behave like a flawed human, not a perfect machine.

def get_chaos_delay(base_delay):
    """
    Returns a fast, aggressive delay.
    No more distractions. Pure speed.
    """
    # v1000000: AGGRESSIVE MODE
    return base_delay * 0.1 # Reduced by 90%

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
