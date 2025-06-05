import aiohttp
import asyncio
from redbot.core.bot import Red
import logging

log = logging.getLogger("red.felice.htfwiki")

class FandomAPI:
    def __init__(self):
        self.session = None
        self.bot: Red = None
        self.base_url = "https://happytreefriends.fandom.com/api.php"
        self.token = ""
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

    async def login(self, bot: Red):
        self.bot = bot
        tokens = await bot.get_shared_api_tokens("wiki")
        username = tokens.get("username")
        password = tokens.get("password")  # ← back to 'password'

        if not all([username, password]):
            log.error("Fandom API credentials (username/password) are not set.")
            return

        self.session = aiohttp.ClientSession()

        # Get login token
        async with self.session.get(f"{self.base_url}?action=query&meta=tokens&type=login&format=json") as resp:
            data = await resp.json()
            login_token = data["query"]["tokens"]["logintoken"]

        # Log in
        payload = {
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": login_token,
            "format": "json"
        }

        async with self.session.post(self.base_url, data=payload, headers=self.headers) as resp:
            login_result = await resp.json()
            log.info(f"Login result: {login_result}")

        # Get CSRF token
        async with self.session.get(f"{self.base_url}?action=query&meta=tokens&format=json") as resp:
            data = await resp.json()
            self.token = data["query"]["tokens"]["csrftoken"]

    async def get_recent_changes(self):
        params = {
            "action": "query",
            "format": "json",
            "list": "recentchanges",
            "rcprop": "title|ids|sizes|flags|user|comment",
            "rclimit": "20",
        }
        async with self.session.get(self.base_url, params=params) as resp:
            data = await resp.json()
            return data.get("query", {}).get("recentchanges", [])

    async def get_revision_content(self, revid: int):
        params = {
            "action": "query",
            "format": "json",
            "prop": "revisions",
            "revids": revid,
            "rvprop": "content"
        }
        async with self.session.get(self.base_url, params=params) as resp:
            data = await resp.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                revisions = page.get("revisions", [])
                if revisions:
                    return revisions[0].get("*", "")
            return ""

    async def block_user(self, user: str, duration: str, reason: str) -> bool:
        payload = {
            "action": "block",
            "user": user,
            "expiry": duration,
            "reason": reason,
            "nocreate": True,
            "autoblock": True,
            "allowusertalk": False,
            "reblock": True,
            "token": self.token,
            "format": "json"
        }
        async with self.session.post(self.base_url, data=payload, headers=self.headers) as resp:
            result = await resp.json()
            success = "block" in result
            if success:
                await self.send_wall_message(user, reason)
            return success

    async def unblock_user(self, user: str, reason: str) -> bool:
        payload = {
            "action": "unblock",
            "user": user,
            "reason": reason,
            "token": self.token,
            "format": "json"
        }
        async with self.session.post(self.base_url, data=payload, headers=self.headers) as resp:
            result = await resp.json()
            return "unblock" in result

    async def send_wall_message(self, user: str, reason: str):
        title = f"Message_Wall:{user}"
        payload = {
            "action": "edit",
            "title": title,
            "section": "new",
            "summary": "Block notification",
            "text": f"You have been blocked. Reason: {reason}",
            "token": self.token,
            "format": "json"
        }
        async with self.session.post(self.base_url, data=payload, headers=self.headers) as resp:
            await resp.json()
