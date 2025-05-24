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
    async def redditban(self, ctx, username: str, *, reason: str = "No reason provided"):
        """Ban a user from the subreddit. Only available for moderators of the r/happytreefriends Discord server."""
        if not await self._has_permission(ctx):
            return await ctx.send("🚫 You do not have permission to use this command.")

        reddit = await get_reddit_instance(self.config)
        try:
            sub = reddit.subreddit("happytreefriends")
            sub.banned.add(username, ban_reason=reason)
            await ctx.send(f"✅ Banned u/{username} from r/happytreefriends")
        except Exception as e:
            await ctx.send(f"❌ Failed to ban user: {e}")
    @commands.group()
    @commands.is_owner()
    async def api(self, ctx):
        """Reddit API credentials configuration."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Available subcommands: set")

    @api.command()
    async def set(self, ctx, client_id: str, client_secret: str, username: str, password: str):
        """Set Reddit API credentials."""
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await self.config.username.set(username)
        await self.config.password.set(password)
        await ctx.send("✅ Reddit API credentials set.")


    async def _has_permission(self, ctx):
        return await self.bot.is_owner(ctx.author) or discord.utils.get(ctx.author.roles, id=ROLE_ID)
