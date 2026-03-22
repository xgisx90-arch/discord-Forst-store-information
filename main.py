import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        try:
            self.tree.clear_commands(guild=None)
            await self.load_extension('cogs.messenger')
            await self.tree.sync()
            print("✅ تم تحديث الأوامر وعمل مزامنة للسلاش كcommand")
        except Exception as e:
            print(f"❌ خطأ: {e}")

    async def on_ready(self):
        print(f'🚀 {self.user.name} جاهز!')
        # حط ID سيرفرك هنا عشان يظهر السلاش فوراً
        guild_id = 1482106086965248203  # استبدله بـ ID سيرفرك
        guild = discord.Object(id=guild_id)

        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print("✅ تم عمل Sync إجباري للسيرفر!")

bot = MyBot()
bot.run(TOKEN)
