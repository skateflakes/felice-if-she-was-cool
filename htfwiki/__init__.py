from .wikia import WikiaMod

async def setup(bot):
    await bot.add_cog(WikiaMod(bot))
