import discord
from redbot.core import commands, Config
import datetime

class FormManager(commands.Cog):
    """Manage and display Google Form responses."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=987654321)
        self.config.register_guild(form_url=None, log_channel=None, responses=[])

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def set_form_url(self, ctx, url: str):
        """Set the Google Form URL."""
        await self.config.guild(ctx.guild).form_url.set(url)
        await ctx.send(f"✅ Google Form URL set to: {url}")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def set_form_channel(self, ctx, channel: discord.TextChannel):
        """Set the channel to send Google Form responses."""
        await self.config.guild(ctx.guild).log_channel.set(channel.id)
        await ctx.send(f"✅ Form responses will be sent to: {channel.mention}")

    @commands.guild_only()
    @commands.command()
    async def formlink(self, ctx):
        """Get the currently set Google Form URL."""
        url = await self.config.guild(ctx.guild).form_url()
        if url:
            await ctx.send(f"📄 Google Form: {url}")
        else:
            await ctx.send("❌ No form URL has been set.")

    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    @commands.command()
    async def add_response(self, ctx, *, response: str):
        """
        Manually add a form response (for testing or external integration).
        Example: [p]add_response Name: John, Age: 25
        """
        log_channel_id = await self.config.guild(ctx.guild).log_channel()
        if not log_channel_id:
            await ctx.send("❌ Log channel not set. Use `[p]set_form_channel` first.")
            return

        response_data = {
            "timestamp": str(datetime.datetime.utcnow()),
            "content": response,
        }

        async with self.config.guild(ctx.guild).responses() as responses:
            responses.append(response_data)

        channel = ctx.guild.get_channel(log_channel_id)
        if channel:
            embed = discord.Embed(
                title="📝 New Google Form Response",
                description=response,
                color=discord.Color.green(),
                timestamp=datetime.datetime.utcnow(),
            )
            await channel.send(embed=embed)

        await ctx.send("✅ Response recorded and sent.")

    @commands.guild_only()
    @commands.command()
    async def list_responses(self, ctx):
        """List all saved responses."""
        responses = await self.config.guild(ctx.guild).responses()
        if not responses:
            await ctx.send("📭 No responses recorded.")
            return

        msg = "\n".join(
            f"[{i+1}] {r['timestamp']}: {r['content']}" for i, r in enumerate(responses[-5:])
        )
        await ctx.send(f"🗂 Last 5 responses:\n```\n{msg}\n```")

    @commands.guild_only()
    @commands.command()
    async def search_responses(self, ctx, *, keyword: str):
        """Search responses for a keyword."""
        responses = await self.config.guild(ctx.guild).responses()
        found = [r for r in responses if keyword.lower() in r['content'].lower()]

        if not found:
            await ctx.send("🔍 No matching responses.")
            return

        msg = "\n".join(f"{r['timestamp']}: {r['content']}" for r in found[:5])
        await ctx.send(f"🧾 Matching responses:\n```\n{msg}\n```")
