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

    @app_commands.command(name="skyportnode", description="Check the status of all Skyport nodes")
    async def skyportnode(self, interaction: discord.Interaction):
        """Slash command to check the status of all Skyport nodes."""
        if not API_KEY or not PANEL_URL:
            await interaction.response.send_message("❌ API Key or Panel URL not configured!", ephemeral=True)
            return

        url = f"{PANEL_URL}/api/nodes"
        headers = {"x-api-key": API_KEY}

        try:
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                nodes = response.json()
                if not nodes:
                    await interaction.response.send_message("⚠️ No nodes found!", ephemeral=True)
                    return

                embed = discord.Embed(title="🌐 Skyport Nodes Status", color=discord.Color.blue())
                
                for node in nodes:
                    embed.add_field(
                        name=f"🖥️ Node {node.get('id', 'Unknown')}",
                        value=(
                            f"**CPU Usage:** {node.get('cpu_usage', 'N/A')}%\n"
                            f"**RAM Usage:** {node.get('ram_usage', 'N/A')}%\n"
                            f"**Total RAM:** {node.get('total_ram', 'N/A')} MB\n"
                            f"**Disk Usage:** {node.get('disk_usage', 'N/A')}%\n"
                            f"**⏳ Uptime:** {node.get('uptime', 'N/A')}"
                        ),
                        inline=False
                    )

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"⚠️ Failed to fetch nodes. Status: {response.status_code}", ephemeral=True)
        except requests.exceptions.RequestException:
            await interaction.response.send_message("❌ Unable to reach Skyport API.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SkyportNode(bot))
