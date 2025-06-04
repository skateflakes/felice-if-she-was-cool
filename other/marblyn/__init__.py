from .marblyn import Marblyn

async def setup(bot):
    await bot.add_cog(Marblyn(bot))
