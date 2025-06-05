import aiohttp
import logging
from urllib.parse import urlencode

log = logging.getLogger("red.felice.wikia.api")

class FandomAPI:
    def __init__(self):
        self.session: aiohttp.ClientSession | None = None
        self.base_url = "https://happytreefriends.fandom.com/api.php"
        self.cookies = None
        self.token = None
        self.username = None
        self.password = None

    async def login(self, bot):
        # Load credentials using Red's API key system
        keys = await bot.get_shared_api_tokens("htfwiki")
        self.username = keys.get("username")
        self.password = keys.get("password")

        if not self.username or not self.password:
            log.error("Fandom username or password not set via [p]set api htfwiki username password")
            return

        self.session = aiohttp.ClientSession()
        login_token = await self.get_login_token()
        if not login_token:
            log.error("Failed to get login token.")
            return

        payload = {
            "action": "clientlogin",
            "username": self.username,
            "password": self.password,
            "loginreturnurl": "https://happytreefriends.fandom.com/",
            "logintoken": login_token,
            "format": "json"
        }

        async with self.session.post(self.base_url, data=payload) as resp:
            data = await resp.json()
            if data.get("clientlogin", {}).get("status") != "PASS":
                log.error("Login failed: %s", data)
            else:
                log.info("Successfully logged in as %s", self.username)

        self.token = await self.get_csrf_token()

    async def get_login_token(self):
        async with self.session.get(self.base_url, params={
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }) as resp:
            data = await resp.json()
            return data["query"]["tokens"]["logintoken"]

    async def get_csrf_token(self):
        async with self.session.get(self.base_url, params={
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }) as resp:
            data = await resp.json()
            return data["query"]["tokens"]["csrftoken"]

    async def get_recent_changes(self):
        if self.session is None:
            raise RuntimeError("Session not initialized. Call login() first.")

        params = {
            "action": "query",
            "list": "recentchanges",
            "rcprop": "title|ids|sizes|flags|user|comment",
            "rclimit": "10",
            "format": "json"
        }
        async with self.session.get(self.base_url, params=params) as resp:
            data = await resp.json()
            return data["query"]["recentchanges"]

    async def get_revision_content(self, revid: int):
        if self.session is None:
            raise RuntimeError("Session not initialized. Call login() first.")

        params = {
            "action": "query",
            "prop": "revisions",
            "revids": revid,
            "rvprop": "content",
            "format": "json"
        }
        async with self.session.get(self.base_url, params=params) as resp:
            data = await resp.json()
            pages = data["query"]["pages"]
            for page in pages.values():
                revisions = page.get("revisions", [])
                if revisions:
                    return revisions[0]["*"] if "*" in revisions[0] else revisions[0].get("slots", {}).get("main", {}).get("*", "")
        return ""

    async def block_user(self, user: str, duration: str, reason: str):
        if not self.token:
            log.warning("No CSRF token for blocking.")
            return False

        payload = {
            "action": "block",
            "user": user,
            "expiry": duration,
            "reason": reason,
            "nocreate": True,
            "autoblock": True,
            "allowusertalk": False,
            "reblock": True,
            "format": "json",
            "token": self.token
        }
        async with self.session.post(self.base_url, data=payload) as resp:
            data = await resp.json()
            if "error" in data:
                log.warning("Failed to block user: %s", data["error"])
                return False

        await self.post_to_wall(user, reason)
        return True

    async def unblock_user(self, user: str, reason: str):
        if not self.token:
            log.warning("No CSRF token for unblocking.")
            return False

        payload = {
            "action": "unblock",
            "user": user,
            "reason": reason,
            "format": "json",
            "token": self.token
        }
        async with self.session.post(self.base_url, data=payload) as resp:
            data = await resp.json()
            if "error" in data:
                log.warning("Failed to unblock user: %s", data["error"])
                return False
        return True

    async def post_to_wall(self, user: str, reason: str):
        if not self.token:
            return

        title = f"Message_Wall:{user}"
        content = f"== Block notice ==\nYou have been blocked. Reason: {reason}"
        payload = {
            "action": "edit",
            "title": title,
            "appendtext": content,
            "format": "json",
            "token": self.token
        }
        async with self.session.post(self.base_url, data=payload) as resp:
            data = await resp.json()
            if "error" in data:
                log.warning("Failed to post to user wall: %s", data["error"])
