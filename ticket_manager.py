import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import os
import logging
import asyncio

logger = logging.getLogger(__name__)

class TicketView(View):
    def __init__(self):
        super().__init__(timeout=None)
        
    @discord.ui.button(label="Bot Creator", style=discord.ButtonStyle.primary, emoji="🤖", custom_id="ticket_bot")
    async def bot_creator(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🎫 Creazione ticket Bot Creator...", ephemeral=True)
        
    @discord.ui.button(label="Server Creator", style=discord.ButtonStyle.primary, emoji="🌐", custom_id="ticket_server")
    async def server_creator(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🎫 Creazione ticket Server Creator...", ephemeral=True)
        
    @discord.ui.button(label="Server/Bot", style=discord.ButtonStyle.primary, emoji="⚡", custom_id="ticket_both")
    async def both_creator(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🎫 Creazione ticket Server/Bot Creator...", ephemeral=True)
        
    @discord.ui.button(label="Partnership", style=discord.ButtonStyle.success, emoji="🤝", custom_id="ticket_partnership")
    async def partnership(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🎫 Creazione ticket Partnership...", ephemeral=True)
        
    @discord.ui.button(label="Segnalazione", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="ticket_report")
    async def segnalazione(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("🚨 Creazione ticket Segnalazione...", ephemeral=True)

class TicketManager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("✅ TicketManager inizializzato")

    @app_commands.command(name="setup_tickets", description="Setup del sistema di ticket")
    @app_commands.default_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup del sistema di ticket"""
        try:
            # Rispondi immediatamente
            await interaction.response.send_message("🔄 Creando il pannello ticket...", ephemeral=True)
            
            # Crea l'embed
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

            # Crea la view con i bottoni
            view = TicketView()
            
            # Invia il messaggio nel canale
            await interaction.channel.send(embed=embed, view=view)
            
            # Modifica la risposta iniziale
            await interaction.edit_original_response(content="✅ Pannello ticket creato con successo!")
            
            logger.info(f"Sistema ticket setup da {interaction.user}")

        except Exception as e:
            logger.error(f"Errore setup tickets: {e}")
            await interaction.edit_original_response(content=f"❌ Errore: {e}")

async def setup(bot):
    # Carica la cog
    cog = TicketManager(bot)
    await bot.add_cog(cog)
    
    # Aggiungi le view persistenti
    bot.add_view(TicketView())
    
    logger.info("✅ TicketManager cog caricato con views persistenti!")
