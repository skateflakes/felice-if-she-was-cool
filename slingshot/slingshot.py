import discord
from redbot.core import commands
from playwright.async_api import async_playwright
import os

class Screenshot(commands.Cog):
    """A cog for taking website screenshots."""

    def __init__(self, bot):
        self.bot = bot
        self.width = 300
        self.height = 454
        self.url = "https://htfslingshot.endersfund.com/htf_slingshot/web/sidebar/weekly"

    async def take_screenshot(self, path: str):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_viewport_size({"width": self.width, "height": self.height})
            await page.goto(self.url, wait_until="load")
            await page.screenshot(path=path)
            await browser.close()

    @commands.command()
    async def slingshot(self, ctx):
        """Takes a screenshot of the predefined website at a fixed size."""
        filename = "screenshot.png"
        await self.take_screenshot(filename)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)

def setup(bot):  # Remove async from setup
    bot.add_cog(Screenshot(bot))
