import discord
from redbot.core import commands
from redbot.core.commands.converter import RawUserIdConverter
from typing import Union

# Whitelisted users
ALLOWED_USER_IDS = {
    459697638124552192,  # cosmo
    382555466968072202,  # klover
    637695016143159326,  # hazel
    1109842206287745194, # vern/soapster
    813536022717136916   # clouded/elvy
}

# Guilds to skip
SKIPPED_GUILD_IDS = {1282000118962323538}


class BanSync(commands.Cog):
    """Ban or unban a user across all servers the bot is in."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def bansync(self, ctx: commands.Context, user: Union[discord.User, RawUserIdConverter], *, reason: str = "No reason provided."):
        """Ban a user from all servers the bot is in."""

        # permission check
        if not await self.bot.is_owner(ctx.author) and ctx.author.id not in ALLOWED_USER_IDS:
            await ctx.send("❌ You don't have permission to use this command.")
            return

        # Prevent banning self
        if isinstance(user, discord.User):
            if user.id == ctx.author.id:
                await ctx.send("🚫 You can't ban yourself.")
                return
            if user.bot:
                await ctx.send("🚫 You can't ban bots.")
                return

        # If raw ID, fetch user object if possible
        if isinstance(user, int):
            fetched_user = await self.bot.fetch_user(user)
            if fetched_user:
                if fetched_user.bot:
                    await ctx.send("🚫 You can't ban bots.")
                    return
                if fetched_user.id == ctx.author.id:
                    await ctx.send("🚫 You can't ban yourself.")
                    return
                user = fetched_user
            else:
                user = discord.Object(id=user)

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

    @commands.command()
    @commands.bot_has_permissions(ban_members=True)
    async def unbansync(self, ctx: commands.Context, user: Union[discord.User, RawUserIdConverter]):
        """Unban a user from all servers they were banned with BanSync."""

        if not await self.bot.is_owner(ctx.author) and ctx.author.id not in ALLOWED_USER_IDS:
            await ctx.send("❌ You don't have permission to use this command.")
            return

        user_id = user.id if isinstance(user, discord.User) else int(user)

        total = 0
        failed = []

        for guild in self.bot.guilds:
            if guild.id in SKIPPED_GUILD_IDS:
                continue
            if not guild.me.guild_permissions.ban_members:
                failed.append(f"{guild.name} (no permission)")
                continue

            try:
                bans = await guild.bans()
                entry = discord.utils.find(
                    lambda e: e.user.id == user_id and e.reason and e.reason.endswith("(BanSync)"),
                    bans
                )
                if entry:
                    await guild.unban(entry.user, reason="Reverse BanSync")
                    total += 1
            except discord.Forbidden:
                failed.append(f"{guild.name} (forbidden)")
            except Exception as e:
                failed.append(f"{guild.name} ({type(e).__name__})")

        message = f"✅ Unbanned user `{user_id}` from {total} servers."
        if failed:
            message += f"\n❌ Failed in:\n" + "\n".join(failed)
        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(BanSync(bot))
