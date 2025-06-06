import aiohttp
import logging
from redbot.core import commands
from redbot.core.utils.api_tunnel import get_shared_api_tokens

log = logging.getLogger("red.felice.wikia.api")

class FandomAPI:
    def __init__(self):
        self.base_url = "https://happytreefriends.fandom.com/api.php"
        self.username = None
        self.password = None
        self.session = None
        self.token = None

    async def login(self):
        tokens = await get_shared_api_tokens("htfwiki")
        self.username = tokens.get("username")
        self.password = tokens.get("password")

        if not self.username or not self.password:
            raise RuntimeError("Fandom username and password must be set with: [p]set api htfwiki username password")

        self.session = aiohttp.ClientSession()

        # Get login token
        async with self.session.get(self.base_url, params={
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }) as resp:
            result = await resp.json()
            login_token = result["query"]["tokens"]["logintoken"]

        # Perform login
        async with self.session.post(self.base_url, data={
            "action": "login",
            "lgname": self.username,
            "lgpassword": self.password,
            "lgtoken": login_token,
            "format": "json"
        }) as resp:
            login_result = await resp.json()
            if login_result.get("login", {}).get("result") != "Success":
                raise RuntimeError(f"Fandom login failed: {login_result}")

        # Get CSRF token
        async with self.session.get(self.base_url, params={
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }) as resp:
            result = await resp.json()
            self.token = result["query"]["tokens"]["csrftoken"]

    async def get_recent_changes(self):
        if not self.session:
            log.error("HTTP session not initialized. Did you forget to login?")
            return []

        params = {
            "action": "query",
            "list": "recentchanges",
            "rcprop": "title|ids|user|comment|flags",
            "rclimit": 10,
            "format": "json"
        }

        async with self.session.get(self.base_url, params=params) as resp:
            try:
                data = await resp.json()
            except Exception as e:
                log.exception("Failed to parse JSON from recentchanges: %s", e)
                return []

            if "query" not in data or "recentchanges" not in data["query"]:
                log.warning("Unexpected recentchanges response: %s", data)
                return []

            return data["query"]["recentchanges"]

    async def get_revision_content(self, rev_id: int) -> str:
        if not self.session:
            log.error("Session not initialized for get_revision_content")
            return ""

        params = {
            "action": "query",
            "prop": "revisions",
            "revids": rev_id,
            "rvprop": "content",
            "format": "json"
        }
        async with self.session.get(self.base_url, params=params) as resp:
            data = await resp.json()
            try:
                pages = data["query"]["pages"]
                for page_data in pages.values():
                    revisions = page_data.get("revisions")
                    if revisions:
                        return revisions[0].get("*", "") or revisions[0].get("slots", {}).get("main", {}).get("*", "")
            except KeyError:
                log.warning("Missing 'pages' in revision content response: %s", data)
            return ""

    async def block_user(self, user: str, expiry: str, reason: str) -> bool:
        if not self.token:
            log.warning("No CSRF token for blocking.")
            return False

        params = {
            "action": "block",
            "user": user,
            "expiry": expiry,
            "reason": reason,
            "nocreate": True,
            "autoblock": True,
            "allowusertalk": False,
            "reblock": True,
            "format": "json",
            "token": self.token
        }
        async with self.session.post(self.base_url, data=params) as resp:
            data = await resp.json()
            if "error" in data:
                log.warning("Failed to block user: %s", data["error"])
                return False
            return True

    async def unblock_user(self, user: str, reason: str) -> bool:
        if not self.token:
            log.warning("No CSRF token for unblocking.")
            return False

        params = {
            "action": "unblock",
            "user": user,
            "reason": reason,
            "format": "json",
            "token": self.token
        }
        async with self.session.post(self.base_url, data=params) as resp:
            data = await resp.json()
            if "error" in data:
                log.warning("Failed to unblock user: %s", data["error"])
                return False
            return True

    async def post_message_wall(self, user: str, reason: str):
        if not self.token:
            log.warning("No CSRF token for message wall.")
            return

        params = {
            "action": "edit",
            "title": f"Message_Wall:{user}",
            "section": "new",
            "summary": "Block notice",
            "text": f"You have been blocked. Reason: {reason}",
            "token": self.token,
            "format": "json"
        }
        async with self.session.post(self.base_url, data=params) as resp:
            await resp.json()
