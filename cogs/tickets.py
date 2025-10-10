import os
import discord
from discord.ext import commands
from discord import ui
import asyncio
import logging

logger = logging.getLogger(__name__)

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if not value and default is None:
        logger.warning(f"⚠️ Variabile {var_name} non trovata")
    return value or default

# ✅ VIEW SEMPLIFICATA E TESTATA
class SimpleTicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label='🚨 Segnala', style=discord.ButtonStyle.danger, custom_id='ticket_report')
    async def report_button(self, interaction: discord.Interaction, button: ui.Button):
        logger.info(f"🎯 Pulsante Segnala premuto da {interaction.user}")
        await self.create_ticket(interaction, "report")
    
    @ui.button(label='👑 Richiesta CEO', style=discord.ButtonStyle.success, custom_id='ticket_ceo')
    async def ceo_button(self, interaction: discord.Interaction, button: ui.Button):
        logger.info(f"🎯 Pulsante CEO premuto da {interaction.user}")
        await self.create_ticket(interaction, "ceo_request")
    
    @ui.button(label='🤖 Crea Bot', style=discord.ButtonStyle.primary, custom_id='ticket_bot')
    async def bot_button(self, interaction: discord.Interaction, button: ui.Button):
        logger.info(f"🎯 Pulsante Bot premuto da {interaction.user}")
        await self.create_ticket(interaction, "bot_creator")
    
    @ui.button(label='🖥️ Crea Server', style=discord.ButtonStyle.primary, custom_id='ticket_server')
    async def server_button(self, interaction: discord.Interaction, button: ui.Button):
        logger.info(f"🎯 Pulsante Server premuto da {interaction.user}")
        await self.create_ticket(interaction, "server_creator")
    
    @ui.button(label='🤝 Partnership', style=discord.ButtonStyle.secondary, custom_id='ticket_partnership')
    async def partnership_button(self, interaction: discord.Interaction, button: ui.Button):
        logger.info(f"🎯 Pulsante Partnership premuto da {interaction.user}")
        await self.create_ticket(interaction, "partnership")
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        try:
            logger.info(f"🎫 Creazione ticket {ticket_type} per {interaction.user}")
            
            # Ottieni la categoria
            category_id = get_env_var('TICKETS_CATEGORY_ID')
            if not category_id:
                await interaction.response.send_message("❌ Categoria ticket non configurata", ephemeral=True)
                return
            
            guild = interaction.guild
            category = guild.get_channel(int(category_id))
            if not category:
                await interaction.response.send_message("❌ Categoria ticket non trovata", ephemeral=True)
                return
            
            # Configura in base al tipo di ticket
            if ticket_type == "ceo_request":
                role_id = get_env_var('CEO_ROLE_ID')
                role_name = "CEO"
                color = discord.Color.gold()
                channel_name = f"ceo-{interaction.user.name}"
            elif ticket_type == "report":
                role_id = get_env_var('REPORT_ROLE_ID') 
                role_name = "Segnalazioni"
                color = discord.Color.red()
                channel_name = f"segnalazione-{interaction.user.name}"
            else:
                role_id = get_env_var('STAFF_ROLE_ID')
                role_name = "Staff"
                color = discord.Color.blue()
                channel_name = f"{ticket_type}-{interaction.user.name}"
            
            if not role_id:
                await interaction.response.send_message(f"❌ Ruolo {role_name} non configurato", ephemeral=True)
                return
            
            role = guild.get_role(int(role_id))
            if not role:
                await interaction.response.send_message(f"❌ Ruolo {role_name} non trovato", ephemeral=True)
                return
            
            # Crea il canale
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
                role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
            }
            
            channel = await guild.create_text_channel(
                name=channel_name[:100],
                category=category,
                overwrites=overwrites,
                topic=f"Ticket {ticket_type} - {interaction.user.display_name}"
            )
            
            logger.info(f"✅ Canale {channel.name} creato")
            
            # Crea embed di base
            embed = discord.Embed(
                title=f"🎫 Ticket {ticket_type.replace('_', ' ').title()}",
                description="Grazie per aver aperto un ticket! Lo staff ti aiuterà al più presto.",
                color=color
            )
            
            embed.add_field(name="👤 Creato da", value=interaction.user.mention, inline=True)
            embed.add_field(name="📊 Tipo", value=ticket_type.replace('_', ' ').title(), inline=True)
            embed.add_field(name="🕒 Creato il", value=discord.utils.format_dt(discord.utils.utcnow(), 'F'), inline=True)
            
            embed.add_field(
                name="📋 Istruzioni",
                value="• Descrivi il tuo problema/richiesta in dettaglio\n• Fornisci tutte le informazioni necessarie\n• Attendi la risposta dello staff",
                inline=False
            )
            
            # View per la gestione
            management_view = SimpleManagementView()
            
            # Invia il messaggio
            message = await channel.send(
                content=f"{role.mention} {interaction.user.mention}",
                embed=embed,
                view=management_view
            )
            
            logger.info(f"✅ Embed inviato nel canale {channel.name}")
            
            # Risposta all'utente
            await interaction.response.send_message(
                f"✅ Ticket creato! {channel.mention}",
                ephemeral=True
            )
            
        except Exception as e:
            logger.error(f"❌ Errore creazione ticket: {e}")
            await interaction.response.send_message(
                f"❌ Errore durante la creazione del ticket: {e}",
                ephemeral=True
            )

# ✅ VIEW PER LA GESTIONE SEMPLIFICATA
class SimpleManagementView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @ui.button(label='👤 Prendi in Carico', style=discord.ButtonStyle.success, custom_id='claim_ticket')
    async def claim_ticket(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="👤 Ticket Preso in Carico",
            description=f"Il ticket è stato preso in carico da {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @ui.button(label='🔒 Chiudi Ticket', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
        embed = discord.Embed(
            title="🔒 Ticket Chiuso",
            description="Il ticket verrà chiuso in 5 secondi...",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
    
    @commands.Cog.listener()
    async def on_ready(self):
        # ✅ REGISTRA LE VIEW - ESSENZIALE!
        self.bot.add_view(SimpleTicketView())
        self.bot.add_view(SimpleManagementView())
        self.logger.info("✅ View ticket registrate correttamente")
    
    @discord.app_commands.command(name="setup_tickets", description="Setup del sistema di ticket")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup del sistema di ticket"""
        
        self.logger.info(f"🎯 Comando setup_tickets eseguito da {interaction.user}")
        
        embed = discord.Embed(
            title="🎫 Sistema Ticket",
            description="**Seleziona il tipo di ticket che vuoi aprire:**\n*I ticket sono privati e riservati*",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🚨 **Segnalazioni**",
            value="• **Segnala** - Problemi, abusi, violazioni",
            inline=False
        )
        
        embed.add_field(
            name="👑 **Richieste Speciali**",
            value="• **Richiesta CEO** - Questioni riservate per i CEO",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ **Servizi**",
            value="• **Crea Bot** - Sviluppo bot personalizzati\n• **Crea Server** - Creazione server Discord\n• **Partnership** - Collaborazioni e partnership",
            inline=False
        )
        
        embed.set_footer(text="Clicca su un pulsante per aprire un ticket privato")
        
        view = SimpleTicketView()
        
        try:
            await interaction.response.send_message(embed=embed, view=view)
            self.logger.info("✅ Messaggio di setup inviato correttamente")
        except Exception as e:
            self.logger.error(f"❌ Errore invio messaggio setup: {e}")
            await interaction.response.send_message(
                "❌ Errore durante l'invio del messaggio di setup",
                ephemeral=True
            )
    
    @discord.app_commands.command(name="test_ticket", description="Test del sistema ticket")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def test_ticket(self, interaction: discord.Interaction):
        """Comando di test"""
        
        embed = discord.Embed(
            title="🧪 Test Sistema Ticket",
            description="Questo è un messaggio di test per verificare che gli embed funzionino.",
            color=discord.Color.green()
        )
        
        embed.add_field(name="✅ Bot Online", value="Il bot è online e funzionante", inline=True)
        embed.add_field(name="📊 Comandi", value="I comandi slash sono sincronizzati", inline=True)
        embed.add_field(name="🎯 Pulsanti", value="I pulsanti dovrebbero funzionare", inline=True)
        
        view = SimpleTicketView()
        
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
    logger.info("✅ Cog Ticket caricata con successo!")
