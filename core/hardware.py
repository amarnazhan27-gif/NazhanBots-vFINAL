# termux_version/core/hardware.py
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    
import os
import time

# v5000 ETERNITY: Hardware Preservation Protocol
# Prevents device death by monitoring thermals and battery.

BATTERY_THRESHOLD_PAUSE = 20
BATTERY_THRESHOLD_KILL = 5
TEMP_THRESHOLD = 80 # Celsius (approx)

def get_battery_status():
    if not PSUTIL_AVAILABLE:
        return 100, True # Mock
        
    if not hasattr(psutil, "sensors_battery"):
        return 100, False 
        
    try:
        battery = psutil.sensors_battery()
        if battery:
            return battery.percent, battery.power_plugged
    except Exception:
        pass # Permission denied on some Android devices
    return 100, True

def is_safe_to_attack():
    # 1. Battery Check
    percent, plugged = get_battery_status()
    
    # Check even if plugged (heat issue) or just strict mode
    if percent <= BATTERY_THRESHOLD_KILL:
        print(f"🪫 [HARDWARE] CRITICAL BATTERY ({percent}%). SAVING SYSTEM...")
        # v31000: Alert Owner
        alert_battery_critical(percent)
        
        with open("shutdown.reason", "w") as f: f.write("BATTERY_CRITICAL")
        os._exit(0)
        
    if not plugged and percent <= BATTERY_THRESHOLD_PAUSE:
        print(f"🔋 [HARDWARE] Low Battery ({percent}%). Pausing Attacks.")
        return False
            
    # 2. Temperature Check
    return True

# v23000: ADAPTIVE CONCURRENCY
def get_adaptive_concurrency(default=50):
    if not PSUTIL_AVAILABLE: return default

    try:
        # CPU Load (Last 1 sec)
        cpu_load = psutil.cpu_percent(interval=0.1)
        
        # RAM Usage
        mem = psutil.virtual_memory()
        ram_usage = mem.percent
        
        # Critical Throttling
        if cpu_load > 90 or ram_usage > 90:
            print(f"🔥 [SENTINEL] CPU {cpu_load}% / RAM {ram_usage}%. Throttling to 5 threads.")
            return 5
            
        # Heavy Load
        if cpu_load > 70 or ram_usage > 80:
            print(f"⚠️ [SENTINEL] High Load. Reducing threads.")
            return max(10, default // 2)
            
        # Normal
        return default
    except:
        return default

# v31000: DIRECT ALERT
def alert_battery_critical(percent):
    try:
        import json
        import requests
        config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
        with open(config_path, 'r') as f: config = json.load(f)
        
        token = config.get("TELEGRAM_BOT_TOKEN")
        chat_id = config.get("TELEGRAM_CHAT_ID")
        
        msg = f"🪫 **CRITICAL ALERT**: Battery at {percent}%. Initiating Emergency Shutdown."
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
    except: pass
