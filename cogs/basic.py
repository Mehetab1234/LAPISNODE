import discord
from discord import app_commands
from discord.ext import commands, tasks
import pytz
from datetime import datetime, timedelta
import asyncio

class Basic(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 🌎 World Clock Command
    @app_commands.command(name="worldclock", description="Get the current time in a specified timezone.")
    async def worldclock(self, interaction: discord.Interaction, timezone: str):
        try:
            tz = pytz.timezone(timezone)
            current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")
            await interaction.response.send_message(f"🕰️ Current time in `{timezone}`: `{current_time}`", ephemeral=True)
        except pytz.UnknownTimeZoneError:
            available_zones = ", ".join(pytz.all_timezones[:10])
            await interaction.response.send_message(
                f"❌ Invalid timezone!\n**Example valid timezones:** `{available_zones}`\n\nUse `/timezones` to see all.",
                ephemeral=True
            )

    # 🌍 List of Available Timezones
    @app_commands.command(name="timezones", description="Get a list of valid timezones.")
    async def timezones(self, interaction: discord.Interaction):
        zones = ", ".join(pytz.all_timezones[:20])
        await interaction.response.send_message(f"✅ **Valid Timezones:**\n`{zones}`\nCheck all [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)", ephemeral=True)

    # ⏳ Time Difference Command
    @app_commands.command(name="timediff", description="Calculate the time difference between two dates (YYYY-MM-DD).")
    async def timediff(self, interaction: discord.Interaction, date1: str, date2: str):
        try:
            d1 = datetime.strptime(date1, "%Y-%m-%d")
            d2 = datetime.strptime(date2, "%Y-%m-%d")
            diff = abs((d2 - d1).days)
            await interaction.response.send_message(f"📆 The difference between `{date1}` and `{date2}` is `{diff} days`.", ephemeral=True)
        except ValueError:
            await interaction.response.send_message("❌ Invalid date format! Use `YYYY-MM-DD`.", ephemeral=True)

    # ⏰ Timer Command
    @app_commands.command(name="timer", description="Set a countdown timer in seconds.")
    async def timer(self, interaction: discord.Interaction, seconds: int):
        if seconds <= 0:
            await interaction.response.send_message("❌ Time must be greater than 0 seconds.", ephemeral=True)
            return
        
        await interaction.response.send_message(f"⏳ Timer started for `{seconds}` seconds.", ephemeral=True)
        await asyncio.sleep(seconds)
        await interaction.followup.send(f"⏰ Time's up! `{seconds}` seconds have passed.", ephemeral=True)

    # ⏳ Reminder Command
    @app_commands.command(name="remindme", description="Set a reminder (time in minutes).")
    async def remindme(self, interaction: discord.Interaction, minutes: int, *, message: str):
        if minutes <= 0:
            await interaction.response.send_message("❌ Time must be greater than 0 minutes.", ephemeral=True)
            return

        await interaction.response.send_message(f"⏳ Reminder set for `{minutes}` minutes: `{message}`.", ephemeral=True)
        await asyncio.sleep(minutes * 60)
        await interaction.followup.send(f"🔔 Reminder: `{message}`", ephemeral=True)

    # 🚫 Ban Command (Requires Admin Permission)
    @app_commands.command(name="ban", description="Ban a user from the server.")
    @app_commands.default_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if interaction.user.guild_permissions.ban_members:
            await member.ban(reason=reason)
            await interaction.response.send_message(f"🚨 `{member}` has been banned! Reason: `{reason}`")
        else:
            await interaction.response.send_message("❌ You don't have permission to use this command.", ephemeral=True)

# ✅ Setup function
async def setup(bot):
    await bot.add_cog(Basic(bot))
