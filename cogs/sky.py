import requests
import os
import discord
from discord import app_commands

API_KEY = os.getenv("SKYPORT_API_KEY")
PANEL_URL = os.getenv("SKYPORT_PANEL_URL")

class SkyportCommands(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="skyportnode", description="Check Skyport node status")
    async def skyportnode(self, interaction: discord.Interaction):
        await interaction.response.defer()  # Prevents interaction timeout

        headers = {"x-api-key": API_KEY}
        response = requests.get(f"{PANEL_URL}/api/nodes", headers=headers)

        print("Skyport API Response:", response.status_code, response.text)  # Debugging

        if response.status_code != 200:
            await interaction.followup.send("❌ Unable to reach Skyport API.", ephemeral=True)
            return

        try:
            nodes = response.json()
            message = "**Skyport Node Status:**\n"
            for node in nodes:
                message += f"**{node['name']}** - CPU: {node['cpu']}%, RAM: {node['ram']}%\n"
            await interaction.followup.send(message, ephemeral=True)
        except requests.exceptions.JSONDecodeError:
            await interaction.followup.send("❌ Skyport API returned an empty response.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(SkyportCommands(bot))
