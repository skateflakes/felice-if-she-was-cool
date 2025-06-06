from .wikia import HTFWikia

async def setup(bot):
    await bot.add_cog(HTFWikia(bot))
