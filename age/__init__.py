from .dobmanager import DOBManager

async def setup(bot):
    await bot.add_cog(DOBManager(bot))
