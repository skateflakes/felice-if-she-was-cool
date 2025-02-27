from redbot.core.bot import Red
from .slingshot import Screenshot

def setup(bot: Red):
    bot.add_cog(Screenshot(bot))
