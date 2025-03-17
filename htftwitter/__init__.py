from .twitter_logger import TwitterLogger
from redbot.core.bot import Red

async def setup(bot: Red):
    await bot.add_cog(TwitterLogger(bot))
