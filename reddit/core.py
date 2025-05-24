import discord
from redbot.core import commands, Config
from .redditapi import get_reddit_instance
from .listener import RedditPostListener

ROLE_ID = 901272962341154826

class RedditMod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=4042024050)
        self.config.register_global(
            client_id=None,
            client_secret=None,
            username=None,
            password=None,
            user_agent="RedditModBot/0.1 by YourUsername"
        )
        self.reddit = None
        self.post_logger = RedditPostListener(bot, self)

    @commands.command()
    async def redditban(self, ctx, subreddit: str, username: str, *, reason: str = "No reason provided"):
        """Ban a user from a subreddit. Requires bot owner or specific role."""
        if not await self._has_permission(ctx):
            return await ctx.send("🚫 You do not have permission to use this command.")

        reddit = await get_reddit_instance(self.config)
        try:
            sub = reddit.subreddit(subreddit)
            sub.banned.add(username, ban_reason=reason)
            await ctx.send(f"✅ Banned u/{username} from r/{subreddit}")
        except Exception as e:
            await ctx.send(f"❌ Failed to ban user: {e}")

    async def _has_permission(self, ctx):
        return await self.bot.is_owner(ctx.author) or discord.utils.get(ctx.author.roles, id=ROLE_ID)