import os
import requests
import discord
from discord import app_commands
from discord.ext import commands

# Load environment variables
SKYPORT_API_URL = os.getenv("SKYPORT_API_URL")
SKYPORT_API_KEY = os.getenv("SKYPORT_API_KEY")

class Skyport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="skyportnode", description="Check Skyport node status")
    async def skyportnode(self, interaction: discord.Interaction):
        if not SKYPORT_API_URL or not SKYPORT_API_KEY:
            await interaction.response.send_message("❌ API Key or Panel URL not configured!", ephemeral=True)
            return
        
        headers = {
            "Authorization": f"Bearer {SKYPORT_API_KEY}",
            "Content-Type": "application/json",
        }

        try:
            response = requests.get(f"{SKYPORT_API_URL}/admin/nodes", headers=headers)

            if response.status_code == 200:
                data = response.json()
                if not data:
                    await interaction.response.send_message("❌ Skyport API returned an empty response.", ephemeral=True)
                    return

                embed = discord.Embed(title="Skyport Node Status", color=discord.Color.blue())
                for node in data:
                    embed.add_field(
                        name=f"Node: {node['name']}",
                        value=f"**Status:** {node['status']}\n"
                              f"**CPU:** {node['cpu_usage']}%\n"
                              f"**RAM:** {node['memory_usage']} MB",
                        inline=False
                    )

                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(f"❌ Skyport API Error: {response.status_code}\n{response.text}", ephemeral=True)

        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(f"❌ NOT WORKING: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Skyport(bot))
