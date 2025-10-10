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

class SecurityBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        """Setup hook che viene chiamato all'avvio"""
        logger.info("🔄 Setup hook avviato...")
        
        # Prima verifica quali file esistono
        await self.debug_files()
        
        # Poi carica le cog
        await self.load_cogs()
        
        # Infine sincronizza i comandi
        await self.sync_commands()

    async def debug_files(self):
        """Debug dei file nella directory corrente"""
        logger.info("📁 Scansione file nella directory corrente:")
        current_dir = os.listdir('.')
        py_files = [f for f in current_dir if f.endswith('.py')]
        cog_files = [f for f in py_files if f.endswith('_cog.py')]
        
        logger.info(f"📝 Tutti i file .py: {len(py_files)}")
        for file in py_files:
            logger.info(f"  - {file}")
        
        logger.info(f"🔧 File cog trovati: {len(cog_files)}")
        for file in cog_files:
            logger.info(f"  - {file}")

    async def load_cogs(self):
        """Carica tutte le cog con gestione errori migliorata"""
        # Lista delle cog da caricare
        cog_list = [
            'tickets_cog',
            'status_cog', 
            'security_cog'
        ]
        
        logger.info("🔄 Caricamento cog...")
        
        for cog_name in cog_list:
            try:
                # Verifica se il file esiste
                if not os.path.exists(f"{cog_name}.py"):
                    logger.warning(f"⚠️ File {cog_name}.py non trovato, salto...")
                    continue
                
                # Prova a caricare la cog
                await self.load_extension(cog_name)
                logger.info(f"✅ {cog_name} caricata con successo")
                
            except commands.ExtensionNotFound:
                logger.error(f"❌ Cog {cog_name} non trovata")
            except commands.NoEntryPointError:
                logger.error(f"❌ Cog {cog_name} non ha una funzione setup()")
            except commands.ExtensionFailed as e:
                logger.error(f"❌ Errore nell'inizializzazione di {cog_name}: {e}")
            except Exception as e:
                logger.error(f"❌ Errore imprevisto caricando {cog_name}: {e}")

    async def sync_commands(self):
        """Sincronizza i comandi slash"""
        logger.info("🔄 Sincronizzazione comandi slash...")
        try:
            # Sincronizza comandi globali
            synced = await self.tree.sync()
            logger.info(f'✅ {len(synced)} comandi slash sincronizzati globalmente!')
            
            # Log dei comandi disponibili
            if synced:
                logger.info("📝 Comandi slash disponibili:")
                for cmd in synced:
                    logger.info(f"  - /{cmd.name}")
            else:
                logger.warning("⚠️ Nessun comando slash sincronizzato")
                
        except Exception as e:
            logger.error(f'❌ Errore sincronizzazione comandi: {e}')

    async def on_ready(self):
        """Evento quando il bot è pronto"""
        logger.info(f'✅ {self.user} è online!')
        logger.info(f'📊 Connesso a {len(self.guilds)} server')
        
        # Imposta lo status del bot
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="la sicurezza del server"
        )
        await self.change_presence(activity=activity)
        
        # Verifica che le cog siano caricate
        logger.info("🔄 Cog caricate:")
        if self.cogs:
            for cog_name in self.cogs:
                logger.info(f"  - {cog_name}")
        else:
            logger.warning("⚠️ Nessuna cog caricata")

# Inizializza il bot
bot = SecurityBot()

# Comandi di debug e utilità
@bot.tree.command(name="sync", description="Sincronizza i comandi (solo owner)")
async def sync_commands(interaction: discord.Interaction):
    """Forza la sincronizzazione dei comandi slash"""
    try:
        # Verifica che sia l'owner del bot
        if interaction.user.id != bot.owner_id:
            await interaction.response.send_message("❌ Solo l'owner del bot può usare questo comando!", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        # Sincronizza i comandi
        synced = await bot.tree.sync()
        await interaction.followup.send(
            f"✅ Sincronizzati {len(synced)} comandi!", 
            ephemeral=True
        )
        logger.info(f"🔄 Sincronizzazione forzata: {len(synced)} comandi")
        
    except Exception as e:
        await interaction.followup.send(
            f"❌ Errore sincronizzazione: {e}", 
            ephemeral=True
        )
        logger.error(f"Errore sincronizzazione forzata: {e}")

@bot.tree.command(name="ping", description="Controlla la latenza del bot")
async def ping(interaction: discord.Interaction):
    """Comando ping per testare il bot"""
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(
        f"🏓 Pong! Latency: {latency}ms", 
        ephemeral=True
    )

@bot.tree.command(name="info", description="Informazioni sul bot")
async def bot_info(interaction: discord.Interaction):
    """Mostra informazioni sul bot"""
    embed = discord.Embed(
        title="🤖 NexaDev Security Bot",
        description="Bot per la sicurezza e gestione server Discord",
        color=0x00ff00
    )
    embed.add_field(name="📊 Server", value=len(bot.guilds), inline=True)
    embed.add_field(name="🏓 Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🔧 Cog Caricate", value=len(bot.cogs), inline=True)
    embed.add_field(name="📝 Comandi Slash", value=len(bot.tree.get_commands()), inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def main():
    """Funzione principale"""
    logger.info("🚀 Avvio del NexaDev Security Bot...")
    
    # Verifica variabili d'ambiente
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ ERRORE: DISCORD_TOKEN non trovato!")
        logger.error("💡 Assicurati di aver impostato la variabile d'ambiente DISCORD_TOKEN")
        return
    
    # Verifica variabili opzionali
    required_vars = ['TICKETS_CATEGORY_ID', 'STAFF_ROLE_ID', 'REPORT_ROLE_ID', 'CEO_ROLE_ID']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
            logger.warning(f"⚠️ Variabile {var} non configurata")
    
    if missing_vars:
        logger.warning(f"⚠️ Variabili mancanti: {', '.join(missing_vars)}")
    else:
        logger.info("✅ Tutte le variabili d'ambiente configurate")
    
    # Imposta l'owner del bot (opzionale, per comandi admin)
    try:
        # Puoi impostare manualmente l'owner ID se vuoi
        # bot.owner_id = 123456789012345678
        pass
    except Exception as e:
        logger.warning(f"⚠️ Impossibile impostare owner_id: {e}")
    
    # Avvia il bot
    try:
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("❌ ERRORE: Token Discord non valido!")
    except KeyboardInterrupt:
        logger.info("⏹️ Bot fermato manualmente")
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
