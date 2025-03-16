import discord
from discord.ext import commands
import asyncio
from config import DISCORD_TOKEN

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="$", intents = intents)
COGS = ["cogs.handlers", "cogs.moderation", "cogs.utility"]

async def load_cogs():
    for cog in COGS:
        await bot.load_extension(cog)

async def main():
    print("Starting bot...")
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)

asyncio.run(main())