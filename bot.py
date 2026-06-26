import os, asyncio, discord
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()
TOKEN=os.getenv("DISCORD_TOKEN")
intents=discord.Intents.default()
intents.message_content=True
intents.members=True
bot=commands.Bot(command_prefix="!",intents=intents)
@bot.event
async def on_ready():
    print(f"Đăng nhập thành công: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Đã đồng bộ {len(synced)} slash command")
    except Exception as e:
        print(e)
async def load_extensions():
    for f in os.listdir("./cogs"):
        if f.endswith(".py"):
            await bot.load_extension(f"cogs.{f[:-3]}")
async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)
asyncio.run(main())
