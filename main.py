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
        self.synced = False

    async def setup_hook(self):
        """Setup hook che viene chiamato all'avvio"""
        logger.info("🔄 Setup hook avviato...")
        
        # Carica le cog
        await self.load_cogs()
        
        # Sincronizza i comandi
        await self.sync_commands()

    async def load_cogs(self):
        """Carica tutte le cog"""
        cog_files = ['ticket_manager']
        
        for cog_name in cog_files:
            try:
                if os.path.exists(f"{cog_name}.py"):
                    await self.load_extension(cog_name)
                    logger.info(f"✅ {cog_name} caricata")
                else:
                    logger.warning(f"⚠️ {cog_name}.py non trovato")
            except Exception as e:
                logger.error(f"❌ Errore caricamento {cog_name}: {e}")

    async def sync_commands(self):
        """Sincronizza i comandi slash"""
        try:
            if not self.synced:
                synced = await self.tree.sync()
                self.synced = True
                logger.info(f'✅ {len(synced)} comandi slash sincronizzati!')
                
                # Mostra tutti i comandi
                all_commands = self.tree.get_commands()
                logger.info("📝 Comandi globali disponibili:")
                for cmd in all_commands:
                    logger.info(f"  - /{cmd.name}")
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
            name="la sicurezza | /help"
        )
        await self.change_presence(activity=activity)
        
        # Log delle cog caricate
        logger.info("🔧 Cog caricate:")
        for cog_name in self.cogs:
            logger.info(f"  - {cog_name}")

# Inizializza il bot
bot = SecurityBot()

# COMANDI GLOBALI - Questi sono SEMPRE disponibili
@bot.tree.command(name="ping", description="Controlla la latenza del bot")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! {latency}ms", ephemeral=True)

@bot.tree.command(name="help", description="Mostra tutti i comandi disponibili")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Comandi Disponibili",
        description="Ecco tutti i comandi del bot:",
        color=0x00ff00
    )
    
    # Comandi globali
    embed.add_field(
        name="🌐 Comandi Globali",
        value="• `/ping` - Controlla la latenza\n• `/help` - Questo messaggio\n• `/sync` - Sincronizza comandi\n• `/info` - Info bot",
        inline=False
    )
    
    # Comandi dalle cog
    if bot.cogs:
        for cog_name, cog_instance in bot.cogs.items():
            commands_list = []
            for attr_name in dir(cog_instance):
                attr = getattr(cog_instance, attr_name)
                if hasattr(attr, '__self__') and hasattr(attr, 'binding'):
                    if isinstance(attr.binding, app_commands.Command):
                        commands_list.append(f"• `/{attr.binding.name}` - {attr.binding.description}")
            
            if commands_list:
                embed.add_field(
                    name=f"🔧 {cog_name}",
                    value="\n".join(commands_list[:5]),  # Mostra max 5 comandi
                    inline=False
                )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="sync", description="Sincronizza i comandi (owner only)")
async def sync(interaction: discord.Interaction):
    """Sincronizza i comandi slash"""
    try:
        # Verifica owner (puoi impostare bot.owner_id)
        # if interaction.user.id != bot.owner_id:
        #     await interaction.response.send_message("❌ Solo l'owner può usare questo comando!", ephemeral=True)
        #     return
        
        await interaction.response.defer(ephemeral=True)
        
        # Sincronizza
        synced = await bot.tree.sync()
        bot.synced = True
        
        await interaction.followup.send(f"✅ Sincronizzati {len(synced)} comandi!")
        logger.info(f"🔄 Sincronizzazione manuale: {len(synced)} comandi")
        
    except Exception as e:
        await interaction.followup.send(f"❌ Errore: {e}")
        logger.error(f"Errore sync manuale: {e}")

@bot.tree.command(name="info", description="Informazioni sul bot")
async def info(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 NexaDev Security Bot",
        description="Bot per la sicurezza e gestione server Discord",
        color=0x00ff00
    )
    embed.add_field(name="📊 Server", value=len(bot.guilds), inline=True)
    embed.add_field(name="🏓 Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="🔧 Cog", value=len(bot.cogs), inline=True)
    embed.add_field(name="📝 Comandi", value=len(bot.tree.get_commands()), inline=True)
    embed.add_field(name="🔄 Sincronizzato", value="✅" if bot.synced else "❌", inline=True)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

async def main():
    """Funzione principale"""
    logger.info("🚀 Avvio del NexaDev Security Bot...")
    
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
