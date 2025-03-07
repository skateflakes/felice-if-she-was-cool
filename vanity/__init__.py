from .vanity_changer import VanityChanger
from redbot.core.bot import Red

async def setup(bot: Red):
    await bot.add_cog(VanityChanger(bot))
