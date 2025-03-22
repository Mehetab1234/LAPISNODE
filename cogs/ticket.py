import discord
from discord import app_commands
from discord.ext import commands

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ /ticketsetup command (Admin Only)
    @app_commands.command(name="ticketsetup", description="Setup a support ticket (Admin Only)")
    @app_commands.describe(title="Title of the ticket", description="Ticket details", image_url="Optional image URL")
    async def ticketsetup(self, interaction: discord.Interaction, title: str, description: str, image_url: str = None):
        # Check if user is an admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an admin to use this command!", ephemeral=True)
            return

        # Create embed message
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.avatar.url)
        if image_url:
            embed.set_image(url=image_url)

        await interaction.response.send_message(embed=embed)

# Cog setup
async def setup(bot):
    await bot.add_cog(Ticket(bot))
