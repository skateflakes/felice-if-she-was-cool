import asyncpraw

async def get_reddit_instance(bot):
    tokens = await bot.get_shared_api_tokens("reddit")

    client_id = tokens.get("client_id")
    client_secret = tokens.get("client_secret")
    username = tokens.get("username")
    password = tokens.get("password")

    if not all([client_id, client_secret, username, password]):
        raise ValueError("Missing Reddit API credentials. Use [p]set api reddit ...")

    reddit = asyncpraw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
        user_agent=f"HTFBot Discord moderation cog (by u/{username})"
    )
    return reddit
