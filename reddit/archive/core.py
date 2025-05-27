import discord
from redbot.core import commands, Config
import asyncpraw
import asyncio

class RedditPostListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        default_global = {
            "client_id": "",
            "client_secret": "",
            "username": "",
            "password": ""
        }
        self.config.register_global(**default_global)
        self.reddit_loop = self.bot.loop.create_task(self.post_listener())

    def cog_unload(self):
        self.reddit_loop.cancel()

    async def get_reddit_instance(self):
        creds = await self.config.all()
        return asyncpraw.Reddit(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            username=creds["username"],
            password=creds["password"],
            user_agent="HTFBot/1.0"
        )

    @commands.command()
    @commands.is_owner()
    async def setredditapi(self, ctx, client_id: str, client_secret: str, username: str, password: str):
        await self.config.client_id.set(client_id)
        await self.config.client_secret.set(client_secret)
        await self.config.username.set(username)
        await self.config.password.set(password)
        await ctx.send("Reddit API credentials saved.")

    async def post_listener(self):
        await self.bot.wait_until_ready()
        try:
            reddit = await self.get_reddit_instance()
            subreddit = await reddit.subreddit("happytreefriends")
            async for post in subreddit.stream.submissions():
                channel = discord.utils.get(self.bot.get_all_channels(), name="reddit-logs")
                if channel:
                    embed = discord.Embed(title=post.title, url=post.url, description=post.selftext[:2048])
                    embed.set_author(name=post.author.name if post.author else "[deleted]")
                    await channel.send(embed=embed)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[RedditPostListener] Stream error: {e}")
