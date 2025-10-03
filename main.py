import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()

# Verifica solo le variabili essenziali
required_env_vars = ['DISCORD_TOKEN']

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise Exception(f"Variabili d'ambiente ESSENZIALI mancanti: {', '.join(missing_vars)}")

# Avvisa per le variabili opzionali mancanti
optional_env_vars = ['GUILD_ID', 'TICKET_CHANNEL_ID', 'VERIFY_CHANNEL_ID', 'STATUS_CHANNEL_ID', 'STAFF_ROLE_ID']
missing_optional = [var for var in optional_env_vars if not os.getenv(var)]
if missing_optional:
    print(f"ATTENZIONE: Variabili opzionali mancanti: {', '.join(missing_optional)}")
    print("Alcune funzionalità potrebbero non funzionare correttamente.")

# Crea app Flask
app = Flask('')

@app.route('/')
def home():
    return "✅ NexaDev Bot is running!"

def run_flask():
    port = int(os.getenv('PORT', 10000))
    print(f"🚀 Avvio server Flask sulla porta {port}")
    app.run(host='0.0.0.0', port=port)

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
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f'✅ Caricato: cogs.{filename[:-3]}')
                loaded_cogs += 1
            except Exception as e:
                print(f'❌ Errore caricamento cogs.{filename[:-3]}: {e}')
    print(f'📦 Totale cogs caricati: {loaded_cogs}')

@bot.event
async def on_connect():
    print('🔗 Connesso a Discord...')
    await load_cogs()

def start_bot():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("❌ DISCORD_TOKEN non trovato")
    print('🔑 Token trovato, avvio bot Discord...')
    bot.run(token)

if __name__ == "__main__":
    print('🚀 Avvio NexaDev Bot...')
    
    # Avvia Flask in un thread separato
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Aspetta che Flask si avvii
    import time
    time.sleep(3)
    
    # Avvia il bot
    start_bot()
