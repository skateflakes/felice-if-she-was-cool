from redbot.core.bot import Red
from .slingshot import Screenshot

async def setup(bot: Red) -> None:
    await bot.add_cog(Screenshot(bot))
