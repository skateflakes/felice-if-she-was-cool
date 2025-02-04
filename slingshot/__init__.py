from .mycog import slingshot


async def setup(bot):
    await bot.add_cog(slingshot(bot))
