import discord
from discord.ext import commands
from discord import ui, app_commands
import os
import aiohttp
import io
from utils.embeds import create_main_embed

# 1. المودال المحدث (بدون رابط تكت ومع خانة ID الروم)
class EmbedModal(ui.Modal, title="إرسال إمبيد المتجر"):
    msg_title = ui.TextInput(label="العنوان العلوي", placeholder="مثلاً: نيترو قيمنق", required=True)
    msg_details = ui.TextInput(
        label="التفاصيل",
        style=discord.TextStyle.paragraph,
        placeholder="انسخ النص المنسق هنا...",
        required=True
    )
    msg_shop_link = ui.TextInput(label="رابط الموقع/الشراء", placeholder="https://...", required=False)
    # الخانة الجديدة لـ ID الروم (مثل روم التكت أو القوانين)
    msg_target_channel_id = ui.TextInput(
        label="ID الروم اللي عايز تشاور عليها", 
        placeholder="انسخ الـ ID هنا...", 
        required=False
    )

    def __init__(self, cog_instance, target_channel):
        super().__init__()
        self.cog = cog_instance
        self.target_channel = target_channel

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("✅ جاري تنفيذ طلبك والنشر...", ephemeral=True)

        guild_id = interaction.guild_id
        channel_id = self.msg_target_channel_id.value
        
        # إنشاء رابط "داخلي" يفتح الروم فوراً
        internal_link = f"https://discord.com/channels/{guild_id}/{channel_id}" if channel_id.isdigit() else None

        title_text = self.msg_title.value
        details_text = self.msg_details.value
        
        # وصف الإمبيد مع ذكر الروم (Mention) عشان تظهر بشكل تفاعلي
        mention_text = f"\n📍 الروم الموجهة: <#{channel_id}>" if channel_id.isdigit() else ""
        description_text = f"اضغط على زر ( 📦 اظهار جميع التفاصيل : {title_text} ){mention_text}"
        
        main_embed = create_main_embed(title_text, description_text, self.cog.top_banner)
        
        # تمرير البيانات للـ View
        view = DetailsView(details_text, self.msg_shop_link.value, internal_link)
        
        await self.target_channel.send(embed=main_embed, view=view)

        # إرسال البانر السفلي (عريض وكبير)
        async with aiohttp.ClientSession() as session:
            async with session.get(self.cog.bottom_banner) as resp:
                if resp.status == 200:
                    data = io.BytesIO(await resp.read())
                    file = discord.File(data, filename="banner.png")
                    await self.target_channel.send(file=file)

# 2. الـ View مع زرار الروم وزرار الموقع
class DetailsView(ui.View):
    def __init__(self, details_content, shop_url, internal_channel_url):
        super().__init__(timeout=None)
        self.details_content = details_content

        # زرار الموقع (لو موجود)
        if shop_url and shop_url.startswith("http"):
            self.add_item(ui.Button(label="رابط الشراء 🛒", url=shop_url, style=discord.ButtonStyle.link))
        
        # زرار "الروم" (بيفتح الروم اللي انت حطيت الـ ID بتاعها)
        if internal_channel_url:
            self.add_item(ui.Button(label="انتقل للروم 📍", url=internal_channel_url, style=discord.ButtonStyle.link))

    @ui.button(label="اظهار جميع التفاصيل 📦", style=discord.ButtonStyle.blurple, custom_id="show_details_btn")
    async def show_details(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(content=f"{self.details_content}", ephemeral=True)

class Messenger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.default_target_id = int(os.getenv('TARGET_CHANNEL_ID'))
        self.top_banner = os.getenv('TOP_BANNER_URL')
        self.bottom_banner = os.getenv('BOTTOM_BANNER_URL')

    @app_commands.command(name="send_embed", description="إرسال إمبيد متجر مع توجيه لروم محددة")
    async def send_embed(self, interaction: discord.Interaction, channel: discord.TextChannel = None):
        target_channel = channel or self.bot.get_channel(self.default_target_id)
        if not target_channel:
            await interaction.response.send_message("❌ الروم غير موجود!", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedModal(self, target_channel))

async def setup(bot):
    await bot.add_cog(Messenger(bot))
