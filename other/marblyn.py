from redbot.core import commands
import discord

class Marblyn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if "marblyn" in message.content.lower():
            user_id = 257596407911940097
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)

            if user:
                try:
                    await user.send(
                        f'"marblyn"\n{message.channel.mention}\n{message.content}'
                    )
                except discord.Forbidden:
                    pass  # Cannot DM user
