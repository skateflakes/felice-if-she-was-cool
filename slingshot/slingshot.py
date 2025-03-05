import discord
from redbot.core import commands
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import os

class Screenshot(commands.Cog):
    """A cog for taking website screenshots."""

    def __init__(self, bot):
        self.bot = bot
        self.width = 525
        self.height = 814
        self.url = "https://htfslingshot.endersfund.com/htf_slingshot/web/sidebar/weekly"

    async def take_screenshot(self, path: str):
        options = Options()
        options.add_argument("--headless")
        options.add_argument(f"--window-size={self.width},{self.height}")
        
        chromedriver_autoinstaller.install()  # chromedriver thing idk
        driver = webdriver.Chrome(options=options)
        driver.get(self.url)
        driver.execute_script("document.body.style.zoom='175%'")  # zoooooooooooom
        driver.set_window_size(self.width, self.height)  # resize Real
        driver.execute_script("document.body.style.overflow = 'hidden';")  # hide scrollbar
        driver.save_screenshot(path)
        driver.quit()

    @commands.command()
    async def slingshot(self, ctx):
        """Takes a screenshot of the predefined website at a fixed size."""
        filename = "DeadeyeDerbyLeaderboard.png"
        await self.take_screenshot(filename)
        await ctx.send(file=discord.File(filename))
        os.remove(filename)

from redbot.core.bot import Red

def setup(bot: Red):  # Remove async from setup
    bot.add_cog(Screenshot(bot))
