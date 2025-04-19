from .server_rules import RulesCog

async def setup(bot):
    await bot.add_cog(RulesCog(bot))
