import aiohttp
import logging

log = logging.getLogger("red.felice.wikia")

class FandomAPI:
    def __init__(self):
        self.base_url = "https://happytreefriends.fandom.com"
        self.api_url = f"{self.base_url}/api.php"
        self.session = aiohttp.ClientSession()
        self.logged_in = False
        self.csrf_token = None
        self.cookies = None

    async def login(self, bot):
        creds = await bot.get_shared_api_tokens("fandom")
        username = creds.get("username")
        password = creds.get("password")

        if not username or not password:
            log.error("Missing Fandom API credentials. Use `[p]set api fandom username password`.")
            return False

        async with self.session.get(self.api_url, params={
            "action": "query",
            "meta": "tokens",
            "type": "login",
            "format": "json"
        }) as r:
            login_token = (await r.json())["query"]["tokens"]["logintoken"]

        payload = {
            "action": "login",
            "lgname": username,
            "lgpassword": password,
            "lgtoken": login_token,
            "format": "json"
        }
        async with self.session.post(self.api_url, data=payload) as r:
            res = await r.json()
            if res["login"]["result"] != "Success":
                log.error(f"Fandom login failed: {res}")
                return False
            self.cookies = r.cookies

        async with self.session.get(self.api_url, params={
            "action": "query",
            "meta": "tokens",
            "format": "json"
        }, cookies=self.cookies) as r:
            self.csrf_token = (await r.json())["query"]["tokens"]["csrftoken"]

        self.logged_in = True
        log.info("Successfully logged in to Fandom")
        return True

    async def get_recent_changes(self):
        async with self.session.get(self.api_url, params={
            "action": "query",
            "list": "recentchanges",
            "rcprop": "title|ids|sizes|flags|user|comment|timestamp",
            "rclimit": "10",
            "format": "json"
        }) as r:
            data = await r.json()
            return data["query"]["recentchanges"]

    async def get_revision_content(self, revid):
        async with self.session.get(self.api_url, params={
            "action": "query",
            "prop": "revisions",
            "revids": revid,
            "rvprop": "content",
            "format": "json"
        }) as r:
            data = await r.json()
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                revisions = page.get("revisions", [])
                if revisions:
                    return revisions[0].get("*", "")
        return ""

    async def block_user(self, username: str, expiry: str, reason: str):
        if not self.logged_in:
            return False
        payload = {
            "action": "block",
            "user": username,
            "expiry": expiry,
            "reason": reason,
            "nocreate": 1,
            "autoblock": 1,
            "reblock": 1,
            "anononly": 0,
            "allowusertalk": 1,
            "format": "json",
            "token": self.csrf_token
        }
        async with self.session.post(self.api_url, data=payload, cookies=self.cookies) as r:
            res = await r.json()
            if "block" in res:
                await self.post_wall_message(username, f"You have been blocked. Reason: {reason}")
                return True
            log.warning(f"Failed to block user {username}: {res}")
            return False

    async def unblock_user(self, username: str, reason: str):
        if not self.logged_in:
            return False
        payload = {
            "action": "unblock",
            "user": username,
            "reason": reason,
            "format": "json",
            "token": self.csrf_token
        }
        async with self.session.post(self.api_url, data=payload, cookies=self.cookies) as r:
            res = await r.json()
            if "unblock" in res:
                await self.post_wall_message(username, f"You have been unblocked. Reason: {reason}")
                return True
            log.warning(f"Failed to unblock user {username}: {res}")
            return False

    async def post_wall_message(self, username: str, message: str):
        title = "Block Notice"
        page = f"Message_Wall:{username.replace(' ', '_')}"
        text = message
        payload = {
            "action": "edit",
            "title": page,
            "text": text,
            "summary": "Automated block notice",
            "format": "json",
            "token": self.csrf_token
        }
        async with self.session.post(self.api_url, data=payload, cookies=self.cookies) as r:
            res = await r.json()
            return "edit" in res
