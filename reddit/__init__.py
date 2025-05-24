from .core import RedditMod

async def setup(bot):
    await bot.add_cog(RedditMod(bot))