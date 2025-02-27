from redbot.core.bot import Red
from screenshot import Screenshot


async def setup(bot: Red) -> None:
    await bot.add_cog(Mod(bot))
