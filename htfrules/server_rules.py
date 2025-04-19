import discord
from redbot.core import commands

# Whitelisted guilds
WHITELISTED_GUILDS = {
    1033567360692523008  # Replace with real guild IDs
}

# Rules with subrules
RULES = {
    "a": {
        # ... (no change to section a)
    },
    "b": {
        # ... (no change to section b)
    },
    "c": {
        1: {
            "text": "Breaking Discord’s [Terms of Service](https://discord.com/terms) or [Community Guidelines](https://discord.com/guidelines)",
            "subtext": (
                "If you are under the age of 13, you will be banned. You may rejoin when you're 13.\n"
                "- **If you lie about your age to stay in the server until you turn 13, you will be permanently banned without an appeal. "
                "In order to comply with the law and Discord’s ToS, we have to strictly enforce this rule.**\n"
                "- If you raid the server or organize one, you will be banned along with your Discord account reported.\n"
                "- If you have been known to raid other HTF servers, you will be banned from this server."
            )
        },
        2: {
            "text": "Incitement or Discussion of illegal activity",
            "subtext": (
                "Which includes:\n"
                "- Doxxing\n"
                "- Pirated Content\n"
                "- Real-life threats\n"
                "- ETC"
            )
        },
        3: {
            "text": "Posting inappropriate content",
            "subtext": (
                "Not Safe For Work (NSFW) isn't allowed and will never be tolerated ever.\n"
                "- Posting NSFW art is also not tolerated.\n"
                "Drawn gore is okay (as Happy Tree Friends is mainly gruesome), **real life gore (including rat abuse videos) leads to a ban.**\n"
                "- This rule also complies to any form of fetish content."
            )
        },
        4: {
            "text": "Discrimination",
            "subtext": "Inappropriate discussions discriminating against anyone based on their race, sexuality, religion, gender, etc, is not tolerated at all.\n- Deadnaming and misgendering others will also result in a ban."
        },
        5: {
            "text": "Impersonation",
            "subtext": "If you are pretending to be someone else, you will be asked to change your appearance. Otherwise, you will be banned.\n- Impersonating staff will lead to an immediate ban and it cannot be appealed."
        },
        6: {
            "text": "Joining the server to troll",
            "subtext": "Just don't. Find something better to do."
        },
        7: {
            "text": "Attempting to circumvent a moderation action",
            "subtext": "This server has autoroles, if you get caught evading a mute your mute will stay permanent and unappealable.\n- Asking a staff member to revoke moderation action also counts\n- We will find out if you attempt to spy on the server."
        },
        8: {
            "text": "Sending malicious attachments/links",
            "subtext": "If your Discord account was hacked, send in an appeal and we will unban you and give you directions on how to secure your account."
        },
        9: {
            "text": "Sending any official paid Mondo products in the chat",
            "subtext": "Continuation to Rule C2. We’re going to strictly enforce this rule and sending attachments, like the Still Alive package or The Crackpet Show will result in a permanent ban."
        },
        10: {
            "text": "Attempting to start any argument with staff after receiving infractions",
            "subtext": "Use common sense. Either take the moderation action or appeal. Do not argue with staff about it."
        },
        11: {
            "text": "Unsolicited Direct Messages",
            "subtext": "Do not DM advertise to users of the server, unless they have asked. There is an ads channel, use it!\n- Do not message the Vixa Games staff team any complaints about the server, use the feedback form instead, and we will do our best to improve the server."
        },
        12: {
            "text": "Leaking Member-Only Content",
            "subtext": "Leaking any previews of MondoMedia’s membership-only features (such as HTF Episode Previews) in the server isn't allowed.\n- Sending MondoMedia’s community posts will only result in a warning with your message being deleted."
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
            f"**Rule {number} of Section {section.upper()}**:\n"
            f"```{text}```\n"
            f"- {subtext}\n\n"
            f"📄 Please read the full rules here:\n{RULES_DOC_LINK}"
        )

        await message.channel.send(rule_msg)

async def setup(bot):
    await bot.add_cog(RulesCog(bot))
