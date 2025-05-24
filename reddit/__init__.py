from .core import RedditPostListener

async def setup(bot):
    await bot.add_cog(RedditPostListener(bot))
