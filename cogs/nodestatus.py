import os
import discord
from discord import app_commands
from discord.ext import commands
import requests

class NodeStatus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nodestatus", description="Check Pterodactyl node status")
    async def nodestatus(self, interaction: discord.Interaction):
        PTERO_API_KEY = os.getenv("PTERO_API_KEY")
        PTERO_PANEL_URL = os.getenv("PTERO_PANEL_URL")

        if not PTERO_API_KEY or not PTERO_PANEL_URL:
            await interaction.response.send_message("❌ API Key or Panel URL not set!", ephemeral=True)
            return

        headers = {"Authorization": f"Bearer {PTERO_API_KEY}", "Accept": "application/json"}

        try:
            response = requests.get(f"{PTERO_PANEL_URL}/api/application/nodes", headers=headers)
            response.raise_for_status()  # Raise error if request fails
            data = response.json()

            embed = discord.Embed(title="🖥️ Pterodactyl Node Status", color=discord.Color.blue())

            for node in data['data']:
                node_info = node['attributes']

                # Check if the node is reachable
                node_status = "✅ Online"
                ping_url = f"{PTERO_PANEL_URL}/api/application/nodes/{node_info['id']}"

                try:
                    ping_response = requests.get(ping_url, headers=headers, timeout=5)
                    if ping_response.status_code != 200:
                        node_status = "❌ Offline"
                except requests.exceptions.RequestException:
                    node_status = "❌ Offline"

                embed.add_field(
                    name=f"🔹 Node: {node_info['name']}",
                    value=(
                        f"👤 **Memory:** {node_info['memory']}MB\n"
                        f"💽 **Disk:** {node_info['disk']}MB\n"
                        f"🔌 **Status:** {node_status}"
                    ),
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(f"❌ Failed to fetch node status!\nError: `{e}`", ephemeral=True)

# Cog setup
async def setup(bot):
    await bot.add_cog(NodeStatus(bot))
