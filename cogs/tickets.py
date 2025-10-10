import discord
from discord import app_commands
from discord.ext import commands
import os
import logging

logger = logging.getLogger(__name__)

class TicketsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ticket", description="Crea un ticket di supporto")
    @app_commands.describe(motivo="Motivo del ticket")
    async def ticket(self, interaction: discord.Interaction, motivo: str):
        """Crea un ticket di supporto"""
        try:
            # Implementa la logica del ticket qui
            await interaction.response.send_message(
                f"🎫 Ticket creato! Motivo: {motivo}", 
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Errore comando ticket: {e}")
            await interaction.response.send_message(
                "❌ Errore nella creazione del ticket", 
                ephemeral=True
            )

    @app_commands.command(name="close", description="Chiudi il ticket corrente")
    async def close(self, interaction: discord.Interaction):
        """Chiudi il ticket corrente"""
        try:
            await interaction.response.send_message("🔒 Ticket chiuso!", ephemeral=True)
        except Exception as e:
            logger.error(f"Errore comando close: {e}")

async def setup(bot):
    await bot.add_cog(TicketsCog(bot))
    logger.info("✅ TicketsCog caricato")
