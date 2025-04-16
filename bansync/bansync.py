import discord
from redbot.core import commands
from redbot.core.commands.converter import RawUserIdConverter
from typing import Union

# ids
ALLOWED_USER_IDS = {1}  # no one is whitelisted (yet)

class BanSync(commands.Cog):
    """Ban a user from all servers the bot is in."""

    def __init__(self, bot):
        self.bot = bot

    def is_authorized(self, ctx: commands.Context) -> bool:
        return ctx.author.id in ALLOWED_USER_IDS or ctx.bot.is_owner(ctx.author)

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def bansync(self, ctx: commands.Context, user: Union[discord.User, RawUserIdConverter], *, reason: str = "No reason provided."):
        """
        Ban a user from all servers the bot is in.
        Appends (BanSync) to the reason.
        """
        # 🔐 Permission check
        if not await self.bot.is_owner(ctx.author) and ctx.author.id not in ALLOWED_USER_IDS:
            await ctx.send("❌ You don't have permission to use this command.")
            return

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

async def setup(bot):
    await bot.add_cog(BanSync(bot))
