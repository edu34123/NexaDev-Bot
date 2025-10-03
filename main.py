import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

# Verifica che tutte le variabili d'ambiente siano presenti
required_env_vars = [
    'DISCORD_TOKEN',
    'GUILD_ID', 
    'TICKET_CHANNEL_ID',
    'VERIFY_CHANNEL_ID',
    'STATUS_CHANNEL_ID',
    'STAFF_ROLE_ID'
]

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise Exception(f"Variabili d'ambiente mancanti: {', '.join(missing_vars)}")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} è online!')
    print(f'Server: {bot.guilds[0].name if bot.guilds else "Nessun server"}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="NexaDev Tickets"))

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'Caricato: cogs.{filename[:-3]}')
            except Exception as e:
                print(f'Errore caricamento cogs.{filename[:-3]}: {e}')

@bot.event
async def on_connect():
    await load_cogs()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("DISCORD_TOKEN non trovato nelle variabili d'ambiente")
    bot.run(token)
