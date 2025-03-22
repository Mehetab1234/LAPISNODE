import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class TicketView(discord.ui.View):
    """Button View to create a new ticket"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Generate a ticket channel name
        ticket_number = sum(1 for c in guild.channels if c.name.startswith("ticket-")) + 1
        ticket_name = f"ticket-{ticket_number:03}"

        # Check if the user already has a ticket
        existing_ticket = discord.utils.get(guild.channels, name=ticket_name)
        if existing_ticket:
            await interaction.response.send_message("❌ You already have an open ticket!", ephemeral=True)
            return

        # Create a new ticket channel with permissions
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Hide from others
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),  # Allow user
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),  # Allow bot
        }

        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites, category=None)
        await ticket_channel.send(f"🎟️ **{user.mention}, your ticket has been created!**\nAn admin will assist you shortly.")

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ /ticketsetup command (Admin Only)
    @app_commands.command(name="ticketsetup", description="Setup a ticket system (Admin Only)")
    @app_commands.describe(title="Title of the ticket panel", description="Panel details")
    async def ticketsetup(self, interaction: discord.Interaction, title: str, description: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an admin to use this command!", ephemeral=True)
            return

        # Create embed panel
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        embed.set_footer(text="Click the button below to create a ticket.")

        view = TicketView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Ticket system setup complete!", ephemeral=True)

# Cog setup
async def setup(bot):
    await bot.add_cog(Ticket(bot))
