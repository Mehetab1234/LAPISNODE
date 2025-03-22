import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import json
import os

SETTINGS_FILE = "ticket_settings.json"

# Default settings
DEFAULT_SETTINGS = {
    "panel_title": "🎟️ Support Tickets",
    "panel_description": "Click the button below to open a support ticket!",
    "button_label": "🎫 Create Ticket",
    "button_color": "green",
    "category_name": "Tickets",
    "close_delay": 5,
    "image_url": None,
    "allowed_roles": ["Admin", "Support"]
}

BUTTON_COLORS = {
    "blurple": discord.ButtonStyle.blurple,
    "green": discord.ButtonStyle.green,
    "red": discord.ButtonStyle.red,
    "grey": discord.ButtonStyle.grey
}

# Load settings from file
def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS

# Save settings to file
def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

TICKET_SETTINGS = load_settings()


class TicketView(discord.ui.View):
    """View for creating a ticket."""
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label=TICKET_SETTINGS["button_label"], style=BUTTON_COLORS[TICKET_SETTINGS["button_color"]], custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        user = interaction.user

        category = discord.utils.get(guild.categories, name=TICKET_SETTINGS["category_name"])
        if not category and TICKET_SETTINGS["category_name"]:
            category = await guild.create_category(TICKET_SETTINGS["category_name"])

        ticket_number = sum(1 for c in guild.channels if c.name.startswith("ticket-")) + 1
        ticket_name = f"ticket-{ticket_number:03}"

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),
        }
        for role_name in TICKET_SETTINGS["allowed_roles"]:
            role = discord.utils.get(guild.roles, name=role_name)
            if role:
                overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

        ticket_channel = await guild.create_text_channel(ticket_name, overwrites=overwrites, category=category)

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

        updated = False
        if panel_title:
            TICKET_SETTINGS["panel_title"] = panel_title
            updated = True
        if panel_description:
            TICKET_SETTINGS["panel_description"] = panel_description
            updated = True
        if button_label:
            TICKET_SETTINGS["button_label"] = button_label
            updated = True
        if button_color and button_color in BUTTON_COLORS:
            TICKET_SETTINGS["button_color"] = button_color
            updated = True
        if category_name:
            TICKET_SETTINGS["category_name"] = category_name
            updated = True
        if close_delay is not None:
            TICKET_SETTINGS["close_delay"] = max(1, close_delay)
            updated = True
        if image_url or image_url == "none":
            TICKET_SETTINGS["image_url"] = None if image_url.lower() == "none" else image_url
            updated = True

        if updated:
            save_settings(TICKET_SETTINGS)
            await interaction.response.send_message("✅ Ticket settings updated!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠ No changes were made.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Ticket(bot))
