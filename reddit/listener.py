import discord
from discord.ext import tasks
import asyncio
import praw
from .redditapi import get_reddit_instance

POST_LOG_CHANNEL_ID = 1375574181567139880  # hardcoded

class RedditPostListener:
    def __init__(self, bot, cog):
        self.bot = bot
        self.cog = cog
        self.logged_ids = set()
        self.log_posts.start()

    @tasks.loop(seconds=60)
    async def log_posts(self):
        reddit = await get_reddit_instance(self.cog.config)
        subreddit = reddit.subreddit("happytreefriends")

        channel = self.bot.get_channel(POST_LOG_CHANNEL_ID)
        if channel is None:
            return

        try:
            async for post in subreddit.stream.submissions(skip_existing=True):
                if post.id in self.logged_ids:
                    continue
                self.logged_ids.add(post.id)
                embed = discord.Embed(title=post.title, url=post.url, description=post.selftext[:2000])
                embed.set_author(name=f"r/{post.subreddit}", url=f"https://reddit.com{post.permalink}")
                embed.set_footer(text=f"Posted by u/{post.author}")
                await channel.send(embed=embed)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"[RedditPostListener] Error: {e}")
