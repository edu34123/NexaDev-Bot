import discord
from discord import app_commands
from discord.ext import commands
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

class TicketManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("🔄 TicketManager inizializzato")

    @app_commands.command(name="ticket", description="Crea un ticket di supporto")
    async def ticket(self, interaction: discord.Interaction):
        """Crea un ticket di supporto"""
        try:
            await interaction.response.send_message("🎫 Sistema ticket funzionante!", ephemeral=True)
            logger.info(f"Ticket command used by {interaction.user}")
        except Exception as e:
            logger.error(f"Errore comando ticket: {e}")
            await interaction.response.send_message("❌ Errore nella creazione del ticket", ephemeral=True)

    @app_commands.command(name="close", description="Chiudi il ticket corrente")
    async def close(self, interaction: discord.Interaction):
        """Chiudi il ticket corrente"""
        try:
            await interaction.response.send_message("🔒 Ticket chiuso!", ephemeral=True)
        except Exception as e:
            logger.error(f"Errore comando close: {e}")

# QUESTA FUNZIONE È OBBLIGATORIA - SENZA DI QUESTA LA COG NON SI CARICA
async def setup(bot):
    cog = TicketManager(bot)
    await bot.add_cog(cog)
    logger.info("✅ TicketManager cog caricato con successo!")
