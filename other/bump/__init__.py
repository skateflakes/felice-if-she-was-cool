from .bump import BumpLock

async def setup(bot):
    await bot.add_cog(BumpLock(bot))
