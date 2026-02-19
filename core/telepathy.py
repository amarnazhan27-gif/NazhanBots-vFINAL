# termux_version/core/telepathy.py
import json
import os
import requests

# v26000: TELEPATHY (Swarm Intelligence)
# Allows bots to share intelligence via Telegram Group.
# Bot A sends: [HIVE_SIGNAL] FOUND: {"url": "..."}
# Bot B receives, parses, and adds to local config.

def broadcast_discovery(bot, chat_id, api_data):
    """
    Broadcasts a new API discovery to the Swarm (Telegram Group).
    """
    try:
        # Minimal payload to avoid ban
        payload = {
            "u": api_data.get("url"),
            "m": api_data.get("method"),
            "d": api_data.get("data")
        }
        msg = f"📡 [SWARM_SIGNAL] {json.dumps(payload)}"
        bot.send_message(chat_id, msg)
    except: pass

def process_swarm_signal(text):
    """
    Parses a swarm signal and updates local intelligence.
    Returns: (bool) Is New Discovery?
    """
    if "SWARM_SIGNAL" not in text: return False
    
    try:
        json_part = text.split("[SWARM_SIGNAL]")[1].strip()
        data = json.loads(json_part)
        
        # Reconstruct API object
        new_api = {
            "name": f"Swarm-{os.urandom(2).hex()}",
            "url": data.get("u"),
            "method": data.get("m"),
            "data": data.get("d"),
            "provider": "swarm"
        }
        
        # Current APIs
        path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
        current_apis = []
        if os.path.exists(path):
            with open(path, 'r') as f: current_apis = json.load(f)
            
        # Check duplicate
        for api in current_apis:
            if api.get("url") == new_api["url"]:
                return False # Already knew it
                
        # Add new
        current_apis.append(new_api)
        with open(path, 'w') as f:
            json.dump(current_apis, f, indent=2)
            
        return True
    except:
        return False

def broadcast_via_http(api_data):
    """
    Sends Swarm Signal via direct HTTP to Telegram (Bypassing Bot Object).
    Used by Brain/Hunter threads.
    """
    try:
        config_path = os.path.join(os.path.dirname(__file__), '../config/config.json')
        with open(config_path, 'r') as f: config = json.load(f)
        
        token = config.get("TELEGRAM_BOT_TOKEN")
        chat_id = config.get("TELEGRAM_CHAT_ID")
        
        if not token or not chat_id: return
        
        payload = {
            "u": api_data.get("url"),
            "m": api_data.get("method"),
            "d": api_data.get("data")
        }
        msg = f"📡 [SWARM_SIGNAL] {json.dumps(payload)}"
        
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg})
    except: pass
