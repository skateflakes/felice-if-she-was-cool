import discord
from discord.ext import tasks
from redbot.core import commands
from pathlib import Path
import asyncpraw
import json
import os

def load_settings():
    path = Path("C:\Users\lenovo\AppData\Local\Red-DiscordBot\Red-DiscordBot\data\felice\cogs\RedditModeration")
    with open(path, "r") as f:
        return json.load(f)

SETTINGS = load_settings()

class RedditPostListener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.post_check.start()

    def cog_unload(self):
        self.post_check.cancel()

    async def _get_reddit(self):
        return asyncpraw.Reddit(
            client_id=SETTINGS["client_id"],
            client_secret=SETTINGS["client_secret"],
            username=SETTINGS["username"],
            password=SETTINGS["password"],
            user_agent="HTFBot/1.0"
        )

    @tasks.loop(minutes=1)
    async def post_check(self):
        try:
            reddit = await self._get_reddit()
            subreddit = await reddit.subreddit("happytreefriends")
            async for submission in subreddit.stream.submissions(skip_existing=True):
                channel = self.bot.get_channel(1375574181567139880)  # Your channel ID
                if channel:
                    embed = discord.Embed(
                        title=submission.title,
                        url=submission.url,
                        description=submission.selftext[:2000],
                        color=discord.Color.orange()
                    )
                    embed.set_author(name=submission.author.name)
                    await channel.send(embed=embed)
        except Exception as e:
            print(f"[RedditPostListener] Stream error: {e}")
