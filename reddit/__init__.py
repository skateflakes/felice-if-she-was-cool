from .core import RedditPostListener
from .moderation import RedditModeration

async def setup(bot):
    await bot.add_cog(RedditPostListener(bot))
    await bot.add_cog(RedditModeration(bot))
