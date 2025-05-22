import discord
from redbot.core import commands, app_commands
from redbot.core.bot import Red
from PIL import Image, ImageDraw, ImageFont
import os
import io
from typing import List

IMAGE_FOLDER = "./memes/images/"
DEFAULT_FONT_SIZE = 40
FONT_PATH = "/usr/share/fonts/truetype/impact.ttf"  # Update path if needed

class MemeMaker(commands.Cog):
    """Make classic memes with top and bottom text."""

    def __init__(self, bot: Red):
        self.bot = bot

    # --- Slash Command: Make Meme ---
    @app_commands.command(name="makememe", description="Create a meme with optional top and bottom text")
    @app_commands.describe(
        image="Image filename (from the memes/images folder)",
        text="Text: first line is top, second line (optional) is bottom",
        font_size="Font size (default: 40)"
    )
    async def makememe(
        self,
        interaction: discord.Interaction,
        image: str,
        text: str,
        font_size: int = DEFAULT_FONT_SIZE,
    ):
        image_path = os.path.join(IMAGE_FOLDER, image)

        if not os.path.isfile(image_path):
            await interaction.response.send_message("Image not found.", ephemeral=True)
            return

        # Split input into top and optional bottom
        lines = text.split("\n", 1)
        top_text = lines[0]
        bottom_text = lines[1] if len(lines) > 1 else ""

        try:
            img = Image.open(image_path).convert("RGB")
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(FONT_PATH, font_size)

            def draw_centered_text(text, y_pos):
                w, h = draw.textsize(text, font=font)
                draw.text(
                    ((img.width - w) / 2, y_pos),
                    text,
                    font=font,
                    fill="white",
                    stroke_width=2,
                    stroke_fill="black",
                )

            draw_centered_text(top_text.upper(), 10)
            if bottom_text:
                draw_centered_text(bottom_text.upper(), img.height - font_size - 10)

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)

            file = discord.File(fp=buf, filename="meme.png")
            await interaction.response.send_message(file=file)
        except Exception as e:
            await interaction.response.send_message(f"Failed to generate meme: {e}", ephemeral=True)

    # --- Prefix Command: List Images ---
    @commands.command(name="memelist")
    async def memelist(self, ctx: commands.Context):
        """List available meme images (paginated)."""
        files = [f for f in os.listdir(IMAGE_FOLDER) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
        if not files:
            await ctx.send("No meme images found.")
            return

        pages = [files[i:i + 4] for i in range(0, len(files), 4)]
        current_page = 0

        async def send_page(page_index: int):
            embed = discord.Embed(
                title=f"Meme Images (Page {page_index + 1}/{len(pages)})",
                description="\n".join(f"• `{name}`" for name in pages[page_index]),
                color=discord.Color.blurple()
            )
            view = MemeListView(pages, send_page, page_index)
            await ctx.send(embed=embed, view=view)

        await send_page(current_page)

class MemeListView(discord.ui.View):
    def __init__(self, pages: List[List[str]], callback, current_page: int = 0):
        super().__init__(timeout=60)
        self.pages = pages
        self.callback = callback
        self.current_page = current_page

        self.prev_button.disabled = self.current_page == 0
        self.next_button.disabled = self.current_page >= len(pages) - 1

    @discord.ui.button(label="⬅ Prev", style=discord.ButtonStyle.secondary)
    async def prev_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page -= 1
        await interaction.response.defer()
        await interaction.message.delete()
        await self.callback(self.current_page)

    @discord.ui.button(label="Next ➡", style=discord.ButtonStyle.secondary)
    async def next_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.current_page += 1
        await interaction.response.defer()
        await interaction.message.delete()
        await self.callback(self.current_page)

async def setup(bot: Red):
    await bot.add_cog(MemeMaker(bot))
