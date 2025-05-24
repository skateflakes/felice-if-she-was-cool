import discord
from discord.ext import tasks
from redbot.core import commands, Config
import asyncpraw

class RedditPostListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=257596407911940097)
        default = {
            "client_id": "",
            "client_secret": "",
            "username": "",
            "password": ""
        }
        self.config.register_global(**default)
        self.post_check.start()

    def cog_unload(self):
        self.post_check.cancel()

    async def _get_reddit(self):
        return asyncpraw.Reddit(
            client_id=await self.config.client_id(),
            client_secret=await self.config.client_secret(),
            username=await self.config.username(),
            password=await self.config.password(),
            user_agent="HTFBot/1.0"
        )

    @tasks.loop(seconds=10)
async def post_check(self):
    reddit = await self._get_reddit()
    subreddit = await reddit.subreddit("happytreefriends")
    submissions = subreddit.stream.submissions(skip_existing=True)

    while True:
        try:
            submission = await submissions.__anext__()
        except Exception as e:
            print(f"[RedditPostListener] Stream error: {e}")
            break

        channel = self.bot.get_channel(1375574181567139880)
        if channel:
            embed = discord.Embed(
                title=submission.title,
                url=submission.url,
                description=submission.selftext[:2000],
                color=discord.Color.orange()
            )
            embed.set_author(name=submission.author.name)
            await channel.send(embed=embed)
