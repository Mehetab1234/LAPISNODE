import discord
from discord.ext import commands
import aiohttp
import os

SKYPORT_API_KEY = os.getenv("SKYPORT_API_KEY")
PANEL_URL = os.getenv("PANEL_URL")

class Skyport(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="nodestatus")
    async def nodestatus(self, ctx):
        if not SKYPORT_API_KEY or not PANEL_URL:
            await ctx.send("❌ API Key or Panel URL not configured!")
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{PANEL_URL}/api/nodes", headers={"Authorization": f"Bearer {SKYPORT_API_KEY}"}) as response:
                if response.status != 200:
                    await ctx.send("❌ Skyport API returned an error!")
                    return
                data = await response.json()
        
        if not data:
            await ctx.send("❌ Skyport API returned an empty response.")
            return

        embed = discord.Embed(title="Skyport Node Status", color=discord.Color.blue())
        for node in data:
            embed.add_field(name=node["name"], value=f"Status: {node['status']}", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Skyport(bot))
