import discord
from discord import app_commands
from discord.ext import commands
import asyncio

# Default settings (Can be changed via command)
TICKET_SETTINGS = {
    "panel_title": "🎟️ Support Tickets",
    "panel_description": "Click the button below to open a support ticket!",
    "button_label": "🎫 Create Ticket",
    "button_color": "green",
    "category_name": "Tickets",
    "close_delay": 5,
    "image_url": None,  # Set None to disable image
    "allowed_roles": ["Admin", "Support"]
}

# Convert string to ButtonStyle
BUTTON_COLORS = {
    "blurple": discord.ButtonStyle.blurple,
    "green": discord.ButtonStyle.green,
    "red": discord.ButtonStyle.red,
    "grey": discord.ButtonStyle.grey
}

class TicketView(discord.ui.View):
    """View for creating a ticket."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=TICKET_SETTINGS["button_label"], style=BUTTON_COLORS[TICKET_SETTINGS["button_color"]], custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        # Check or create category
        category = discord.utils.get(guild.categories, name=TICKET_SETTINGS["category_name"])
        if not category and TICKET_SETTINGS["category_name"]:
            category = await guild.create_category(TICKET_SETTINGS["category_name"])

        # Generate unique ticket name
        ticket_number = sum(1 for c in guild.channels if c.name.startswith("ticket-")) + 1
        ticket_name = f"ticket-{ticket_number:03}"

        # Set permissions (user + allowed roles)
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        for role_name in TICKET_SETTINGS["allowed_roles"]:
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
        if TICKET_SETTINGS["image_url"]:
            embed.set_image(url=TICKET_SETTINGS["image_url"])

        view = CloseTicketView()
        await ticket_channel.send(embed=embed, view=view)

        await interaction.response.send_message(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)


class CloseTicketView(discord.ui.View):
    """View with a button to close the ticket."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"⏳ Closing ticket in {TICKET_SETTINGS['close_delay']} seconds...", ephemeral=True)
        await asyncio.sleep(TICKET_SETTINGS["close_delay"])
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

        embed = discord.Embed(title=TICKET_SETTINGS["panel_title"], description=TICKET_SETTINGS["panel_description"], color=discord.Color.blue())
        if TICKET_SETTINGS["image_url"]:
            embed.set_image(url=TICKET_SETTINGS["image_url"])

        view = TicketView()
        await interaction.channel.send(embed=embed, view=view)
        await interaction.response.send_message("✅ Ticket system set up!", ephemeral=True)

    @app_commands.command(name="ticketconfig", description="Customize the ticket panel")
    @app_commands.describe(
        panel_title="Set a custom title for the ticket panel",
        panel_description="Set a custom description",
        button_label="Set the button text",
        button_color="Choose color: blurple, green, red, grey",
        category_name="Set the category for tickets",
        close_delay="Set delay before ticket closes (seconds)",
        image_url="Set an optional image URL"
    )
    async def ticketconfig(self, interaction: discord.Interaction,
                           panel_title: str = None,
                           panel_description: str = None,
                           button_label: str = None,
                           button_color: str = None,
                           category_name: str = None,
                           close_delay: int = None,
                           image_url: str = None):
        """Command to update ticket panel settings."""
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an admin to use this command!", ephemeral=True)
            return

        if panel_title:
            TICKET_SETTINGS["panel_title"] = panel_title
        if panel_description:
            TICKET_SETTINGS["panel_description"] = panel_description
        if button_label:
            TICKET_SETTINGS["button_label"] = button_label
        if button_color and button_color in BUTTON_COLORS:
            TICKET_SETTINGS["button_color"] = button_color
        if category_name:
            TICKET_SETTINGS["category_name"] = category_name
        if close_delay is not None:
            TICKET_SETTINGS["close_delay"] = max(1, close_delay)  # Prevents negative values
        if image_url:
            TICKET_SETTINGS["image_url"] = image_url

        await interaction.response.send_message("✅ Ticket settings updated!", ephemeral=True)


# Cog setup
async def setup(bot):
    await bot.add_cog(Ticket(bot))
