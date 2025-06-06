import discord
from redbot.core import commands
from .api import get_reddit_instance
import re

def has_redditmod_role():
    async def predicate(ctx):
        allowed_role_id = 901273156558413834
        return any(role.id == allowed_role_id for role in ctx.author.roles)
    return commands.check(predicate)

class RedditMod(commands.Cog):
    """Reddit moderation for r/happytreefriends"""

    def __init__(self, bot):
        self.bot = bot
        self.reddit = None
        self.subreddit = None

    async def cog_load(self):
        self.reddit = await get_reddit_instance(self.bot)
        self.subreddit = await self.reddit.subreddit("happytreefriends")

    @commands.command()
    @has_redditmod_role()
    async def redditban(self, ctx, user: str, duration: str = None, *, reason: str = "No reason specified."):
        """Ban a Reddit user. Duration formats: 12h, 7d, 2w, 1m (optional)."""
        mod_note = f"User was banned by {ctx.author} through HTFBot on Discord."
        duration_days = None

        if duration:
            match = re.match(r"^(\d+)([hdwm])$", duration.lower())
            if match:
                num, unit = int(match.group(1)), match.group(2)
                if unit == "h":
                    duration_days = max(1, num // 24)  # Reddit minimum = 1 day
                elif unit == "d":
                    duration_days = num
                elif unit == "w":
                    duration_days = num * 7
                elif unit == "m":
                    duration_days = num * 30
            else:
                reason = f"{duration} {reason}".strip()
                duration_days = None

        try:
            if duration_days:
                await self.subreddit.banned.add(
                    user,
                    duration=duration_days,
                    note=mod_note,
                    ban_reason=reason,
                    ban_message="You have been banned from r/happytreefriends."
                )
                await ctx.send(f"✅ Banned u/{user} for {duration_days} day(s).\nReason: {reason}")
            else:
                await self.subreddit.banned.add(
                    user,
                    note=mod_note,
                    ban_reason=reason,
                    ban_message="You have been banned from r/happytreefriends."
                )
                await ctx.send(f"✅ Permanently banned u/{user}.\nReason: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Failed to ban u/{user}: {e}")

    @commands.command()
    @has_redditmod_role()
    async def redditunban(self, ctx, user: str, *, reason: str = "No reason specified."):
        """Unban a Reddit user from r/happytreefriends."""
        try:
            await self.subreddit.banned.remove(user)
            await ctx.send(f"✅ Unbanned u/{user}. Reason: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Failed to unban u/{user}: {e}")
