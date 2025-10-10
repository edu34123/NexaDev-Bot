import os
import discord
from discord.ext import commands
import asyncio
from flask import Flask
from threading import Thread
import logging

# Configura logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server web per Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Discord Online - Ticket System Ready!"

@app.route('/health')
def health():
    return "✅ OK"

@app.route('/ping')
def ping():
    return "pong"

def run_web():
    try:
        port = int(os.getenv('PORT', 10000))
        logger.info(f"🌐 Avvio server web sulla porta {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Errore server web: {e}")

# Avvia il server web in un thread separato
try:
    web_thread = Thread(target=run_web, daemon=True)
    web_thread.start()
    logger.info("✅ Server web avviato")
except Exception as e:
    logger.error(f"❌ Errore avvio server web: {e}")

# Configurazione bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'✅ {bot.user} è online!')
    logger.info(f'📊 Connesso a {len(bot.guilds)} server')
    
    try:
        synced = await bot.tree.sync()
        logger.info(f'✅ {len(synced)} comandi slash sincronizzati!')
        
        # Stampa tutti i comandi registrati
        logger.info("📝 Comandi slash disponibili:")
        for cmd in synced:
            logger.info(f"  - /{cmd.name}")
            
    except Exception as e:
        logger.error(f'❌ Errore sincronizzazione comandi: {e}')

async def load_cogs():
    cogs = ['tickets_cog', 'status_cog', 'security_cog']
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            logger.info(f"✅ {cog} caricata")
        except Exception as e:
            logger.error(f"❌ Errore caricamento {cog}: {e}")

async def main():
    logger.info("🚀 Avvio del bot...")
    
    # Verifica variabili d'ambiente
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ ERRORE: DISCORD_TOKEN non trovato!")
        return
    
    # Verifica altre variabili importanti
    required_vars = ['TICKETS_CATEGORY_ID', 'STAFF_ROLE_ID', 'REPORT_ROLE_ID', 'CEO_ROLE_ID']
    for var in required_vars:
        if not os.getenv(var):
            logger.warning(f"⚠️ Variabile {var} non configurata")
    
    logger.info("✅ Variabili d'ambiente verificate")
    
    # Carica le cog
    await load_cogs()
    
    logger.info("✅ Tutte le cog caricate, avvio bot...")
    
    # Avvia il bot
    try:
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("❌ ERRORE: Token Discord non valido!")
    except Exception as e:
        logger.error(f"💥 Errore durante l'avvio: {e}")

if __name__ == "__main__":
    logger.info("🎯 Script principale avviato")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Bot fermato manualmente")
    except Exception as e:
        logger.error(f"💥 Errore critico: {e}")
