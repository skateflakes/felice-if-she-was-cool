import discord
from redbot.core import commands
from .api import get_reddit_instance

class RedditMod(commands.Cog):
    """Reddit moderation for r/happytreefriends"""

    def __init__(self, bot):
        self.bot = bot
        self.reddit = get_reddit_instance()
        self.subreddit = self.reddit.subreddit("happytreefriends")

    @commands.command()
    async def redditban(self, ctx, user: str, duration: int = None, *, reason: str = "No reason specified."):
        """Ban a Reddit user from r/happytreefriends."""
        mod_note = f"User was banned by {ctx.author} through HTFBot on Discord."
        try:
            self.subreddit.banned.add(
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
        mod_note = f"Ban revoked by {ctx.author} through HTFBot on Discord."
        try:
            self.subreddit.banned.remove(user)
            self.subreddit.mod.notes.create(user, mod_note)
            await ctx.send(f"✅ Unbanned u/{user}. Reason: {reason}")
        except Exception as e:
            await ctx.send(f"❌ Failed to unban u/{user}: {e}")
