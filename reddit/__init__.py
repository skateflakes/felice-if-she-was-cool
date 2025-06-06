from .redditmod import RedditMod

async def setup(bot):
    await bot.add_cog(RedditMod(bot))
