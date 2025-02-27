import discord
from redbot.core import commands
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

class Screenshot(commands.Cog):
    """A cog for taking website screenshots."""

    def __init__(self, bot):
        self.bot = bot
        self.width = 300
        self.height = 454
        self.url = "https://htfslingshot.endersfund.com/htf_slingshot/web/sidebar/weekly"

    async def take_screenshot(self, path: str):
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--window-size={self.width},{self.height}")
        
        service = Service("chromedriver")  # Ensure chromedriver is installed
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        driver.save_screenshot(path)
        driver.quit()

    @commands.command()
    async def slingshot(self, ctx):
        """Takes a screenshot of the predefined website at a fixed size."""
        filename = "screenshot.png"
        await self.take_screenshot(filename)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)

def setup(bot):  # Remove async from setup
    bot.add_cog(Screenshot(bot))
