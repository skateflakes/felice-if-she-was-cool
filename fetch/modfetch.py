import discord
from redbot.core import commands
from datetime import datetime
from asyncio import TimeoutError

MOCK_LOGS = [
    {
        "user_id": "1234567890",
        "type": "warn",
        "reason": "Spamming",
        "guild_name": "Cool Server",
        "mod_name": "ModUser",
        "timestamp": "2025-04-01T14:22:00"
    },
    {
        "user_id": "1234567890",
        "type": "ban",
        "reason": "TOS violation",
        "guild_name": "Chill Zone",
        "mod_name": "Admin123",
        "timestamp": "2025-03-25T08:45:00"
    }
]

class ModFetch(commands.Cog):
    """Fetch mod logs for a user (with pagination)."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def fetch(self, ctx, user: discord.User):
        """Fetch warnings, kicks, bans for a user across servers."""
        user_logs = [log for log in MOCK_LOGS if log["user_id"] == str(user.id)]
        if not user_logs:
            await ctx.send(f"✅ No logs found for `{user}`.")
            return

        # Sort logs by most recent
        user_logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        pages = self.paginate_logs(user_logs, user)

        current = 0
        message = await ctx.send(embed=pages[current])
        await message.add_reaction("◀️")
        await message.add_reaction("▶️")
        await message.add_reaction("❌")

        def check(reaction, user_reacting):
            return (
                user_reacting == ctx.author
                and reaction.message.id == message.id
                and str(reaction.emoji) in ["◀️", "▶️", "❌"]
            )

        while True:
            try:
                reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if str(reaction.emoji) == "▶️":
                    current = (current + 1) % len(pages)
                    await message.edit(embed=pages[current])
                elif str(reaction.emoji) == "◀️":
                    current = (current - 1) % len(pages)
                    await message.edit(embed=pages[current])
                elif str(reaction.emoji) == "❌":
                    await message.delete()
                    break

                await message.remove_reaction(reaction, ctx.author)

            except TimeoutError:
                break

    def paginate_logs(self, logs, user):
        pages = []
        type_emojis = {"warn": "⚠️", "kick": "👢", "ban": "🔨"}

        per_page = 5
        for i in range(0, len(logs), per_page):
            chunk = logs[i:i + per_page]
            embed = discord.Embed(
                title=f"Mod Logs for {user}",
                color=discord.Color.red()
            )

            for log in chunk:
                ts = log.get("timestamp")
                try:
                    dt = datetime.fromisoformat(ts)
                    timestamp_str = dt.strftime("%Y-%m-%d %H:%M")
                except Exception:
                    timestamp_str = ts

                emoji = type_emojis.get(log["type"], "📄")
                embed.add_field(
                    name=f"{emoji} {log['type'].upper()} — {log['guild_name']}",
                    value=(
                        f"**Reason:** {log['reason']}\n"
                        f"**By:** {log['mod_name']}\n"
                        f"**At:** {timestamp_str}"
                    ),
                    inline=False
                )

            pages.append(embed)

        return pages

    @fetch.error
    async def fetch_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 You need the **Manage Messages** permission to use this command.")
