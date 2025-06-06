import aiohttp
import asyncio
from redbot.core import commands
from redbot.core import Config
from redbot.core.bot import Red
from discord.ext import tasks
import logging
from datetime import datetime, timedelta

log = logging.getLogger("red.felice.wikia")

class FandomAPI:
    def __init__(self, bot: Red):
        self.bot = bot
        self.base_url = "https://happytreefriends.fandom.com/api.php"
        self.session = None
        self.username = None
        self.password = None
        self.token = None

    async def login(self):
        tokens = await self.bot.get_shared_api_tokens("htfwiki")
        self.username = tokens.get("username")
        self.password = tokens.get("password")

        if not self.username or not self.password:
            raise RuntimeError("Missing username or password. Set them with `[p]set api htfwiki username password`.")

        self.session = aiohttp.ClientSession()

        # Step 1: Get login token
        async with self.session.get(self.base_url, params={
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }) as resp:
            data = await resp.json()
            login_token = data["query"]["tokens"]["logintoken"]

        # Step 2: Post login request
        async with self.session.post(self.base_url, data={
            "action": "login",
            "lgname": self.username,
            "lgpassword": self.password,
            "lgtoken": login_token,
            "format": "json"
        }) as resp:
            result = await resp.json()
            if result["login"]["result"] != "Success":
                raise RuntimeError("Fandom login failed: {}".format(result["login"]["result"]))

        # Step 3: Get CSRF token
        async with self.session.get(self.base_url, params={
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }) as resp:
            data = await resp.json()
            self.token = data["query"]["tokens"]["csrftoken"]

    async def get_recent_changes(self):
        now = datetime.utcnow()
        start = (now - timedelta(minutes=2)).isoformat() + "Z"
        params = {
            "action": "query",
            "format": "json",
            "list": "recentchanges",
            "rcprop": "title|ids|user|comment|flags|timestamp",
            "rcstart": start,
            "rclimit": 10,
            "rcdir": "newer"
        }
        async with self.session.get(self.base_url, params=params) as resp:
            data = await resp.json()
            if data is None or "query" not in data:
                return []
            return data["query"]["recentchanges"]

class HTFWikia(commands.Cog):
    def __init__(self, bot: Red):
        self.bot = bot
        self.api = FandomAPI(bot)
        self.edit_channel_id = 1379623956889337906
        self.report_channel_id = 1379672967256080397
        self.session = aiohttp.ClientSession()
        self.edit_monitor.start()

    def cog_unload(self):
        self.edit_monitor.cancel()
        asyncio.create_task(self.session.close())

    @tasks.loop(seconds=60)
    async def edit_monitor(self):
        try:
            if self.api.session is None:
                await self.api.login()

            changes = await self.api.get_recent_changes()
            if not changes:
                return

            edit_channel = self.bot.get_channel(self.edit_channel_id)
            report_channel = self.bot.get_channel(self.report_channel_id)
            if not edit_channel:
                return

            for change in changes:
                msg = f"**Edit:** [[{change['title']}]] by `{change['user']}`\nComment: {change.get('comment', 'No comment')}\n<https://happytreefriends.fandom.com/wiki/{change['title'].replace(' ', '_')}>"
                await edit_channel.send(msg)

                if "{{Delete" in change.get("comment", "") and report_channel:
                    await report_channel.send(f"⚠️ **Delete template used:** [[{change['title']}]] by `{change['user']}`\n<https://happytreefriends.fandom.com/wiki/{change['title'].replace(' ', '_')}>")

        except Exception as e:
            log.exception("Failed to poll recent changes: %s", e)

    @edit_monitor.before_loop
    async def before_edit_monitor(self):
        await self.bot.wait_until_ready()

async def setup(bot: Red):
    await bot.add_cog(HTFWikia(bot))
