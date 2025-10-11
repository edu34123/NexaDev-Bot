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
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

# Avvia server web
web_thread = Thread(target=run_web, daemon=True)
web_thread.start()

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
        logger.info("🔄 Setup hook avviato...")
        await self.load_cogs()
        await self.sync_commands()
        
        # Invia automaticamente i messaggi
        await self.send_auto_messages()

    async def load_cogs(self):
        cogs = ['cogs.tickets', 'cogs.verification', 'cogs.status']
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ {cog} caricato")
            except Exception as e:
                logger.error(f"❌ Errore {cog}: {e}")

    async def sync_commands(self):
        try:
            synced = await self.tree.sync()
            logger.info(f'✅ {len(synced)} comandi sincronizzati')
        except Exception as e:
            logger.error(f'❌ Errore sincronizzazione: {e}')

    async def send_auto_messages(self):
        await self.wait_until_ready()
        await asyncio.sleep(5)  # Aspetta che il bot sia pronto
        
        try:
            # Invia messaggi di verifica
            from cogs.verification import VerificationView
            channel_it = self.get_channel(1423717246261264509)  # Canale italiano
            channel_eng = self.get_channel(1423743289475076318)  # Canale inglese
            
            if channel_it:
                embed_it = discord.Embed(
                    title="🔐 Verifica | Verification",
                    description=(
                        "**Italiano:**\n"
                        "Clicca sul pulsante qui sotto per verificarti e accedere al server!\n\n"
                        "**English:**\n"
                        "Click the button below to verify yourself and access the server!"
                    ),
                    color=0x00ff00
                )
                view = VerificationView()
                await channel_it.purge(limit=10)  # Pulisci vecchi messaggi
                await channel_it.send(embed=embed_it, view=view)
                logger.info("✅ Messaggio verifica italiano inviato")
            
            if channel_eng:
                embed_eng = discord.Embed(
                    title="🔐 Verification | Verifica",
                    description=(
                        "**English:**\n"
                        "Click the button below to verify yourself and access the server!\n\n"
                        "**Italiano:**\n"
                        "Clicca sul pulsante qui sotto per verificarti e accedere al server!"
                    ),
                    color=0x00ff00
                )
                view = VerificationView()
                await channel_eng.purge(limit=10)
                await channel_eng.send(embed=embed_eng, view=view)
                logger.info("✅ Messaggio verifica inglese inviato")
                
        except Exception as e:
            logger.error(f"❌ Errore invio messaggi automatici: {e}")

    async def on_ready(self):
        logger.info(f'✅ {self.user} è online!')
        activity = discord.Activity(type=discord.ActivityType.watching, name="NexaDev Services")
        await self.change_presence(activity=activity)

bot = NexaBot()

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ DISCORD_TOKEN non trovato!")
        return
    await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
