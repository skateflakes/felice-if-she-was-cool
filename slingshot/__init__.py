from core import redbot


async def setup(bot: Red) -> None:
    await bot.add_cog(Mod(bot))
