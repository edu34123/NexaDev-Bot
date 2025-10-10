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

# COMANDO DI TEST PER IL SETUP TICKET
@bot.tree.command(name="test_ticket", description="Test del sistema ticket")
async def test_ticket(interaction: discord.Interaction):
    """Comando di test per il sistema ticket"""
    try:
        embed = discord.Embed(
            title="🎫 TEST - NexaDev Supporto",
            description="**Questo è un messaggio di test!**",
            color=0x00ff00
        )
        embed.add_field(
            name="🤖 Bot Creator",
            value="Richiedi la creazione di un bot",
            inline=True
        )
        embed.add_field(
            name="🚨 Segnalazione", 
            value="Segnala un problema",
            inline=True
        )
        
        await interaction.response.send_message("✅ Messaggio di test inviato!", ephemeral=True)
        await interaction.channel.send(embed=embed)
        
    except Exception as e:
        logger.error(f"Errore test ticket: {e}")
        await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)

@bot.tree.command(name="setup_here", description="Crea il pannello ticket in questo canale")
@commands.has_permissions(administrator=True)
async def setup_here(interaction: discord.Interaction):
    """Crea il pannello ticket direttamente"""
    try:
        embed = discord.Embed(
            title="🎫 NexaDev - Supporto",
            description="Seleziona il tipo di assistenza di cui hai bisogno:",
            color=0x00ff00
        )
        
        embed.add_field(
            name="🤖 Bot Creator",
            value="Richiedi la creazione di un bot",
            inline=True
        )
        embed.add_field(
            name="🌐 Server Creator", 
            value="Richiedi la creazione di un server",
            inline=True
        )
        embed.add_field(
            name="⚡ Server/Bot Creator",
            value="Richiedi entrambi i servizi", 
            inline=True
        )
        embed.add_field(
            name="🤝 Partnership",
            value="Richiedi una partnership",
            inline=True
        )
        embed.add_field(
            name="🚨 Segnalazione", 
            value="Segnala un problema o utente",
            inline=True
        )

        # Crea i bottoni
        from discord.ui import Button, View
        
        class TestView(View):
            def __init__(self):
                super().__init__(timeout=None)
            
            @discord.ui.button(label="Bot Creator", style=discord.ButtonStyle.primary, emoji="🤖")
            async def bot_test(self, interaction: discord.Interaction, button: Button):
                await interaction.response.send_message("✅ Test Bot Creator funziona!", ephemeral=True)
            
            @discord.ui.button(label="Segnalazione", style=discord.ButtonStyle.danger, emoji="🚨")
            async def report_test(self, interaction: discord.Interaction, button: Button):
                await interaction.response.send_message("✅ Test Segnalazione funziona!", ephemeral=True)

        view = TestView()
        await interaction.response.send_message(embed=embed, view=view)
        logger.info(f"Pannello test creato da {interaction.user}")

    except Exception as e:
        logger.error(f"Errore setup_here: {e}")
        await interaction.response.send_message(f"❌ Errore: {e}", ephemeral=True)

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
    
    embed.add_field(
        name="🎫 Ticket System",
        value="• `/setup_tickets` - Setup sistema ticket\n• `/test_ticket` - Test sistema\n• `/setup_here` - Crea pannello qui",
        inline=False
    )
    
    embed.add_field(
        name="🔧 Utility",
        value="• `/ping` - Controlla latenza\n• `/help` - Questo messaggio\n• `/sync` - Sincronizza comandi",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="sync", description="Sincronizza i comandi")
async def sync(interaction: discord.Interaction):
    try:
        await interaction.response.defer(ephemeral=True)
        synced = await bot.tree.sync()
        bot.synced = True
        await interaction.followup.send(f"✅ Sincronizzati {len(synced)} comandi!")
    except Exception as e:
        await interaction.followup.send(f"❌ Errore: {e}")

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
