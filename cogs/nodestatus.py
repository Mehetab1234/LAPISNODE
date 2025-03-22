import os
import discord
from discord import app_commands
from discord.ext import commands
import requests

class NodeStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ /nodestatus command (Check Pterodactyl Node Status)
    @app_commands.command(name="nodestatus", description="Check Pterodactyl node status")
    async def nodestatus(self, interaction: discord.Interaction):
        PTERO_API_KEY = os.getenv("PTERO_API_KEY")
        PTERO_PANEL_URL = os.getenv("PTERO_PANEL_URL")

        if not PTERO_API_KEY or not PTERO_PANEL_URL:
            await interaction.response.send_message("❌ API Key or Panel URL not set in environment variables!", ephemeral=True)
            return

        headers = {"Authorization": f"Bearer {PTERO_API_KEY}", "Accept": "application/json"}
        response = requests.get(f"{PTERO_PANEL_URL}/api/application/nodes", headers=headers)

        if response.status_code == 200:
            data = response.json()
            embed = discord.Embed(title="🖥️ Pterodactyl Node Status", color=discord.Color.green())

            for node in data['data']:
                node_info = node['attributes']
                embed.add_field(
                    name=f"Node: {node_info['name']}",
                    value=f"👤 Memory: {node_info['memory']}MB\n💽 Disk: {node_info['disk']}MB\n🔌 Status: ✅ Online",
                    inline=False
                )

            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("❌ Failed to fetch node status!", ephemeral=True)

# Cog setup
async def setup(bot):
    await bot.add_cog(NodeStatus(bot))
