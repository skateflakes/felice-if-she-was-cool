import discord
from redbot.core import commands

class ServerRules(commands.Cog):
    """A cog for managing server rules with sections for warnings, mutes, and bans."""

    def __init__(self, bot):
        self.bot = bot
        self.rules = {
            "A": [],  # Warnings
            "B": [],  # Mutes
            "C": []   # Bans
        }

    @commands.command()
    async def add_rule(self, ctx, section: str, *, rule: str):
        """Add a rule to a specific section (A: Warnings, B: Mutes, C: Bans)."""
        section = section.upper()
        if section in self.rules:
            self.rules[section].append(rule)
            await ctx.send(f"# Rule added to Section {section}: {rule}")
        else:
            await ctx.send("Invalid section. Use A (Warnings), B (Mutes), or C (Bans).")

    @commands.command()
    async def edit_rule(self, ctx, section: str, index: int, *, new_rule: str):
        """Edit a rule in a specific section by index."""
        section = section.upper()
        if section in self.rules and 0 <= index < len(self.rules[section]):
            old_rule = self.rules[section][index]
            self.rules[section][index] = new_rule
            await ctx.send(f"Rule updated in Section {section}:
Old: {old_rule}
New: {new_rule}")
        else:
            await ctx.send("Invalid section or index.")

    @commands.command()
    async def remove_rule(self, ctx, section: str, index: int):
        """Remove a rule from a specific section by index."""
        section = section.upper()
        if section in self.rules and 0 <= index < len(self.rules[section]):
            removed_rule = self.rules[section].pop(index)
            await ctx.send(f"Rule removed from Section {section}: {removed_rule}")
        else:
            await ctx.send("Invalid section or index.")(self, ctx, section: str, *, rule: str):
        """Add a rule to a specific section (A: Warnings, B: Mutes, C: Bans)."""
        section = section.upper()
        if section in self.rules:
            self.rules[section].append(rule)
            await ctx.send(f"# Rule added to Section {section}: {rule}")
        else:
            await ctx.send("Invalid section. Use A (Warnings), B (Mutes), or C (Bans).")

    @commands.command()
    async def search_rule(self, ctx, *, keyword: str):
        """Search for a rule containing a keyword across all sections."""
        results = []
        for section, rules in self.rules.items():
            for rule in rules:
                if keyword.lower() in rule.lower():
                    results.append(f"Section {section}: {rule}")
        if results:
            await ctx.send("Please read the rules: https://docs.google.com/document/d/e/2PACX-1vTvMfTZy24lQihE9J6MV1Jh2hoHCRzpqx3nM73goqhHP8ydlerWNdfSvx0ag-X0XUddfHD0cvE8AIs5/pub")
            await ctx.send("\n".join(results))
        else:
            await ctx.send("No rules found with that keyword.")

    @commands.command()
    async def list_rules(self, ctx, section: str = None):
        """List all rules or rules from a specific section."""
        if section:
            section = section.upper()
            if section in self.rules:
                rules = self.rules[section]
                if rules:
                    await ctx.send(f"Rules in Section {section}:\n" + "\n".join(rules))
                else:
                    await ctx.send(f"No rules in Section {section}.")
            else:
                await ctx.send("Invalid section. Use A (Warnings), B (Mutes), or C (Bans).")
        else:
            all_rules = "\n".join([f"Section {s}:\n" + "\n".join(r) for s, r in self.rules.items() if r])
            await ctx.send(all_rules if all_rules else "No rules have been added yet.")

async def setup(bot):
    await bot.add_cog(ServerRules(bot))
