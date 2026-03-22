import discord
from discord.ext import commands
from discord import ui, app_commands
import os
import aiohttp
import io
from utils.embeds import create_main_embed

# 1. المودال لجمع البيانات (5 خانات كحد أقصى)
class EmbedModal(ui.Modal, title="إرسال إمبيد المتجر بالأزرار"):
    msg_title = ui.TextInput(label="العنوان العلوي", placeholder="مثلاً: نيترو قيمنق", required=True)
    msg_details = ui.TextInput(
        label="التفاصيل",
        style=discord.TextStyle.paragraph,
        placeholder="انسخ النص المنسق هنا...",
        required=True
    )
    # خانات الروابط (اختيارية)
    link_shop = ui.TextInput(label="رابط الشراء/الموقع", placeholder="https://...", required=False)
    link_ticket = ui.TextInput(label="رابط التكت", placeholder="https://...", required=False)
    link_extra = ui.TextInput(label="رابط إضافي", placeholder="https://...", required=False)

    def __init__(self, cog_instance, target_channel):
        super().__init__()
        self.cog = cog_instance
        self.target_channel = target_channel

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ جاري معالجة الأزرار والنشر...", ephemeral=True)

        # تجهيز الروابط في قاموس (Dictionary) لتسهيل التعامل معها
        links_data = [
            {"label": "رابط الشراء 🛒", "url": self.link_shop.value},
            {"label": "فتح تكت 🎫", "url": self.link_ticket.value},
            {"label": "رابط إضافي 🔗", "url": self.link_extra.value}
        ]

        title_text = self.msg_title.value
        details_text = self.msg_details.value
        description_text = f"اضغط على زر ( 📦 اظهار جميع التفاصيل : {title_text} )"
        
        # إنشاء الإمبيد الرئيسي
        main_embed = create_main_embed(title_text, description_text, self.cog.top_banner)
        
        # إنشاء الـ View وإضافة أزرار الروابط له
        view = DetailsView(details_text, links_data)
        
        await self.target_channel.send(embed=main_embed, view=view)

        # إرسال البانر السفلي (عريض وكبير)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.cog.bottom_banner) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    file = discord.File(data, filename="banner.png")
                    await self.target_channel.send(file=file)

# 2. الـ View المسؤول عن عرض الزرار الأزرق وأزرار الروابط
class DetailsView(ui.View):
    def __init__(self, details_content, links_data):
        super().__init__(timeout=None)
        self.details_content = details_content

        # إضافة زر "إظهار التفاصيل" أولاً
        # ملاحظة: هذا الزر استجابة (Interaction)، أما الباقي فهي روابط (URL)
        
        # إضافة أزرار الروابط ديناميكياً إذا وُجدت
        for item in links_data:
            url = item["url"]
            if url and url.startswith("http"):
                # زرار من نوع Link (يفتح رابط)
                self.add_item(ui.Button(label=item["label"], url=url, style=discord.ButtonStyle.link))

    @ui.button(label="اظهار جميع التفاصيل 📦", style=discord.ButtonStyle.blurple, custom_id="show_details_btn", row=1)
    async def show_details(self, interaction: discord.Interaction, button: ui.Button):
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

    @app_commands.command(name="send_embed", description="إرسال إمبيد متجر احترافي بأزرار روابط")
    async def send_embed(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        target_channel = channel or self.bot.get_channel(self.default_target_id)
        if not target_channel:
            await interaction.response.send_message("❌ الروم غير موجود!", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedModal(self, target_channel))

async def setup(bot):
    await bot.add_cog(Messenger(bot))
