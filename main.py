import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading
import requests
import time

load_dotenv()

print("🚀 Avvio NexaDev Bot...")

# Verifica solo le variabili essenziali
required_env_vars = ['DISCORD_TOKEN']

missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise Exception(f"Variabili d'ambiente ESSENZIALI mancanti: {', '.join(missing_vars)}")

print("✅ Tutte le variabili essenziali trovate")

# App Flask per keep-alive
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ NexaDev Bot is running!"

@app.route('/health')
def health():
    return "OK"

def run_flask():
    port = int(os.getenv('PORT', 10000))
    print(f"🌐 Server Flask sulla porta {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

# Keep-alive per evitare sospensioni
def keep_alive():
    time.sleep(30)  # Aspetta che tutto si avvii
    while True:
        try:
            # Fai una richiesta a te stesso per mantenere attivo
            requests.get(f"http://localhost:{os.getenv('PORT', 10000)}/health", timeout=5)
            print("🔄 Keep-alive request inviata")
        except:
            print("⚠️ Keep-alive fallita")
        time.sleep(300)  # Ogni 5 minuti

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
    # Avvia Flask
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Avvia keep-alive
    keep_alive_thread = threading.Thread(target=keep_alive)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()
    
    # Avvia bot Discord
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        raise ValueError("❌ DISCORD_TOKEN non trovato")
    
    print('🔑 Token trovato, avvio bot Discord...')
    try:
        bot.run(token)
    except Exception as e:
        print(f"❌ Errore avvio bot: {e}")
