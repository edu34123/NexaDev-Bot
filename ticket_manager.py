import discord
from discord import app_commands
from discord.ext import commands
import os
import logging

logger = logging.getLogger(__name__)

class TicketManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ TicketManager inizializzato")

    @app_commands.command(name="ticket", description="Crea un ticket di supporto")
    @app_commands.describe(motivo="Motivo del ticket")
    async def ticket(self, interaction: discord.Interaction, motivo: str):
        """Crea un ticket di supporto"""
        try:
            embed = discord.Embed(
                title="🎫 Ticket Creato",
                description=f"**Motivo:** {motivo}",
                color=0x00ff00
            )
            embed.add_field(name="👤 Creato da", value=interaction.user.mention, inline=True)
            embed.add_field(name="⏰ Data", value=discord.utils.format_dt(discord.utils.utcnow(), 'F'), inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=False)
            logger.info(f"Ticket creato da {interaction.user} per: {motivo}")
            
        except Exception as e:
            logger.error(f"Errore ticket: {e}")
            await interaction.response.send_message("❌ Errore nella creazione del ticket", ephemeral=True)

    @app_commands.command(name="close", description="Chiudi il ticket corrente")
    async def close(self, interaction: discord.Interaction):
        """Chiudi il ticket"""
        try:
            await interaction.response.send_message("🔒 Questo comando chiuderà il ticket...", ephemeral=True)
        except Exception as e:
            logger.error(f"Errore close: {e}")

    @app_commands.command(name="ban", description="Banna un utente")
    @app_commands.describe(utente="Utente da bannare", motivo="Motivo del ban")
    async def ban(self, interaction: discord.Interaction, utente: discord.Member, motivo: str = "Nessun motivo"):
        """Banna un utente"""
        try:
            # Verifica permessi
            if not interaction.user.guild_permissions.ban_members:
                await interaction.response.send_message("❌ Non hai i permessi per bannare!", ephemeral=True)
                return
                
            await utente.ban(reason=motivo)
            embed = discord.Embed(
                title="🔨 Utente Bannato",
                description=f"**Utente:** {utente.mention}\n**Motivo:** {motivo}",
                color=0xff0000
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Errore ban: {e}")
            await interaction.response.send_message("❌ Errore nel ban", ephemeral=True)

    @app_commands.command(name="kick", description="Espelli un utente")
    @app_commands.describe(utente="Utente da espellere", motivo="Motivo dell'espulsione")
    async def kick(self, interaction: discord.Interaction, utente: discord.Member, motivo: str = "Nessun motivo"):
        """Espelli un utente"""
        try:
            if not interaction.user.guild_permissions.kick_members:
                await interaction.response.send_message("❌ Non hai i permessi per espellere!", ephemeral=True)
                return
                
            await utente.kick(reason=motivo)
            embed = discord.Embed(
                title="👢 Utente Espulso",
                description=f"**Utente:** {utente.mention}\n**Motivo:** {motivo}",
                color=0xffa500
            )
            await interaction.response.send_message(embed=embed)
            
        except Exception as e:
            logger.error(f"Errore kick: {e}")
            await interaction.response.send_message("❌ Errore nell'espulsione", ephemeral=True)

    @app_commands.command(name="clear", description="Cancella messaggi")
    @app_commands.describe(quantita="Numero di messaggi da cancellare (1-100)")
    async def clear(self, interaction: discord.Interaction, quantita: int):
        """Cancella messaggi"""
        try:
            if not interaction.user.guild_permissions.manage_messages:
                await interaction.response.send_message("❌ Non hai i permessi per cancellare messaggi!", ephemeral=True)
                return
                
            if quantita < 1 or quantita > 100:
                await interaction.response.send_message("❌ Inserisci un numero tra 1 e 100!", ephemeral=True)
                return
            
            await interaction.response.defer(ephemeral=True)
            deleted = await interaction.channel.purge(limit=quantita)
            await interaction.followup.send(f"✅ Cancellati {len(deleted)} messaggi!", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Errore clear: {e}")
            await interaction.followup.send("❌ Errore nella cancellazione", ephemeral=True)

async def setup(bot):
    await bot.add_cog(TicketManager(bot))
    logger.info("✅ TicketManager cog caricato!")
