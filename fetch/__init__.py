from .modfetch import ModFetch

async def setup(bot):
    await bot.add_cog(ModFetch(bot))
