import asyncio
import datetime
from redbot.core import commands, Config
from redbot.core.commands.converter import TimedeltaConverter
import asyncpraw

# Constants
ALLOWED_ROLE_ID = 901272962341154826
SUBREDDIT_NAME = "happytreefriends"

class RedditModeration(commands.Cog):
    """Reddit moderation tools for the bot owner and authorized role."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=459697638124552192)

    async def _get_reddit(self):
        creds = await self.config.api()
        return asyncpraw.Reddit(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            username=creds["username"],
            password=creds["password"],
            user_agent="RedditModCog"
        )

    def has_permission(self, ctx):
        return ctx.author.id == self.bot.owner_id or any(role.id == ALLOWED_ROLE_ID for role in ctx.author.roles)

    @commands.command()
    async def rban(self, ctx, user: str, *, reason: str = "No reason provided."):
        """Ban a user from the subreddit."""
        if not self.has_permission(ctx):
            return await ctx.send("❌ You don't have permission to use this command.")

        reddit = await self._get_reddit()
        subreddit = await reddit.subreddit(SUBREDDIT_NAME)
        try:
            await subreddit.banned.add(user, note=reason, ban_message=reason)
            await ctx.send(f"✅ Banned u/{user} from r/{SUBREDDIT_NAME}.")
        except Exception as e:
            await ctx.send(f"❌ Failed to ban u/{user}: {e}")

    @commands.command()
    async def runban(self, ctx, user: str):
        """Unban a user from the subreddit."""
        if not self.has_permission(ctx):
            return await ctx.send("❌ You don't have permission to use this command.")

        reddit = await self._get_reddit()
        subreddit = await reddit.subreddit(SUBREDDIT_NAME)
        try:
            await subreddit.banned.remove(user)
            await ctx.send(f"✅ Unbanned u/{user} from r/{SUBREDDIT_NAME}.")
        except Exception as e:
            await ctx.send(f"❌ Failed to unban u/{user}: {e}")

    @commands.command()
    async def rtempban(self, ctx, user: str, duration: TimedeltaConverter, *, reason: str = "Temporary ban"):
        """Temporarily ban a user from the subreddit."""
        if not self.has_permission(ctx):
            return await ctx.send("❌ You don't have permission to use this command.")

        duration_days = int(duration.total_seconds() // 86400)
        if duration_days < 1:
            return await ctx.send("⚠️ Duration must be at least 1 day.")

        reddit = await self._get_reddit()
        subreddit = await reddit.subreddit(SUBREDDIT_NAME)
        try:
            await subreddit.banned.add(user, duration=duration_days, note=reason, ban_message=reason)
            await ctx.send(f"✅ Temporarily banned u/{user} for {duration_days} day(s) from r/{SUBREDDIT_NAME}.")
        except Exception as e:
            await ctx.send(f"❌ Failed to tempban u/{user}: {e}")
