import discord
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.commands import Context
from .api import FandomAPI
import asyncio
import logging

log = logging.getLogger("red.felice.wikia")

class WikiaMod(commands.Cog):
    """Fandom Wiki moderation and logging for Happy Tree Friends."""

    def __init__(self, bot: Red):
        self.bot = bot
        self.api = FandomAPI()
        self.edit_log_channel = 1379623956889337906
        self.forum_log_channel = 1379627002608484373
        self.report_log_channel = 1379672967256080397
        self._loop_task = self.bot.loop.create_task(self.edit_monitor())
        self.bot.loop.create_task(self.api.login(bot))

    def cog_unload(self):
        self._loop_task.cancel()

    async def edit_monitor(self):
        await self.bot.wait_until_ready()
        last_rcid = None
        while True:
            try:
                changes = await self.api.get_recent_changes()
                for change in reversed(changes):
                    if last_rcid is not None and change["rcid"] <= last_rcid:
                        continue
                    await self.process_change(change)
                    last_rcid = change["rcid"]
            except Exception as e:
                log.exception("Failed to poll recent changes: %s", e)
            await asyncio.sleep(90)

    async def process_change(self, change):
        ns = change.get("ns", 0)
        page = change["title"]
        user = change["user"]
        comment = change.get("comment", "")
        minor = change.get("minor", False)
        oldid = change.get("old_revid", 0)
        new_id = change["revid"]

        content = await self.api.get_revision_content(new_id)
        if "{{Delete" in content:
            await self.log_delete_template(change)

        embed = discord.Embed(
            title="Wiki Edit",
            description=f"**Page:** {page}
**User:** {user}
**Comment:** {comment or '—'}",
            color=discord.Color.orange()
        )
        embed.add_field(name="Minor Edit?", value="Yes" if minor else "No", inline=True)
        embed.add_field(
            name="Diff",
            value=f"https://happytreefriends.fandom.com/wiki/{page.replace(' ', '_')}?diff={new_id}&oldid={oldid}",
            inline=False
        )
        await self.send_to_channel(self.edit_log_channel, embed)

        if ns in [1201, 1202]:
            await self.send_to_channel(self.forum_log_channel, embed)

    async def log_delete_template(self, change):
        page = change["title"]
        user = change["user"]
        embed = discord.Embed(
            title="Delete Template Detected",
            description=f"**Page:** {page}
**User:** {user}
Marked for deletion with `{{{{Delete}}}}`",
            color=discord.Color.red()
        )
        await self.send_to_channel(self.report_log_channel, embed)

    async def send_to_channel(self, channel_id: int, embed: discord.Embed):
        channel = self.bot.get_channel(channel_id)
        if channel:
            await channel.send(embed=embed)

    @commands.command()
    async def wikiblock(self, ctx: Context, user: str, duration: str = "infinite", *, reason: str = "No reason specified."):
        success = await self.api.block_user(user, duration, reason)
        if success:
            await ctx.send(f"✅ Blocked `{user}` for `{duration}`. Reason: {reason}")
        else:
            await ctx.send("❌ Failed to block user.")

    @commands.command()
    async def wikiunblock(self, ctx: Context, user: str, *, reason: str):
        success = await self.api.unblock_user(user, reason)
        if success:
            await ctx.send(f"✅ Unblocked `{user}`. Reason: {reason}")
        else:
            await ctx.send("❌ Failed to unblock user.")
