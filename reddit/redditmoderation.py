import discord
from redbot.core import commands, Config
from redbot.core.commands import Context
from discord.ext import tasks
import asyncpraw
import asyncio
from typing import Optional
from datetime import datetime, timedelta

ROLE_ID = 901273156558413834
POST_LOG_CHANNEL_ID = 1375574181567139880
MODQUEUE_CHANNEL_ID = 1376760281983877161
SUBREDDIT = "happytreefriends"

class RedditModeration(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890, force_registration=True)
        default_global = {
            "client_id": "",
            "client_secret": "",
            "username": "",
            "password": ""
        }
        self.config.register_global(**default_global)
        self.reddit = None
        self.post_stream_task.start()

    def cog_unload(self):
        self.post_stream_task.cancel()

    async def initialize_reddit(self):
        creds = await self.config.all()
        if not all(creds.values()):
            return None
        self.reddit = asyncpraw.Reddit(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            username=creds["username"],
            password=creds["password"],
            user_agent="HTFBot/1.0"
        )
        return self.reddit

    @commands.command()
    @commands.is_owner()
    async def setredditapi(self, ctx: Context, client_id: str, client_secret: str, username: str, password: str):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await self.config.username.set(username)
        await self.config.password.set(password)
        await ctx.send("Reddit API credentials have been set.")

    def _is_mod(ctx):
        return ctx.author.id == ctx.bot.owner_id or any(role.id == ROLE_ID for role in ctx.author.roles)

    @commands.command()
    @commands.check(_is_mod)
    async def redditban(self, ctx: Context, user: str, *, reason: Optional[str] = "Reason not specified."):
        reddit = await self.initialize_reddit()
        if not reddit:
            return await ctx.send("Reddit API not configured.")
        subreddit = await reddit.subreddit(SUBREDDIT)
        await subreddit.banned.add(user, note=reason)
        await ctx.send(f"Banned u/{user}.")
Reason: {reason}")

    @commands.command()
    @commands.check(_is_mod)
    async def reddittempban(self, ctx: Context, user: str, duration: int, *, reason: Optional[str] = "Reason not specified."):
        reddit = await self.initialize_reddit()
        if not reddit:
            return await ctx.send("Reddit API not configured.")
        subreddit = await reddit.subreddit(SUBREDDIT)
        await subreddit.banned.add(user, duration=duration, note=reason)
        await ctx.send(f"Temporarily banned u/{user} for {duration} days.
Reason: {reason}")

    @commands.command()
    @commands.check(_is_mod)
    async def redditunban(self, ctx: Context, user: str):
        reddit = await self.initialize_reddit()
        if not reddit:
            return await ctx.send("Reddit API not configured.")
        subreddit = await reddit.subreddit(SUBREDDIT)
        await subreddit.banned.remove(user)
        await ctx.send(f"Unbanned u/{user}.")

    @tasks.loop(seconds=60)
    async def post_stream_task(self):
        await self.bot.wait_until_ready()
        reddit = await self.initialize_reddit()
        if not reddit:
            return
        subreddit = await reddit.subreddit(SUBREDDIT)
        async for post in subreddit.stream.submissions(skip_existing=True):
            try:
                channel = self.bot.get_channel(POST_LOG_CHANNEL_ID)
                if not channel:
                    continue
                embed = discord.Embed(title=post.title, description=(post.selftext[:197] + "...") if post.selftext else None, color=discord.Color.red())
                view = discord.ui.View()
                view.add_item(discord.ui.Button(label="Source", url=f"https://reddit.com{post.permalink}"))
                await channel.send(embed=embed, view=view)
            except Exception:
                continue
