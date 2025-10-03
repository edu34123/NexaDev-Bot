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
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="NexaDev Tickets"))

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_connect():
    await load_cogs()

if __name__ == "__main__":
    bot.run(os.getenv('DISCORD_TOKEN'))
