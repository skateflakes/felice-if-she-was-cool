import asyncpraw
from redbot.core import commands

async def get_reddit_instance(bot):
    client_id = await bot.get_shared_api_tokens("reddit").get("client_id")
    client_secret = await bot.get_shared_api_tokens("reddit").get("client_secret")
    username = await bot.get_shared_api_tokens("reddit").get("username")
    password = await bot.get_shared_api_tokens("reddit").get("password")

    if not all([client_id, client_secret, username, password]):
        raise ValueError("Missing Reddit API credentials. Use [p]set api reddit ...")

    reddit = asyncpraw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent="HTFBot Discord moderation cog (by u/{})".format(username)
    )
    return reddit
