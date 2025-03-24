import discord
from discord import app_commands
from discord.ext import commands
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
API_KEY = os.getenv("SKYPORT_API_KEY")
PANEL_URL = os.getenv("SKYPORT_PANEL_URL")

class SkyportNode(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="skyportnode", description="Check the status of a specific Skyport node by ID")
    async def skyportnode(self, interaction: discord.Interaction, node_id: int):
        """Slash command to check a Skyport node's status by its ID."""
        if not API_KEY or not PANEL_URL:
            await interaction.response.send_message("❌ API Key or Panel URL not configured!", ephemeral=True)
            return

        url = f"{PANEL_URL}/api/nodes/{node_id}"
        headers = {"x-api-key": API_KEY}

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                embed = discord.Embed(title=f"🌐 Skyport Node {node_id} Status", color=discord.Color.blue())
                embed.add_field(name="🖥️ CPU Usage", value=f"{data.get('cpu_usage', 'N/A')}%", inline=True)
                embed.add_field(name="📝 RAM Usage", value=f"{data.get('ram_usage', 'N/A')}%", inline=True)
                embed.add_field(name="💾 Total RAM", value=f"{data.get('total_ram', 'N/A')} MB", inline=True)
                embed.add_field(name="📂 Disk Usage", value=f"{data.get('disk_usage', 'N/A')}%", inline=True)
                embed.add_field(name="⏳ Uptime", value=data.get('uptime', 'N/A'), inline=False)
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"⚠️ Node {node_id} returned status: {response.status_code}", ephemeral=True)
        except requests.exceptions.RequestException:
            await interaction.response.send_message(f"❌ Node {node_id} is offline or unreachable.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SkyportNode(bot))
