import discord
from discord.ext import commands
from discord import ui, app_commands
import os
import aiohttp
import io
from utils.embeds import create_main_embed

# نافذة إدخال البيانات (للحفاظ على التنسيق والأسطر)
class EmbedModal(ui.Modal, title="إرسال إمبيد منسق"):
    # خانة العنوان (سطر واحد)
    msg_title = ui.TextInput(label="العنوان (مثلاً: نيترو قيمنق)", placeholder="اكتب العنوان هنا...", required=True)
    # خانة التفاصيل (عدة أسطر - Paragraph)
    msg_details = ui.TextInput(
        label="التفاصيل (ستظهر عند ضغط الزر)",
        style=discord.TextStyle.paragraph,
        placeholder="انسخ النص المنسق هنا...",
        required=True,
        min_length=1
    )

    def __init__(self, cog_instance, target_channel):
        super().__init__()
        self.cog = cog_instance
        self.target_channel = target_channel

    async def on_submit(self, interaction: discord.Interaction):
        # الرد الأولي
        await interaction.response.send_message("✅ جاري معالجة الصور والنشر بالتنسيق المطلوب...", ephemeral=True)

        # النص المنسق (بيحتفظ بالأسطر هنا)
        details_text = self.msg_details.value
        title_text = self.msg_title.value
        
        description_text = f"اضغط على زر ( 📦 اظهار جميع التفاصيل : {title_text} )"
        
        # 1. إرسال الإمبيد العلوي
        main_embed = create_main_embed(title_text, description_text, self.cog.top_banner)
        view = DetailsView(details_text)
        await self.target_channel.send(embed=main_embed, view=view)

        # 2. إرسال البانر السفلي (عريض وكبير)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.cog.bottom_banner) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    file = discord.File(data, filename="banner.png")
                    await self.target_channel.send(file=file)

class DetailsView(ui.View):
    def __init__(self, details_content):
        super().__init__(timeout=None)
        self.details_content = details_content

    @ui.button(label="اظهار جميع التفاصيل 📦", style=discord.ButtonStyle.blurple, custom_id="show_details_btn")
    async def show_details(self, interaction: discord.Interaction, button: ui.Button):
        # هنا الرسالة هتظهر منسقة زي ما دخلتها في المودال
        await interaction.response.send_message(
            content=f"{self.details_content}", 
            ephemeral=True
        )

class Messenger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_target_id = int(os.getenv('TARGET_CHANNEL_ID'))
        self.top_banner = os.getenv('TOP_BANNER_URL')
        self.bottom_banner = os.getenv('BOTTOM_BANNER_URL')

    @app_commands.command(name="send_embed", description="فتح نافذة لإرسال إمبيد منسق")
    async def send_embed(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        target_channel = channel or self.bot.get_channel(self.default_target_id)
        if not target_channel:
            await interaction.response.send_message("❌ الروم غير موجود!", ephemeral=True)
            return

        # فتح النافذة المنبثقة (Modal)
        await interaction.response.send_modal(EmbedModal(self, target_channel))

async def setup(bot):
    await bot.add_cog(Messenger(bot))
