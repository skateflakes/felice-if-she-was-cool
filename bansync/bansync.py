import discord
from redbot.core import commands
from redbot.core.commands.converter import RawUserIdConverter
from typing import Union

# whitelisted ids
ALLOWED_USER_IDS = {459697638124552192, 382555466968072202, 637695016143159326}

# blacklisted server (htf appeals server)
SKIPPED_GUILD_IDS = {1282000118962323538}

class BanSync(commands.Cog):
    """Ban a user from all servers the bot is in. Use this command carefully because once it's run on someone, it cannot be reversed."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def bansync(self, ctx: commands.Context, user: Union[discord.User, RawUserIdConverter], *, reason: str = "No reason provided."):
        """Ban a user from all servers the bot is in."""

        # permissions
        if not await self.bot.is_owner(ctx.author) and ctx.author.id not in ALLOWED_USER_IDS:
            await ctx.send("❌ You don't have permission to use this command.")
            return

        # prevent the user from self-banning
        if isinstance(user, discord.User) and user.id == ctx.author.id:
            await ctx.send("🚫 You can't ban yourself.")
            return

        # can't ban bots either
        if isinstance(user, discord.User) and user.bot:
            await ctx.send("🚫 You can't ban bots.")
            return

        # id lookup
        if isinstance(user, int):
            fetched_user = self.bot.get_user(user)
            if fetched_user and fetched_user.bot:
                await ctx.send("🚫 You can't ban bots.")
                return
            if user == ctx.author.id:
                await ctx.send("🚫 You can't ban yourself.")
                return
            user = fetched_user or discord.Object(id=user)

        reason += " (BanSync)"
        total = 0
        failed = []

        for guild in self.bot.guilds:
            if guild.id in SKIPPED_GUILD_IDS:
                continue
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
            message += f"\n❌ Failed in:\n" + "\n".join(failed)
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(BanSync(bot))
