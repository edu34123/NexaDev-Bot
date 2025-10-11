import discord
from discord import app_commands
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="status", description="Aggiorna lo stato di creazione")
    @app_commands.describe(
        stato="Stato della creazione",
        membro="Membro da menzionare",
        messaggio="Messaggio dello stato",
        lingua="Lingua (it/eng)"
    )
    async def status_update(self, interaction: discord.Interaction, stato: str, membro: discord.Member, messaggio: str, lingua: str):
        """Aggiorna lo stato di creazione"""
        try:
            if lingua.lower() == "it":
                channel = self.bot.get_channel(1423772997336170653)  # channel_statusit_id
                title = f"📊 Stato Creazione - {stato}"
            elif lingua.lower() == "eng":
                channel = self.bot.get_channel(1423395930811535444)  # chann_statuseng_id
                title = f"📊 Creation Status - {stato}"
            else:
                await interaction.response.send_message("❌ Lingua non valida. Usa 'it' o 'eng'", ephemeral=True)
                return

            if not channel:
                await interaction.response.send_message("❌ Canale non trovato", ephemeral=True)
                return

            embed = discord.Embed(
                title=title,
                description=messaggio,
                color=0x00ff00
            )
            embed.add_field(name="👤 Cliente", value=membro.mention, inline=True)
            embed.add_field(name="🔧 Staff", value=interaction.user.mention, inline=True)
            
            await channel.send(embed=embed)
            await interaction.response.send_message("✅ Status aggiornato!", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Errore status update: {e}")
            await interaction.response.send_message("❌ Errore nell'aggiornamento dello status", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Status(bot))
