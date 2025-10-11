import os
import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from flask import Flask
from threading import Thread
import logging

# Configura logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Server web per Render
app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 NexaDev Bot Online"

@app.route('/health')
def health():
    return "✅ OK"

def run_web():
    try:
        port = int(os.getenv('PORT', 10000))
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Errore server web: {e}")

# Avvia server web
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

class NexaBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Setup hook all'avvio"""
        logger.info("🔄 Caricamento cog...")
        
        # Carica tutte le cog
        cogs = ['cogs.tickets', 'cogs.verification', 'cogs.status']
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ {cog} caricato")
            except Exception as e:
                logger.error(f"❌ Errore {cog}: {e}")
        
        # Sincronizza comandi
        try:
            synced = await self.tree.sync()
            logger.info(f'✅ {len(synced)} comandi sincronizzati')
        except Exception as e:
            logger.error(f'❌ Errore sincronizzazione: {e}')

    async def on_ready(self):
        logger.info(f'✅ {self.user} è online!')
        logger.info(f'📊 Connesso a {len(self.guilds)} server')
        
        # Avvia i task automatici
        self.loop.create_task(self.auto_setup())

    async def auto_setup(self):
        """Setup automatico dei sistemi"""
        await self.wait_until_ready()
        await asyncio.sleep(5)  # Aspetta che tutto sia pronto
        
        # Setup verification
        verification_cog = self.get_cog('Verification')
        if verification_cog:
            await verification_cog.setup_verification()
        
        # Setup tickets
        tickets_cog = self.get_cog('Tickets')
        if tickets_cog:
            await tickets_cog.setup_tickets()

bot = NexaBot()

# Comandi utility
@bot.tree.command(name="sync", description="Sincronizza i comandi")
async def sync(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        synced = await bot.tree.sync()
        await interaction.followup.send(f"✅ Sincronizzati {len(synced)} comandi!")
    except Exception as e:
        await interaction.followup.send(f"❌ Errore: {e}")

@bot.tree.command(name="ping", description="Controlla la latenza")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! {latency}ms", ephemeral=True)

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ DISCORD_TOKEN non trovato!")
        return
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"💥 Errore: {e}")

if __name__ == "__main__":
    asyncio.run(main())
