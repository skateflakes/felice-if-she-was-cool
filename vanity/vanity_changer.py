import discord
from redbot.core import commands
import asyncio

class VanityChanger(commands.Cog):
    """A cog to change the server vanity URL every 5 seconds."""

    def __init__(self, bot):
        self.bot = bot
        self.vanity_options = []  # List of vanity URLs to cycle through
        self.task = None

    @commands.command()
    @commands.admin_or_permissions(manage_guild=True)
    async def set_vanities(self, ctx, *vanities: str):
        """Set the list of vanity URLs to cycle through."""
        if not vanities:
            return await ctx.send("Please provide at least one vanity URL.")
        
        self.vanity_options = list(vanities)
        await ctx.send(f"Vanity URLs set: {', '.join(self.vanity_options)}")

    @commands.command()
    @commands.admin_or_permissions(manage_guild=True)
    async def start_vanity_cycle(self, ctx):
        """Start changing the server vanity URL every 5 seconds."""
        if not self.vanity_options:
            return await ctx.send("Set vanity URLs first using `set_vanities`.")
        
        if self.task and not self.task.done():
            return await ctx.send("Vanity cycling is already running.")
        
        self.task = self.bot.loop.create_task(self.vanity_loop(ctx.guild))
        await ctx.send("Vanity URL cycling started.")

    async def vanity_loop(self, guild):
        while True:
            for vanity in self.vanity_options:
                try:
                    await guild.edit(vanity_url=vanity)
                    print(f"Vanity changed to: {vanity}")
                except discord.Forbidden:
                    print("Missing permissions to change vanity URL.")
                except discord.HTTPException as e:
                    print(f"Failed to change vanity: {e}")
                await asyncio.sleep(5)  # Wait 5 seconds before changing again

    @commands.command()
    @commands.admin_or_permissions(manage_guild=True)
    async def stop_vanity_cycle(self, ctx):
        """Stop changing the server vanity URL."""
        if self.task:
            self.task.cancel()
            self.task = None
            await ctx.send("Vanity URL cycling stopped.")
        else:
            await ctx.send("Vanity cycling is not running.")

async def setup(bot):
    await bot.add_cog(VanityChanger(bot))
