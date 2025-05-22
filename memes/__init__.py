from redbot.core import commands
from .mememaker import MemeMaker

async def setup(bot: commands.Bot):
    await bot.add_cog(MemeMaker(bot))
