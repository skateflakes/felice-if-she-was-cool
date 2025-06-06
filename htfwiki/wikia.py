import asyncio
import discord
from discord.ext import tasks
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from redbot.core.commands import Context, has_permissions
import logging
from .api import FandomAPI

log = logging.getLogger("red.felice.HTFWikia")

ROLE_ID = 1358201367503700095
EDIT_CHANNEL_ID = 1379623956889337906
FORUM_CHANNEL_ID = 1379627002608484373
REPORT_CHANNEL_ID = 1379672967256080397

def contains_delete_template(content: str) -> bool:
    return "{{Delete" in content.lower()

class HTFWikia(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.api = FandomAPI()
        self.ready = False
        self.edit_monitor_task = self.edit_monitor.start()

    async def cog_load(self):
        try:
            await self.api.login()
            self.ready = True
        except Exception as e:
            log.error("Fandom login failed: %s", e)

    def cog_unload(self):
        self.edit_monitor.cancel()

    @tasks.loop(seconds=60)
    async def edit_monitor(self):
        await self.bot.wait_until_red_ready()
        if not self.ready:
            return
        try:
            changes = await self.api.get_recent_changes()
            for change in changes:
                await self.process_change(change)
        except Exception as e:
            log.error("Failed to poll recent changes: %s", e)

    async def process_change(self, change: dict):
        page = change.get("title")
        user = change.get("user")
        comment = change.get("comment", "")
        rc_id = change.get("revid")

        content = await self.api.get_revision_content(rc_id)
        embed = discord.Embed(
            title="Wiki Edit",
            description=f"**Page:** {page}\n**User:** {user}\n**Comment:** {comment}",
            color=discord.Color.green()
        )
        embed.add_field(name="Link", value=f"https://happytreefriends.fandom.com/wiki/{page.replace(' ', '_')}")
        channel = self.bot.get_channel(EDIT_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

        if contains_delete_template(content):
            logchan = self.bot.get_channel(REPORT_CHANNEL_ID)
            if logchan:
                await logchan.send(f"⚠️ **Delete template used** on `{page}` by `{user}`")

    @commands.command()
    async def wikiblock(self, ctx: Context, user: str, time: str = "infinite", *, reason: str = "No reason specified."):
        if not await self.has_mod_role(ctx):
            return await ctx.send("You don't have permission to use this command.")
        success = await self.api.block_user(user, time, reason)
        if success:
            await self.api.post_message_wall(user, reason)
            await ctx.send(f"✅ Blocked `{user}` for `{time}`. Reason: {reason}")
        else:
            await ctx.send("❌ Failed to block user.")

    @commands.command()
    async def wikiunblock(self, ctx: Context, user: str, *, reason: str = "No reason specified."):
        if not await self.has_mod_role(ctx):
            return await ctx.send("You don't have permission to use this command.")
        success = await self.api.unblock_user(user, reason)
        if success:
            await ctx.send(f"✅ Unblocked `{user}`. Reason: {reason}")
        else:
            await ctx.send("❌ Failed to unblock user.")

    async def has_mod_role(self, ctx: Context) -> bool:
        return any(role.id == ROLE_ID for role in ctx.author.roles)
