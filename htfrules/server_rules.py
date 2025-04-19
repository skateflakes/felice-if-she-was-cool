import discord
from redbot.core import commands
from discord.ext import commands as ext_commands

# Only allow the cog in these guilds
WHITELISTED_GUILDS = {
    1033567360692523008  # this command can only work in the HTF server
}

# Hardcoded rules
RULES = {
    "a": {
        1: "Respect all members.",
        2: "No harassment or hate speech.",
        3: "Keep discussions civil."
    },
    "b": {
        1: "Do not spam.",
        2: "Use appropriate channels.",
        3: "No excessive tagging."
    },
    "c": {
        1: "Do not share NSFW content.",
        2: "No ban evasion.",
        3: "Respect server decisions."
    }
}

RULES_DOC_LINK = "https://docs.google.com/document/d/e/2PACX-1vTvMfTZy24lQihE9J6MV1Jh2hoHCRzpqx3nM73goqhHP8ydlerWNdfSvx0ag-X0XUddfHD0cvE8AIs5/pub"

class RulesCog(commands.Cog):
    """Cog for displaying rules using a custom prefix (r.)."""

    def __init__(self, bot):
        self.bot = bot
        self.custom_prefix = "r."

    async def cog_check(self, ctx):
        """Restrict the cog to whitelisted servers only."""
        return ctx.guild and ctx.guild.id in WHITELISTED_GUILDS

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore bot messages or DMs
        if message.author.bot or not message.guild:
            return
        if message.guild.id not in WHITELISTED_GUILDS:
            return

        # Check for custom "r." prefix
        if not message.content.lower().startswith(self.custom_prefix):
            return

        cmd = message.content[len(self.custom_prefix):].strip().lower()

        # Format must be like: r.a1, r.b3, etc.
        if len(cmd) < 2 or not cmd[0] in RULES or not cmd[1:].isdigit():
            return

        section = cmd[0]
        number = int(cmd[1:])

        rule = RULES.get(section, {}).get(number)
        if not rule:
            return

        rule_msg = f"**Rule {section.upper()}{number}**:\n{rule}\n\n📄 Please read the full rules here:\n{RULES_DOC_LINK}"
        await message.channel.send(rule_msg)

async def setup(bot):
    await bot.add_cog(RulesCog(bot))
