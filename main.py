import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from flask import Flask
from threading import Thread
import logging

# Configura logging dettagliato
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Server web per Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot Discord Online - Ticket System Ready!"

@app.route('/health')
def health():
    return "✅ OK"

def run_web():
    try:
        port = int(os.getenv('PORT', 10000))
        logger.info(f"🌐 Avvio server web sulla porta {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Errore server web: {e}")

# Avvia il server web
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

# Usa commands.Bot con tree per i comandi slash
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            application_id=os.getenv('APPLICATION_ID')  # Opzionale ma consigliato
        )

    async def setup_hook(self):
        """Setup hook che viene chiamato all'avvio"""
        logger.info("🔄 Caricamento cog...")
        await self.load_cogs()
        
        # Sincronizza i comandi slash
        logger.info("🔄 Sincronizzazione comandi slash...")
        try:
            synced = await self.tree.sync()
            logger.info(f'✅ {len(synced)} comandi slash sincronizzati!')
            
            # Log dei comandi disponibili
            logger.info("📝 Comandi slash disponibili:")
            for cmd in synced:
                logger.info(f"  - /{cmd.name}")
        except Exception as e:
            logger.error(f'❌ Errore sincronizzazione comandi: {e}')

    async def load_cogs(self):
        cogs = ['tickets_cog', 'status_cog', 'security_cog']
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ {cog} caricata con successo")
            except Exception as e:
                logger.error(f"❌ Errore caricamento {cog}: {e}")

bot = MyBot()

@bot.event
async def on_ready():
    logger.info(f'✅ {bot.user} è online!')
    logger.info(f'📊 Connesso a {len(bot.guilds)} server')
    
    # Verifica che le cog siano caricate
    logger.info("🔄 Verifica cog caricate:")
    for cog_name in bot.cogs:
        logger.info(f"  - {cog_name}")

async def main():
    logger.info("🚀 Avvio del bot...")
    
    # Verifica variabili d'ambiente
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ ERRORE: DISCORD_TOKEN non trovato!")
        return
    
    required_vars = ['TICKETS_CATEGORY_ID', 'STAFF_ROLE_ID', 'REPORT_ROLE_ID', 'CEO_ROLE_ID']
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.warning(f"⚠️ Variabile {var} non configurata")
    
    if missing_vars:
        logger.warning(f"⚠️ Variabili mancanti: {', '.join(missing_vars)}")
    
    logger.info("✅ Verifica variabili d'ambiente completata")
    
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
