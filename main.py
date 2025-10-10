import os
import discord
from discord.ext import commands
import asyncio

# Carica le variabili d'ambiente
from dotenv import load_dotenv
load_dotenv()

# Configurazione
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} è online!')
    print(f'📊 Connesso a {len(bot.guilds)} server')
    
    # Sincronizza i comandi slash
    try:
        synced = await bot.tree.sync()
        print(f'✅ {len(synced)} comandi slash sincronizzati!')
        
        # Stampa i comandi disponibili
        print("📝 Comandi disponibili:")
        for cmd in synced:
            print(f"  - /{cmd.name}")
            
    except Exception as e:
        print(f'❌ Errore sincronizzazione comandi: {e}')

async def load_cogs():
    """Carica tutte le cog"""
    cogs = ['tickets_cog', 'status_cog', 'security_cog']
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Cog {cog} caricata")
        except Exception as e:
            print(f"❌ Errore caricamento {cog}: {e}")

@bot.event
async def on_command_error(ctx, error):
    """Gestione errori"""
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"❌ Errore comando: {error}")

async def main():
    """Funzione principale"""
    print("🚀 Avvio del bot...")
    
    # Verifica che il token esista
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ ERRORE: DISCORD_TOKEN non trovato nelle variabili d'ambiente!")
        print("💡 Assicurati di aver impostato il token in Render.com -> Environment Variables")
        return
    
    print("✅ Token trovato, caricamento cog...")
    
    # Carica le cog
    await load_cogs()
    
    print("✅ Cog caricate, avvio bot...")
    
    # Avvia il bot
    try:
        await bot.start(token)
    except discord.LoginFailure:
        print("❌ ERRORE: Token Discord non valido!")
    except Exception as e:
        print(f"💥 Errore durante l'avvio: {e}")

if __name__ == "__main__":
    # Esegui il bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("⏹️ Bot fermato manualmente")
    except Exception as e:
        print(f"💥 Errore critico: {e}")
