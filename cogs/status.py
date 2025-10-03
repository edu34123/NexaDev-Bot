import discord
from discord import app_commands
from discord.ext import commands
from utils.config import Config

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Aggiorna lo stato di un progetto")
    @app_commands.describe(
        nome="Tipo di progetto",
        modalita="Stato del progetto"
    )
    @app_commands.choices(
        nome=[
            app_commands.Choice(name="server", value="server"),
            app_commands.Choice(name="bot", value="bot"),
            app_commands.Choice(name="server e bot", value="both")
        ],
        modalita=[
            app_commands.Choice(name="appena iniziato", value="started"),
            app_commands.Choice(name="a metà", value="halfway"),
            app_commands.Choice(name="finito", value="finished")
        ]
    )
    async def status(self, interaction: discord.Interaction, nome: str, modalita: str):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Non hai i permessi per eseguire questo comando!", ephemeral=True)
            return

        status_channel = self.bot.get_channel(Config.STATUS_CHANNEL_ID)
        if not status_channel:
            await interaction.response.send_message("Canale status non trovato!", ephemeral=True)
            return

        # Mappe per le traduzioni
        nome_map = {
            "server": "Server",
            "bot": "Bot", 
            "both": "Server e Bot"
        }
        
        modalita_map = {
            "started": "🟡 Appena Iniziato",
            "halfway": "🟠 A Metà", 
            "finished": "🟢 Finito"
        }

        embed = discord.Embed(
            title="📊 **Stato Progetto**",
            description=f"**Tipo:** {nome_map[nome]}\n**Stato:** {modalita_map[modalita]}\n**Aggiornato da:** {interaction.user.mention}",
            color=0x7289da,
            timestamp=discord.utils.utcnow()
        )

        await status_channel.send(embed=embed)
        await interaction.response.send_message("Stato aggiornato con successo!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Status(bot))
