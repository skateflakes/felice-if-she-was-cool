import discord
from redbot.core import commands
from typing import Union
from redbot.core.commands.converter import RawUserIdConverter

class BanSync(commands.Cog):
    """Cog for synchronizing bans across all servers."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    @commands.bot_has_permissions(ban_members=True)
    async def bansync(self, ctx, user: Union[discord.User, RawUserIdConverter], *, reason: str = "No reason provided."):
        """
        Ban a user from all servers the bot is in.
        The reason will be appended with (BanSync).
        """
        reason += " (BanSync)"
        total = 0
        failed = []

        if isinstance(user, int):
            user = self.bot.get_user(user) or discord.Object(id=user)

        for guild in self.bot.guilds:
            if not guild.me.guild_permissions.ban_members:
                failed.append(f"{guild.name} (no permission)")
                continue
            try:
                await guild.ban(user, reason=reason)
                total += 1
            except discord.Forbidden:
                failed.append(f"{guild.name} (forbidden)")
            except Exception as e:
                failed.append(f"{guild.name} ({type(e).__name__})")

        message = f"✅ Banned `{user}` from {total} servers."
        if failed:
            message += "\n❌ Failed in:\n" + "\n".join(failed)
        await ctx.send(message)
