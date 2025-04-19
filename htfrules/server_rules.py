import discord
from redbot.core import commands

# Whitelisted guilds
WHITELISTED_GUILDS = {
    123456789012345678,  # Replace with real guild IDs
    987654321098765432
}

# Rules with subrules
RULES = {
    "a": {
        1: {
            "text": "Respect all members.",
            "subtext": "Harassment or discrimination creates a hostile environment."
        },
        2: {
            "text": "No hate speech.",
            "subtext": "This includes slurs, threats, and targeting."
        }
    },
    "b": {
        1: {
            "text": "No spamming.",
            "subtext": "Spamming disrupts communication and floods channels."
        }
    },
    "c": {
        1: {
            "text": "No NSFW content.",
            "subtext": "This server is meant to be safe for all ages."
        }
    }
}

RULES_DOC_LINK = "https://docs.google.com/document/d/e/2PACX-1vTvMfTZy24lQihE9J6MV1Jh2hoHCRzpqx3nM73goqhHP8ydlerWNdfSvx0ag-X0XUddfHD0cvE8AIs5/pub"


class RulesCog(commands.Cog):
    """Custom rules cog using r. prefix and subrule support."""

    def __init__(self, bot):
        self.bot = bot
        self.custom_prefix = "r."

    async def cog_check(self, ctx):
        """Restrict the cog to whitelisted servers only."""
        return ctx.guild and ctx.guild.id in WHITELISTED_GUILDS

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return
        if message.guild.id not in WHITELISTED_GUILDS:
            return

        if not message.content.lower().startswith(self.custom_prefix):
            return

        cmd = message.content[len(self.custom_prefix):].strip().lower()

        if len(cmd) < 2 or not cmd[0] in RULES or not cmd[1:].isdigit():
            return

        section = cmd[0]
        number = int(cmd[1:])

        rule_obj = RULES.get(section, {}).get(number)
        if not rule_obj:
            return

        text = rule_obj["text"]
        subtext = rule_obj["subtext"]

        rule_msg = (
            f"**Rule {section.upper()}{number}**:\n"
            f"{text}\n"
            f"{subtext}\n\n"
            f"📄 Please read the full rules here:\n{RULES_DOC_LINK}"
        )

        await message.channel.send(rule_msg)


async def setup(bot):
    await bot.add_cog(RulesCog(bot))
