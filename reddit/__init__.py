from .redditmoderation import RedditModeration

async def setup(bot):
    await bot.add_cog(RedditModeration(bot))
