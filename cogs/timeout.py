import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

class Timeout(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="timeout", description="Temporarily mute a member")
    @app_commands.describe(member="The member to timeout", duration="Duration (e.g., 10s, 5m, 1h)", reason="Reason for timeout")
    async def timeout(self, interaction: discord.Interaction, member: discord.Member, duration: str, reason: str = "No reason provided"):
        # Check if user has admin permissions
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("❌ You must be an admin to use this command!", ephemeral=True)
            return

        # Convert duration to seconds
        time_units = {"s": 1, "m": 60, "h": 3600}
        try:
            unit = duration[-1]
            if unit not in time_units:
                raise ValueError
            time_amount = int(duration[:-1])
            timeout_seconds = time_amount * time_units[unit]
        except ValueError:
            await interaction.response.send_message("❌ Invalid duration! Use `10s`, `5m`, or `1h`.", ephemeral=True)
            return

        # Apply timeout (Discord's timeout feature)
        try:
            await member.timeout(timedelta(seconds=timeout_seconds), reason=reason)
            await interaction.response.send_message(f"✅ {member.mention} has been timed out for {duration}!\n**Reason:** {reason}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ I don't have permission to timeout this member!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Failed to timeout the member!\nError: `{e}`", ephemeral=True)

# Cog setup
async def setup(bot):
    await bot.add_cog(Timeout(bot))
