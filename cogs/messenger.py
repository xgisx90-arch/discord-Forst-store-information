import discord
from discord.ext import commands
from discord import ui, app_commands
import os
import aiohttp
import io
from utils.embeds import create_main_embed


class DetailsView(ui.View):
    def __init__(self, details_content):
        super().__init__(timeout=None)
        self.details_content = details_content

    @ui.button(label="اظهار جميع التفاصيل 📦", style=discord.ButtonStyle.blurple, custom_id="show_details_btn")
    async def show_details(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            content=f"**التفاصيل كاملة:**\n\n{self.details_content}",
            ephemeral=True
        )


class Messenger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_target_id = int(os.getenv('TARGET_CHANNEL_ID'))
        self.top_banner = os.getenv('TOP_BANNER_URL')
        self.bottom_banner = os.getenv('BOTTOM_BANNER_URL')

    @app_commands.command(name="send_embed", description="إرسال إمبيد مع نص ديناميكي وبانر عريض")
    @app_commands.describe(title="العنوان (مثلاً: نيترو)", details="النص المخفي", channel="الروم المستهدف")
    async def send_embed(self, interaction: discord.Interaction, title: str, details: str,
                         channel: discord.TextChannel = None):
        target_channel = channel or self.bot.get_channel(self.default_target_id)

        if not target_channel:
            await interaction.response.send_message("❌ الروم غير موجود!", ephemeral=True)
            return

        await interaction.response.send_message("✅ جاري النشر بالتعديلات الجديدة...", ephemeral=True)

        # التعديل هنا: دمج العنوان (title) داخل جملة الوصف
        description_text = f"اضغط على زر ( 📦 اظهار جميع التفاصيل : {title} )"

        # 1. إرسال الإمبيد العلوي
        main_embed = create_main_embed(title, description_text, self.top_banner)
        view = DetailsView(details)
        await target_channel.send(embed=main_embed, view=view)

        # 2. إرسال البانر السفلي كملف (لضمان الحجم الكبير والعريض)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.bottom_banner) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    file = discord.File(data, filename="bottom_banner.png")
                    await target_channel.send(file=file)
                else:
                    await target_channel.send(content=self.bottom_banner)


async def setup(bot):
    await bot.add_cog(Messenger(bot))