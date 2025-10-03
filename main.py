import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} è online!')
    await bot.load_extension('cogs.tickets')
    await bot.load_extension('cogs.verification')
    await bot.load_extension('cogs.status')
    await bot.tree.sync()

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
