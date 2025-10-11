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
        
        # Invia automaticamente i messaggi dopo il sync
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
        logger.info("🔄 Tentativo di invio messaggi automatici...")
        
        try:
            # Invia messaggi di verifica
            from cogs.verification import VerificationView
            
            # Canali di verifica (dove inviare i messaggi)
            verify_channel_it_id = 1423717246261264509  # Sostituisci con ID corretto
            verify_channel_eng_id = 1423743289475076318  # Sostituisci con ID corretto
            
            channel_it = self.get_channel(verify_channel_it_id)
            channel_eng = self.get_channel(verify_channel_eng_id)
            
            if channel_it:
                # Pulisci canale e invia nuovo messaggio
                try:
                    await channel_it.purge(limit=10)
                except:
                    pass
                
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
                await channel_it.send(embed=embed_it, view=view)
                logger.info("✅ Messaggio verifica italiano inviato")
            
            if channel_eng:
                # Pulisci canale e invia nuovo messaggio
                try:
                    await channel_eng.purge(limit=10)
                except:
                    pass
                
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
                await channel_eng.send(embed=embed_eng, view=view)
                logger.info("✅ Messaggio verifica inglese inviato")
                
        except Exception as e:
            logger.error(f"❌ Errore invio messaggi automatici: {e}")

    async def on_ready(self):
        logger.info(f'✅ {self.user} è online!')
        logger.info(f'📊 Connesso a {len(self.guilds)} server')
        activity = discord.Activity(type=discord.ActivityType.watching, name="/help | NexaDev")
        await self.change_presence(activity=activity)

bot = NexaBot()

# COMANDI SLASH GLOBALI
@bot.tree.command(name="help", description="Mostra tutti i comandi disponibili")
async def help_command(interaction: discord.Interaction):
    """Mostra tutti i comandi slash"""
    embed = discord.Embed(
        title="🤖 Comandi Slash Disponibili",
        description="Ecco tutti i comandi del bot NexaDev:",
        color=0x00ff00
    )
    
    embed.add_field(
        name="🎫 Ticket System",
        value="• `/setup_tickets` - Setup sistema ticket\n• Clicca sui bottoni nei canali ticket",
        inline=False
    )
    
    embed.add_field(
        name="📊 Status System", 
        value="• `/status` - Aggiorna stato creazione",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Utility",
        value="• `/help` - Questo messaggio\n• `/ping` - Controlla latenza\n• `/sync` - Sincronizza comandi",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="ping", description="Controlla la latenza del bot")
async def ping(interaction: discord.Interaction):
    """Controlla la latenza"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! {latency}ms", ephemeral=True)

@bot.tree.command(name="sync", description="Sincronizza i comandi slash (Owner)")
async def sync(interaction: discord.Interaction):
    """Sincronizza i comandi"""
    try:
        await interaction.response.defer(ephemeral=True)
        synced = await bot.tree.sync()
        await interaction.followup.send(f"✅ {len(synced)} comandi sincronizzati!")
        logger.info(f"🔄 Sync manuale: {len(synced)} comandi")
    except Exception as e:
        await interaction.followup.send(f"❌ Errore: {e}")

@bot.tree.command(name="send_verify", description="Invia messaggi di verifica (Admin)")
@app_commands.default_permissions(administrator=True)
async def send_verify(interaction: discord.Interaction):
    """Invia manualmente i messaggi di verifica"""
    try:
        await interaction.response.defer(ephemeral=True)
        await bot.send_auto_messages()
        await interaction.followup.send("✅ Messaggi di verifica inviati!")
    except Exception as e:
        await interaction.followup.send(f"❌ Errore: {e}")

async def main():
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ DISCORD_TOKEN non trovato!")
        return
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f"💥 Errore avvio bot: {e}")

if __name__ == "__main__":
    asyncio.run(main())
