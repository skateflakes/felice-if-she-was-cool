from redbot.core.bot import Red
from .slingshot import Screenshot

async def setup(bot: Red):
    await bot.add_cog(Screenshot(bot))
