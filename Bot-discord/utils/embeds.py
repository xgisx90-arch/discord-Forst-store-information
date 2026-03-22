import discord

def create_main_embed(title, description, image_url):
    embed = discord.Embed(
        title=title,
        description=description,
        color=0x2b2d31 # اللون الرمادي المنسجم مع ديسكورد
    )
    embed.set_image(url=image_url)
    return embed