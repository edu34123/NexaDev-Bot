import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

print("🚀 Avvio NexaDev Bot...")

# Verifica solo le variabili essenziali
required_env_vars = ['DISCORD_TOKEN']

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise Exception(f"Variabili d'ambiente ESSENZIALI mancanti: {', '.join(missing_vars)}")

print("✅ Tutte le variabili essenziali trovate")

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} è online!')
    print(f'📊 Connesso a {len(bot.guilds)} server:')
    for guild in bot.guilds:
        print(f'   - {guild.name} (ID: {guild.id})')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="NexaDev Tickets"))

async def load_cogs():
    loaded_cogs = 0
    cogs_dir = './cogs'
    if os.path.exists(cogs_dir):
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                try:
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    print(f'✅ Caricato: cogs.{filename[:-3]}')
                    loaded_cogs += 1
                except Exception as e:
                    print(f'❌ Errore caricamento cogs.{filename[:-3]}: {e}')
    else:
        print("📁 Directory cogs non trovata, continuo senza cogs")
    print(f'📦 Totale cogs caricati: {loaded_cogs}')

@bot.event
async def on_connect():
    print('🔗 Connesso a Discord...')
    await load_cogs()

if __name__ == "__main__":
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("❌ DISCORD_TOKEN non trovato")
    
    print('🔑 Token trovato, avvio bot Discord...')
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Errore avvio bot: {e}")
