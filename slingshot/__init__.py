from .htf import slingshot


async def setup(bot: Red) -> None:
    await bot.add_cog(Mod(bot))
