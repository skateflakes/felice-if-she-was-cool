from .bansync import BanSync

async def setup(bot):
    await bot.add_cog(BanSync(bot))
