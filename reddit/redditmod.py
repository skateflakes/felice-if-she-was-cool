import discord
from redbot.core import commands
from .api import get_reddit_instance

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
    async def redditban(self, ctx, user: str, duration: int = None, *, reason: str = "No reason specified."):
        """Ban a Reddit user from r/happytreefriends."""
        mod_note = f"User was banned by {ctx.author} through HTFBot on Discord."
        try:
            await self.subreddit.banned.add(
                user,
                duration=duration,
                note=mod_note,
                ban_reason=reason,
                ban_message="You have been banned from r/happytreefriends."
            )
            await ctx.send(f"✅ Banned u/{user} {'for ' + str(duration) + ' days' if duration else 'permanently'}.\nReason: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Failed to ban u/{user}: {e}")

    @commands.command()
    async def redditunban(self, ctx, user: str, *, reason: str = "No reason specified."):
        """Unban a Reddit user from r/happytreefriends."""
        try:
            await self.subreddit.banned.remove(user)
            await ctx.send(f"✅ Unbanned u/{user}. Reason: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Failed to unban u/{user}: {e}")
