import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # Keep the bot alive
import asyncio

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load cogs
COGS = ["cogs.ticket", "cogs.nodestatus", "cogs.timeout"]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

    # Load cogs
    for cog in COGS:
        await bot.load_extension(cog)
        print(f"✅ Loaded {cog}")

    # Sync commands
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} commands globally.")
    except Exception as e:
        print(f"❌ Command sync failed: {e}")

# Keep the bot alive (for Replit/Render)
keep_alive()

# Run bot
bot.run(TOKEN)
