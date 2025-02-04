import discord
from redbot.core import commands
from playwright.async_api import async_playwright
import os

class Screenshot(commands.Cog):
    """A cog for taking website screenshots."""

    def __init__(self, bot):
        self.bot = bot
        self.width = 1280
        self.height = 720

    async def take_screenshot(self, url: str, path: str):
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await page.set_viewport_size({"width": self.width, "height": self.height})
            await page.goto(url, wait_until="load")
            await page.screenshot(path=path)
            await browser.close()

    @commands.command()
    async def screenshot(self, ctx, url: str):
        """Takes a screenshot of a website at a fixed size."""
        filename = "screenshot.png"
        await self.take_screenshot(url, filename)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)

async def setup(bot):
    await bot.add_cog(Screenshot(bot))
