import discord
from redbot.core import commands

# Whitelisted guilds
WHITELISTED_GUILDS = {
    1033567360692523008  # Replace with real guild IDs
}

# Rules with subrules
RULES = {
    "a": {
        1: {
            "text": "Disrespect towards other server members",
            "subtext": "We want this server to be enjoyable for everyone. Constructive criticism isn't disrespectful. Please respect the members of the server."
        },
        2: {
            "text": "Excessively using swear words",
            "subtext": "Swearing is 100% allowed. Please don't excessively swear in the chat."
        },
        3: {
            "text": "Use of languages other than English",
            "subtext": "This is to make it easy to moderate messages. We ask you to use English on this server."
        },
        4: {
            "text": "Excessively discussing about banned or problematic people",
            "subtext": "We ask you to not bring up any problematic people, as it causes issues.\n- Discussion about controversial users are not allowed anywhere on the server. Move it to Direct Messages."
        },
        5: {
            "text": "Posting things outside of specific channels",
            "subtext": "Post memes in #memes, and post art and other things you made in #arts-and-crafts."
        },
        6: {
            "text": "Having an unpingable username/nickname",
            "subtext": "“Fancy” text in your name isn't allowed, we will ask you to change it, or change your nickname so it's easier for users to ping you."
        },
        7: {
            "text": "Voice Chat Misusage",
            "subtext": "Screaming, playing loud music, and screen sharing inappropriate content\n- Do not troll, or constantly skip audio in the Music VC."
        },
        8: {
            "text": "Asking for roles that are not available in 🔍 Browse Channels",
            "subtext": "We will never release any staff applications. Moderation is handpicked by Senior Administrators."
        },
        9: {
            "text": "Misuse of the ping function",
            "subtext": "Do not mass ping users in the server.\n- Do not ping the HTF crew or Vixa Games without a proper reason. (“Where’s HTF?”)"
        },
        10: {
            "text": "Having member(s) of the staff team blocked",
            "subtext": "If a staff member is being a problem to you or anyone else in the server, or the fandom itself, please DM a Senior Administrator, and we will look into it.\n- We have this rule in place because we need to DM you for important things, like if you have received a warning, etc."
        },
        11: {
            "text": "Minimodding",
            "subtext": "If a user is breaking the rules of the server, ping an online staff member. **More info is in the rules doc.**"
        },
        12: {
            "text": "Posting sensitive attachments without a warning",
            "subtext": "Attachments that are loud, flashing, etc.\n- Please apply a spoiler to the attachment instead, with a warning shown."
        },
        13: {
            "text": "Erotic Roleplaying, inside or outside the #roleplay channel",
            "subtext": "Do that in Direct Messages __with the user’s permission__, not in the server."
        },
        14: {
            "text": "Bypassing AutoMod words",
            "subtext": "We have a set of blacklisted users from the server and we do not want them brought up."
        },
        15: {
            "text": "Venting in the public chat",
            "subtext": "Please don't vent in the public chat. Keep things like this in Direct Messages as it can lead to topics not allowed for the server."
        },
        16: {
            "text": "Spoilers outside of the #spoilers channel",
            "subtext": "For access to the spoilers channel you must select the `@Spoilers` role via <id:customization>"
        },
        17: {
            "text": "Posting AI content",
            "subtext": "Posting AI (mostly images) is not allowed."
        },
        18: {
            "text": "Going off-topic in <#1165649280506269777> or <#1165649355370401832>",
            "subtext": "Please use #htf for talking about HTF and #mondo for talking about other MondoMedia content (including HTF).\n- This also includes forcibly changing the subject in the other channels."
        }
    },
    "b": {
        1: {
            "text": "Spamming the chat",
            "subtext": "Using bots is okay, don't go too overboard with them.\n- Do not purposefully spam the chat."
        },
        2: {
            "text": "Not listening to Server Staff",
            "subtext": "Listen to what the server staff tells you to do.\n- Do not abuse loopholes."
        },
        3: {
            "text": "Tampering with the bots or abusing them",
            "subtext": "If there's a bug with a bot, please report them to a staff member instead!"
        },
        4: {
            "text": "Usage of foul language",
            "subtext": "Do not use the ableist, racist, and homophobic slurs.\n  - Usage of these slurs, even being part of these, are also not allowed.\n- You will be given a one week timeout by AutoMod if you use these slurs."
        },
        5: {
            "text": "Unsanitary jokes towards people",
            "subtext": "Don’t use these towards people. Since Mondo Media’s shows have unsanitary jokes, we’re gonna allow it on this server but not excessively."
        },
        6: {
            "text": "Serious politician discussion/argument",
            "subtext": "Please keep conversations like these outside of the server."
        },
        7: {
            "text": "Sending offensive memes",
            "subtext": "You will be removed from the <#1165650627901272064> channel for this. Otherwise, it could lead to a ban too."
        },
        8: {
            "text": "Starting any sort of drama in the chat",
            "subtext": "We do not want **any** drama on this server. If you join the server with the purpose of bringing up drama (rather than letting a staff member know first) will just lead you to a Section C offense (a ban)."
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
            f"**Rule {number} of Section {section.upper()}**:\n"
            f"```{text}```\n"
            f"- {subtext}\n\n"
            f"📄 Please read the full rules here:\n{RULES_DOC_LINK}"
        )

        await message.channel.send(rule_msg)


async def setup(bot):
    await bot.add_cog(RulesCog(bot))
