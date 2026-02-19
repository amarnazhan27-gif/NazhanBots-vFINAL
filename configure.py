# termux_version/configure.py
import json
import os
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def wizard():
    console.print("[bold green]🧙 SUPERIOR SETUP WIZARD[/bold green]")
    console.print("Let's configure your server for GOD MODE.\n")
    
    config_path = os.path.join(os.path.dirname(__file__), 'config/config.json')
    
    # Load existing
    if os.path.exists(config_path):
        with open(config_path, 'r') as f: config = json.load(f)
    else:
        config = {}
        
    # 1. Telegram
    console.print("\n[yellow][1] Telegram Configuration[/yellow]")
    if Prompt.ask("Configure Telegram?", choices=["y", "n"], default="y") == "y":
        config["TELEGRAM_BOT_TOKEN"] = Prompt.ask("Enter Bot Token", default=config.get("TELEGRAM_BOT_TOKEN", ""))
        config["OWNER_ID"] = Prompt.ask("Enter Your Telegram ID (Number)", default=str(config.get("OWNER_ID", "0")))
        
    # 2. Discord
    console.print("\n[yellow][2] Discord Configuration[/yellow]")
    if Prompt.ask("Configure Discord?", choices=["y", "n"], default="y") == "y":
        config["DISCORD_BOT_TOKEN"] = Prompt.ask("Enter Discord Bot Token", default=config.get("DISCORD_BOT_TOKEN", ""))
        config["DISCORD_OWNER_ID"] = Prompt.ask("Enter Your Discord ID (Number)", default=str(config.get("DISCORD_OWNER_ID", "0")))

    # 3. Security
    console.print("\n[yellow][3] Security[/yellow]")
    config["WEB_PASSWORD"] = Prompt.ask("Set Admin Password", default=config.get("WEB_PASSWORD", "admin_god"))
    config["CF_API_KEY"] = Prompt.ask("Enter CapMonster/2Captcha Key (Optional)", default=config.get("CF_API_KEY", ""))

    # Save
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
        
    console.print("\n[bold green]✅ Configuration Saved![/bold green]")
    console.print("Run [bold cyan]bash guardian.sh[/bold cyan] to start the server.")

if __name__ == "__main__":
    try:
        wizard()
    except KeyboardInterrupt:
        console.print("\n[red]Wizard Cancelled.[/red]")
