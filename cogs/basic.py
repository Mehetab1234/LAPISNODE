import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import datetime
import pytz

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reminders = {}  # Store reminders
    
    # 1️⃣ Ban Command
    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "No reason provided"):
        """Ban a user from the server."""
        await user.ban(reason=reason)
        await interaction.response.send_message(f"✅ **{user.name}** has been banned! Reason: {reason}")

    # 2️⃣ Time Reminder
    @app_commands.command(name="remind", description="Set a reminder.")
    async def remind(self, interaction: discord.Interaction, minutes: int, message: str):
        """Set a reminder that sends a message after a certain time."""
        await interaction.response.send_message(f"⏳ Reminder set for {minutes} minutes: {message}")
        await asyncio.sleep(minutes * 60)
        await interaction.followup.send(f"⏰ **Reminder:** {message} - Time's up!")

    # 3️⃣ Timer
    @app_commands.command(name="timer", description="Start a countdown timer.")
    async def timer(self, interaction: discord.Interaction, seconds: int):
        """Start a countdown timer."""
        await interaction.response.send_message(f"⏳ Timer started for {seconds} seconds.")
        await asyncio.sleep(seconds)
        await interaction.followup.send("⏰ Time's up!")

    # 4️⃣ Time Difference
    @app_commands.command(name="timediff", description="Calculate the time difference between two times.")
    async def timediff(self, interaction: discord.Interaction, time1: str, time2: str):
        """Finds the difference between two given times (format: HH:MM)."""
        try:
            t1 = datetime.datetime.strptime(time1, "%H:%M")
            t2 = datetime.datetime.strptime(time2, "%H:%M")
            diff = abs(t2 - t1)
            await interaction.response.send_message(f"⏳ Time difference: **{diff}**")
        except ValueError:
            await interaction.response.send_message("❌ Invalid time format! Use `HH:MM` (24-hour format).", ephemeral=True)

    # 5️⃣ World Clock
    @app_commands.command(name="worldclock", description="Get the current time in any city.")
    async def worldclock(self, interaction: discord.Interaction, city: str):
        """Shows the current time in a given city using pytz."""
        try:
            timezone = pytz.timezone(city)
            current_time = datetime.datetime.now(timezone).strftime("%Y-%m-%d %H:%M:%S")
            await interaction.response.send_message(f"🕰️ Current time in **{city}**: {current_time}")
        except pytz.UnknownTimeZoneError:
            await interaction.response.send_message("❌ Invalid city or timezone!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Basic(bot))
