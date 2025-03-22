import discord
from discord import app_commands
from discord.ext import commands
import asyncio

# Customizable settings
TICKET_PANEL_TITLE = "🎟️ Support Tickets"
TICKET_PANEL_DESCRIPTION = "Click the button below to open a support ticket!"
TICKET_BUTTON_LABEL = "🎫 Create Ticket"
TICKET_BUTTON_COLOR = discord.ButtonStyle.green
TICKET_CATEGORY_NAME = "Tickets"  # Set to None to create tickets outside any category
TICKET_CLOSE_DELAY = 5  # Seconds before deleting the ticket
TICKET_IMAGE_URL = "https://your-image-url.png"  # Optional image for embed (set None to disable)
ALLOWED_ROLES = ["Support", "Admin"]  # Roles that can view all tickets


class TicketView(discord.ui.View):
    """View with a button to create a ticket."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=TICKET_BUTTON_LABEL, style=TICKET_BUTTON_COLOR, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Check or create category
        category = discord.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
        if not category and TICKET_CATEGORY_NAME:
            category = await guild.create_category(TICKET_CATEGORY_NAME)

        # Generate unique ticket name
        ticket_number = sum(1 for c in guild.channels if c.name.startswith("ticket-")) + 1
        ticket_name = f"ticket-{ticket_number:03}"

        # Set permissions (user + allowed roles)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        for role_name in ALLOWED_ROLES:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        # Create ticket channel
        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites, category=category)

        # Ticket embed
        embed = discord.Embed(
            title="🎟️ Ticket Opened",
            description=f"{user.mention}, **Support will be with you shortly.**\nTo close this, press the close button.",
            color=discord.Color.green()
        )
        if TICKET_IMAGE_URL:
            embed.set_image(url=TICKET_IMAGE_URL)

        view = CloseTicketView()
        await ticket_channel.send(embed=embed, view=view)

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    """View with a button to close the ticket."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"⏳ Closing ticket in {TICKET_CLOSE_DELAY} seconds...", ephemeral=True)
        await asyncio.sleep(TICKET_CLOSE_DELAY)
        await interaction.channel.delete()


class Ticket(commands.Cog):
    """Ticket Cog with a setup command."""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticketsetup", description="Set up the ticket system")
    async def ticketsetup(self, interaction: discord.Interaction):
        """Command to create the ticket panel."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an admin to use this command!", ephemeral=True)
            return

        embed = discord.Embed(title=TICKET_PANEL_TITLE, description=TICKET_PANEL_DESCRIPTION, color=discord.Color.blue())
        if TICKET_IMAGE_URL:
            embed.set_image(url=TICKET_IMAGE_URL)

        view = TicketView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Ticket system set up!", ephemeral=True)


# Cog setup
async def setup(bot):
    await bot.add_cog(Ticket(bot))
