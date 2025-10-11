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
        logger.info(f"🌐 Avvio server web sulla porta {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        logger.error(f"❌ Errore server web: {e}")

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
        self.synced = False

    async def setup_hook(self):
        """Setup hook che viene chiamato all'avvio"""
        logger.info("🔄 Setup hook avviato...")
        
        # Carica le cog
        await self.load_cogs()
        
        # Sincronizza i comandi
        await self.sync_commands()
        
        logger.info("✅ Setup hook completato")

    async def load_cogs(self):
        """Carica tutte le cog"""
        cogs = ['cogs.tickets', 'cogs.verification', 'cogs.status']
        
        for cog in cogs:
            try:
                await self.load_extension(cog)
                logger.info(f"✅ {cog} caricato")
            except Exception as e:
                logger.error(f"❌ Errore caricamento {cog}: {e}")

    async def sync_commands(self):
        """Sincronizza i comandi slash"""
        try:
            if not self.synced:
                synced = await self.tree.sync()
                self.synced = True
                logger.info(f'✅ {len(synced)} comandi slash sincronizzati!')
            else:
                logger.info("ℹ️ Comandi già sincronizzati")
        except Exception as e:
            logger.error(f'❌ Errore sincronizzazione: {e}')

    async def on_ready(self):
        """Evento quando il bot è pronto"""
        logger.info(f'✅ {self.user} è online!')
        logger.info(f'📊 Connesso a {len(self.guilds)} server')
        
        # Imposta lo status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="/help | NexaDev Services"
        )
        await self.change_presence(activity=activity)
        
        # Log delle cog caricate
        logger.info("🔧 Cog caricate:")
        for cog_name in self.cogs:
            logger.info(f"  - {cog_name}")

# Inizializza il bot
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

@bot.tree.command(name="sync", description="Sincronizza i comandi slash (Admin)")
@app_commands.default_permissions(administrator=True)
async def sync(interaction: discord.Interaction):
    """Sincronizza i comandi"""
    try:
        await interaction.response.defer(ephemeral=True)
        synced = await bot.tree.sync()
        bot.synced = True
        await interaction.followup.send(f"✅ {len(synced)} comandi sincronizzati!")
        logger.info(f"🔄 Sync manuale: {len(synced)} comandi")
    except Exception as e:
        await interaction.followup.send(f"❌ Errore: {e}")

@bot.tree.command(name="send_messages", description="Invia messaggi automatici (Admin)")
@app_commands.default_permissions(administrator=True)
async def send_messages(interaction: discord.Interaction):
    """Invia manualmente i messaggi automatici"""
    try:
        await interaction.response.defer(ephemeral=True)
        
        # Importa qui per evitare circular imports
        from cogs.verification import VerificationView
        
        # Canali di verifica
        verify_channel_it = bot.get_channel(1423717246261264509)  # Canale verifica italiano
        verify_channel_eng = bot.get_channel(1423743289475076318)  # Canale verifica inglese
        
        # Canali ticket
        ticket_channel_it = bot.get_channel(1423755447445225554)  # tickets_it
        ticket_channel_eng = bot.get_channel(1423395942094344223)  # tickets_eng
        
        messages_sent = 0
        
        # Messaggi di verifica
        if verify_channel_it:
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
            try:
                await verify_channel_it.purge(limit=10)
            except:
                pass
            await verify_channel_it.send(embed=embed_it, view=view)
            messages_sent += 1
            logger.info("✅ Messaggio verifica italiano inviato")
        
        if verify_channel_eng:
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
            try:
                await verify_channel_eng.purge(limit=10)
            except:
                pass
            await verify_channel_eng.send(embed=embed_eng, view=view)
            messages_sent += 1
            logger.info("✅ Messaggio verifica inglese inviato")
        
        await interaction.followup.send(f"✅ {messages_sent} messaggi inviati!")
        
    except Exception as e:
        logger.error(f"Errore invio messaggi: {e}")
        await interaction.followup.send(f"❌ Errore: {e}")

async def main():
    """Funzione principale"""
    logger.info("🚀 Avvio del NexaDev Bot...")
    
    # Verifica variabili d'ambiente
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ ERRORE: DISCORD_TOKEN non trovato!")
        logger.error("💡 Assicurati di aver impostato la variabile d'ambiente DISCORD_TOKEN")
        return
    
    logger.info("✅ Token trovato, avvio bot...")
    
    try:
        # Avvia il bot
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("❌ ERRORE: Token Discord non valido!")
    except KeyboardInterrupt:
        logger.info("⏹️ Bot fermato manualmente")
    except Exception as e:
        logger.error(f"💥 Errore durante l'avvio: {e}")

if __name__ == "__main__":
    logger.info("🎯 Script principale avviato")
    
    # Avvia il server web in un thread
    try:
        web_thread = Thread(target=run_web, daemon=True)
        web_thread.start()
        logger.info("✅ Server web avviato")
    except Exception as e:
        logger.error(f"❌ Errore avvio server web: {e}")
    
    # Avvia il bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("⏹️ Bot fermato manualmente")
    except Exception as e:
        logger.error(f"💥 Errore critico: {e}")
