import discord
from discord import app_commands
from discord.ext import commands
import asyncio

class TicketView(discord.ui.View):
    """Button to create a new ticket"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 Create Ticket", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Generate a unique ticket channel name
        ticket_number = sum(1 for c in guild.channels if c.name.startswith("ticket-")) + 1
        ticket_name = f"ticket-{ticket_number:03}"

        # Check if user already has a ticket
        existing_ticket = discord.utils.get(guild.channels, name=ticket_name)
        if existing_ticket:
            await interaction.response.send_message("❌ You already have an open ticket!", ephemeral=True)
            return

        # Set channel permissions (private to user & admins)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }

        # Create ticket channel
        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites, category=None)

        # Send a message inside the ticket with a close button
        embed = discord.Embed(title="🎟️ Ticket Opened", description=f"{user.mention}, an admin will assist you soon.", color=discord.Color.green())
        view = CloseTicketView()
        await ticket_channel.send(embed=embed, view=view)

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    """Support will be with you shortly.
To close this press the close button"""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⏳ Closing ticket in 5 seconds...", ephemeral=True)
        await asyncio.sleep(5)  # Delay before deletion
        await interaction.channel.delete()

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ /ticketsetup command (Admin Only, With Optional Image)
    @app_commands.command(name="ticketsetup", description="Setup a ticket system (Admin Only)")
    @app_commands.describe(title="Title of the ticket panel", description="Panel details", image_url="Optional image URL")
    async def ticketsetup(self, interaction: discord.Interaction, title: str, description: str, image_url: str = None):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an admin to use this command!", ephemeral=True)
            return

        # Create embed panel
        embed = discord.Embed(title=title, description=description, color=discord.Color.blue())
        embed.set_footer(text="Click the button below to create a ticket.")

        # Add image if provided
        if image_url:
            embed.set_image(url=image_url)

        view = TicketView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Ticket system setup complete!", ephemeral=True)

# Cog setup
async def setup(bot):
    await bot.add_cog(Ticket(bot))
