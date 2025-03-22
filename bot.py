import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive  # Import keep_alive script

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

# Set up bot
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Load cogs
COGS = ["cogs.ticket", "cogs.nodestatus"]

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    for cog in COGS:
        await bot.load_extension(cog)
    print("✅ All cogs loaded!")

# Keep the bot alive
keep_alive()

# Run bot
bot.run(TOKEN)
