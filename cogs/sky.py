import os
import requests
import discord
from discord import app_commands
from discord.ext import commands

# Load API key and URL from environment variables
API_URL = os.getenv("SKYPORT_API_URL")
API_KEY = os.getenv("SKYPORT_API_KEY")

class Skyport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="nodestatus", description="Check Skyport node status")
    async def nodestatus(self, interaction: discord.Interaction):
        if not API_URL or not API_KEY:
            await interaction.response.send_message("❌ API Key or Panel URL not configured!", ephemeral=True)
            return

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        try:
            response = requests.get(f"{API_URL}/api/nodes", headers=headers)
            response.raise_for_status()  # Raise error if status code is 4xx or 5xx

            data = response.json()
            if not data:
                await interaction.response.send_message("❌ Skyport API returned an empty response.", ephemeral=True)
                return

            embed = discord.Embed(title="🌍 Skyport Node Status", color=discord.Color.blue())

            for node in data:
                embed.add_field(
                    name=f"🔹 Node: {node['name']}",
                    value=(
                        f"**ID:** {node['id']}\n"
                        f"**Memory:** {node['memory']} MB\n"
                        f"**CPU:** {node['cpu']}%\n"
                        f"**Disk:** {node['disk']} GB\n"
                        f"**Status:** ✅ Online" if node['status'] else "❌ Offline"
                    ),
                    inline=False
                )

            await interaction.response.send_message(embed=embed)

        except requests.exceptions.RequestException as e:
            await interaction.response.send_message(f"❌ API Error: {str(e)}", ephemeral=True)
        except requests.exceptions.JSONDecodeError:
            await interaction.response.send_message("❌ Skyport API response is not valid JSON.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Skyport(bot))
