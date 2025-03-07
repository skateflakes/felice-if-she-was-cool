from .server_rules import ServerRules
from redbot.core.bot import Red

async def setup(bot: Red):
    await bot.add_cog(ServerRules(bot))
