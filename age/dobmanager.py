import discord
from redbot.core import commands, Config
import asyncio
from datetime import datetime, timedelta

class DOBManager(commands.Cog):
    """Manage DOBs and ban users who are too young."""

    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890123456789)
        default_guild = {"minimum_age": 13}
        default_user = {"dob": None}
        self.config.register_guild(**default_guild)
        self.config.register_user(**default_user)

        self.bot.loop.create_task(self.check_birthdays())

    async def check_birthdays(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            now = datetime.utcnow()

            for guild in self.bot.guilds:
                min_age = await self.config.guild(guild).minimum_age()
                for ban_entry in await guild.bans():
                    user = ban_entry.user
                    dob = await self.config.user(user).dob()
                    if dob:
                        birth_date = datetime.strptime(dob, "%m/%d/%Y")
                        age = self.calculate_age(birth_date)

                        if age >= min_age:
                            try:
                                await guild.unban(user, reason="Now eligible to use Discord and can join this server!")
                            except discord.Forbidden:
                                pass
                            except discord.HTTPException:
                                pass

            await asyncio.sleep(86400)  # Check every 24 hours

    def calculate_age(self, birth_date):
        today = datetime.utcnow()
        return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

    @commands.Cog.listener()
    async def on_member_join(self, member):
        # Check if we already have DOB
        dob = await self.config.user(member).dob()
        if dob:
            return  # Already verified

        try:
            await member.send("Please reply with your **date of birth** in `MM/DD/YYYY` format. (Example: `04/26/2006`) This is required to verify your age.")
        except discord.Forbidden:
            return  # Can't DM user

        def check(m):
            return m.author == member and isinstance(m.channel, discord.DMChannel)

        try:
            msg = await self.bot.wait_for("message", timeout=300, check=check)
            birth_date = datetime.strptime(msg.content.strip(), "%m/%d/%Y")
        except (asyncio.TimeoutError, ValueError):
            return  # Ignore timeout or bad format

        await self.config.user(member).dob.set(birth_date.strftime("%m/%d/%Y"))
        await member.send("✅ Thanks! Your date of birth has been saved.")

        await self.evaluate_member(member)

    async def evaluate_member(self, member):
        dob = await self.config.user(member).dob()
        if not dob:
            return

        birth_date = datetime.strptime(dob, "%m/%d/%Y")
        age = self.calculate_age(birth_date)

        if age < 13:
            # Under Discord ToS, bansync across all guilds
            for guild in self.bot.guilds:
                if guild.get_member(member.id):
                    if guild.me.guild_permissions.ban_members:
                        try:
                            await guild.ban(member, reason="Breaking Discord's Terms of Service; underage (BanSync)")
                        except Exception:
                            pass
        else:
            # Otherwise, check server-specific min ages
            for guild in self.bot.guilds:
                if guild.get_member(member.id):
                    min_age = await self.config.guild(guild).minimum_age()
                    if age < min_age:
                        if guild.me.guild_permissions.ban_members:
                            try:
                                await guild.ban(member, reason=f"Too young for this server (Minimum age: {min_age})")
                            except Exception:
                                pass

    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.command()
    async def setminage(self, ctx, age: int):
        """Set the minimum age for this server."""
        if age < 13:
            await ctx.send("🚫 Minimum age cannot be set below 13.")
            return
        await self.config.guild(ctx.guild).minimum_age.set(age)
        await ctx.send(f"✅ Minimum age for **{ctx.guild.name}** set to **{age}** years old.")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def setdob(self, ctx, user: discord.User, dob: str):
        """Set or correct a user's date of birth manually."""
        try:
            datetime.strptime(dob, "%m/%d/%Y")
        except ValueError:
            await ctx.send("🚫 Invalid date format. Use `MM/DD/YYYY`.")
            return

        await self.config.user(user).dob.set(dob)
        await ctx.send(f"✅ Date of birth for `{user}` set to {dob}.")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def checkdob(self, ctx, user: discord.User):
        """Check a user's saved date of birth."""
        dob = await self.config.user(user).dob()
        if not dob:
            await ctx.send("❌ No date of birth saved for this user.")
            return
        await ctx.send(f"📅 `{user}`'s date of birth: **{dob}**")

    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.command()
    async def forcerequest(self, ctx, user: discord.User):
        """Force re-request DOB via DM."""
        try:
            await user.send("👋 Hi! Please reply with your **date of birth** in `MM/DD/YYYY` format.")
        except discord.Forbidden:
            await ctx.send("❌ Couldn't send DM to this user.")
            return
        await ctx.send(f"✅ Forced DOB request sent to `{user}`.")


async def setup(bot):
    await bot.add_cog(DOBManager(bot))
