import discord
from redbot.core import commands, Config
from discord.ext import tasks
import asyncio

LOCKED_CHANNEL_ID = 1199460134720651364
TARGET_ROLE_IDS = [1089214236472909914]  # Role to lock, plus @everyone
TRIGGER_COMMAND_ID = 947088344167366698
LOCK_DURATION_SECONDS = 120 * 60  # 120 minutes

class BumpLock(commands.Cog):
    """Automatically locks a channel after a bump command is used."""

    def __init__(self, bot):
        self.bot = bot
        self.locked_message_ids = {}

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type != discord.InteractionType.application_command:
            return

        if (
            interaction.channel
            and interaction.channel.id == LOCKED_CHANNEL_ID
            and interaction.data.get("id") == str(TRIGGER_COMMAND_ID)
        ):
            await self.handle_bump(interaction)

    async def handle_bump(self, interaction: discord.Interaction):
        channel = interaction.channel
        guild = interaction.guild

        overwrite_everyone = channel.overwrites_for(guild.default_role)
        overwrite_everyone.send_messages = False

        overwrites = {guild.default_role: overwrite_everyone}

        for role_id in TARGET_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrite = channel.overwrites_for(role)
                overwrite.send_messages = False
                overwrites[role] = overwrite

        await channel.edit(overwrites=overwrites)

        msg = await channel.send(f"Server has been bumped by {interaction.user.mention}! Check back later.")
        await msg.pin()
        self.locked_message_ids[channel.id] = msg.id

        await asyncio.sleep(LOCK_DURATION_SECONDS)

        # Restore permissions
        overwrite_everyone.send_messages = None
        overwrites = {guild.default_role: overwrite_everyone}
        for role_id in TARGET_ROLE_IDS:
            role = guild.get_role(role_id)
            if role:
                overwrite = channel.overwrites_for(role)
                overwrite.send_messages = None
                overwrites[role] = overwrite

        await channel.edit(overwrites=overwrites)

        # Delete the pinned message
        try:
            pinned = await channel.fetch_message(self.locked_message_ids.get(channel.id))
            await pinned.unpin()
            await pinned.delete()
        except Exception:
            pass

async def setup(bot):
    await bot.add_cog(BumpLock(bot))
