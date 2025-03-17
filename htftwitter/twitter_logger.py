import discord
from redbot.core import commands, Config
import aiohttp
import asyncio

class TwitterLogger(commands.Cog):
    """A cog to log new posts in a Twitter/X community."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)
        self.config.register_guild(community_id=None, log_channel=None, last_post_id=None)
        self.session = aiohttp.ClientSession()
        self.bg_task = self.bot.loop.create_task(self.monitor_twitter())

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def set_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel to log new Twitter posts."""
        await self.config.guild(ctx.guild).log_channel.set(channel.id)
        await ctx.send(f"Log channel set to {channel.mention}.")

    async def monitor_twitter(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            for guild in self.bot.guilds:
                community_id = "1673840860641755137"
                log_channel_id = await self.config.guild(guild).log_channel()
                last_post_id = await self.config.guild(guild).last_post_id()

                if community_id and log_channel_id:
                    new_posts = await self.fetch_community_posts(community_id, last_post_id)
                    if new_posts:
                        channel = guild.get_channel(log_channel_id)
                        for post in reversed(new_posts):
                            embed = discord.Embed(title="New Post in Twitter Community", description=post['text'], url=f"https://twitter.com/{post['author_id']}/status/{post['id']}")
                            await channel.send(embed=embed)
                            await self.config.guild(guild).last_post_id.set(post['id'])

            await asyncio.sleep(10)  # Check every 10 seconds

    async def fetch_community_posts(self, community_id, last_post_id):
        # Mock API URL (Replace this with the actual Twitter API v2 endpoint)
        url = f"https://api.twitter.com/2/timelines/community/{community_id}.json"
        headers = {"Authorization": "Bearer YOUR_TWITTER_BEARER_TOKEN"}

        async with self.session.get(url, headers=headers) as response:
            if response.status == 200:
                data = await response.json()
                posts = data.get("data", [])

                if last_post_id:
                    # Filter only new posts
                    new_posts = [post for post in posts if post['id'] > last_post_id]
                    return new_posts
                else:
                    return posts

    def cog_unload(self):
        self.bg_task.cancel()
        self.bot.loop.create_task(self.session.close())

async def setup(bot):
    await bot.add_cog(TwitterLogger(bot))
