import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import logging
import asyncio

logger = logging.getLogger(__name__)

# View per i ticket italiani
class TicketViewIT(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Creazione Server e Bot", style=discord.ButtonStyle.primary, emoji="⚡", custom_id="ticket_both_it")
    async def both_it(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "server-bot", "it")
    
    @discord.ui.button(label="Creazione Server", style=discord.ButtonStyle.primary, emoji="🌐", custom_id="ticket_server_it")
    async def server_it(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "server", "it")
    
    @discord.ui.button(label="Creazione Bot", style=discord.ButtonStyle.primary, emoji="🤖", custom_id="ticket_bot_it")
    async def bot_it(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "bot", "it")
    
    @discord.ui.button(label="Partnership", style=discord.ButtonStyle.success, emoji="🤝", custom_id="ticket_partnership_it")
    async def partnership_it(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "partnership", "it")
    
    @discord.ui.button(label="Segnalazione", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="ticket_report_it")
    async def report_it(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "report", "it")
    
    @discord.ui.button(label="Richiesta CEO", style=discord.ButtonStyle.blurple, emoji="👑", custom_id="ticket_ceo_it")
    async def ceo_it(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "ceo", "it")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild = interaction.guild
            category = guild.get_channel(1426245729193820191)  # tickets_category
            
            if not category:
                await interaction.followup.send("❌ Categoria ticket non trovata", ephemeral=True)
                return

            # Nome del canale
            type_names = {
                "server-bot": "server-bot", "server": "server", "bot": "bot",
                "partnership": "partnership", "report": "segnalazione", "ceo": "ceo"
            }
            
            channel_name = f"{type_names[ticket_type]}-{interaction.user.name}".lower()[:100]
            
            # Verifica se esiste già
            for channel in category.channels:
                if channel.name == channel_name:
                    await interaction.followup.send("❌ Hai già un ticket aperto!", ephemeral=True)
                    return

            # Permessi
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            }

            # Crea canale
            ticket_channel = await category.create_text_channel(
                name=channel_name,
                overwrites=overwrites
            )

            # Embed del ticket
            type_titles = {
                "server-bot": "Creazione Server e Bot",
                "server": "Creazione Server", 
                "bot": "Creazione Bot",
                "partnership": "Partnership",
                "report": "Segnalazione",
                "ceo": "Richiesta CEO"
            }
            
            embed = discord.Embed(
                title=f"🎫 {type_titles[ticket_type]}",
                description=f"**Creato da:** {interaction.user.mention}",
                color=0x00ff00
            )
            
            # View per claim e chiusura
            ticket_view = TicketActionsView()
            
            await ticket_channel.send(
                content=f"{interaction.user.mention}",
                embed=embed,
                view=ticket_view
            )
            
            await interaction.followup.send(f"✅ Ticket creato: {ticket_channel.mention}", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Errore creazione ticket IT: {e}")
            await interaction.followup.send("❌ Errore nella creazione del ticket", ephemeral=True)

# View per i ticket inglesi
class TicketViewENG(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Server & Bot Creation", style=discord.ButtonStyle.primary, emoji="⚡", custom_id="ticket_both_eng")
    async def both_eng(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "server-bot", "eng")
    
    @discord.ui.button(label="Server Creation", style=discord.ButtonStyle.primary, emoji="🌐", custom_id="ticket_server_eng")
    async def server_eng(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "server", "eng")
    
    @discord.ui.button(label="Bot Creation", style=discord.ButtonStyle.primary, emoji="🤖", custom_id="ticket_bot_eng")
    async def bot_eng(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "bot", "eng")
    
    @discord.ui.button(label="Partnership", style=discord.ButtonStyle.success, emoji="🤝", custom_id="ticket_partnership_eng")
    async def partnership_eng(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "partnership", "eng")
    
    @discord.ui.button(label="Report", style=discord.ButtonStyle.danger, emoji="🚨", custom_id="ticket_report_eng")
    async def report_eng(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "report", "eng")
    
    @discord.ui.button(label="CEO Request", style=discord.ButtonStyle.blurple, emoji="👑", custom_id="ticket_ceo_eng")
    async def ceo_eng(self, interaction: discord.Interaction, button: Button):
        await self.create_ticket(interaction, "ceo", "eng")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        try:
            await interaction.response.defer(ephemeral=True)
            
            guild = interaction.guild
            category = guild.get_channel(1426245729193820191)  # tickets_category
            
            if not category:
                await interaction.followup.send("❌ Ticket category not found", ephemeral=True)
                return

            # Channel name
            type_names = {
                "server-bot": "server-bot", "server": "server", "bot": "bot",
                "partnership": "partnership", "report": "report", "ceo": "ceo"
            }
            
            channel_name = f"{type_names[ticket_type]}-{interaction.user.name}".lower()[:100]
            
            # Check if exists
            for channel in category.channels:
                if channel.name == channel_name:
                    await interaction.followup.send("❌ You already have an open ticket!", ephemeral=True)
                    return

            # Permissions
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            }

            # Create channel
            ticket_channel = await category.create_text_channel(
                name=channel_name,
                overwrites=overwrites
            )

            # Ticket embed
            type_titles = {
                "server-bot": "Server & Bot Creation",
                "server": "Server Creation", 
                "bot": "Bot Creation",
                "partnership": "Partnership",
                "report": "Report",
                "ceo": "CEO Request"
            }
            
            embed = discord.Embed(
                title=f"🎫 {type_titles[ticket_type]}",
                description=f"**Created by:** {interaction.user.mention}",
                color=0x00ff00
            )
            
            # View for claim and close
            ticket_view = TicketActionsView()
            
            await ticket_channel.send(
                content=f"{interaction.user.mention}",
                embed=embed,
                view=ticket_view
            )
            
            await interaction.followup.send(f"✅ Ticket created: {ticket_channel.mention}", ephemeral=True)
            
        except Exception as e:
            logger.error(f"Error creating ticket ENG: {e}")
            await interaction.followup.send("❌ Error creating ticket", ephemeral=True)

# View per le azioni nel ticket
class TicketActionsView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Claim", style=discord.ButtonStyle.success, emoji="👤", custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: Button):
        # Verifica se è staff
        if not any(role.permissions.manage_messages for role in interaction.user.roles):
            await interaction.response.send_message("❌ Solo lo staff può claimare i ticket!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="✅ Ticket Claimed",
            description=f"**Staff:** {interaction.user.mention}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
        button.disabled = True
        await interaction.message.edit(view=self)
    
    @discord.ui.button(label="Chiudi", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        # Verifica permessi
        if not any(role.permissions.manage_messages for role in interaction.user.roles):
            await interaction.response.send_message("❌ Solo lo staff può chiudere i ticket!", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🔒 Chiusura Ticket",
            description="Il ticket verrà chiuso in 5 secondi...",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Aggiungi le view persistenti
        self.bot.add_view(TicketViewIT())
        self.bot.add_view(TicketViewENG())
        self.bot.add_view(TicketActionsView())
        logger.info("✅ Ticket views caricate")

    @app_commands.command(name="setup_tickets", description="Setup sistema ticket")
    @app_commands.default_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup dei pannelli ticket"""
        try:
            await interaction.response.send_message("🔄 Setup ticket in corso...", ephemeral=True)
            
            # Canale italiano
            channel_it = self.bot.get_channel(1423755447445225554)
            if channel_it:
                embed_it = discord.Embed(
                    title="🎫 NexaDev - Supporto Ticket",
                    description="Seleziona il tipo di assistenza di cui hai bisogno:",
                    color=0x00ff00
                )
                embed_it.add_field(name="⚡ Creazione Server e Bot", value="Richiedi la creazione di server e bot", inline=False)
                embed_it.add_field(name="🌐 Creazione Server", value="Richiedi solo la creazione server", inline=False)
                embed_it.add_field(name="🤖 Creazione Bot", value="Richiedi solo la creazione bot", inline=False)
                embed_it.add_field(name="🤝 Partnership", value="Richiedi una partnership", inline=False)
                embed_it.add_field(name="🚨 Segnalazione", value="Segnala un problema", inline=False)
                embed_it.add_field(name="👑 Richiesta CEO", value="Richiedi l'intervento del CEO", inline=False)
                
                await channel_it.purge(limit=10)
                await channel_it.send(embed=embed_it, view=TicketViewIT())
            
            # Canale inglese
            channel_eng = self.bot.get_channel(1423395942094344223)
            if channel_eng:
                embed_eng = discord.Embed(
                    title="🎫 NexaDev - Ticket Support",
                    description="Select the type of assistance you need:",
                    color=0x00ff00
                )
                embed_eng.add_field(name="⚡ Server & Bot Creation", value="Request server and bot creation", inline=False)
                embed_eng.add_field(name="🌐 Server Creation", value="Request only server creation", inline=False)
                embed_eng.add_field(name="🤖 Bot Creation", value="Request only bot creation", inline=False)
                embed_eng.add_field(name="🤝 Partnership", value="Request a partnership", inline=False)
                embed_eng.add_field(name="🚨 Report", value="Report an issue", inline=False)
                embed_eng.add_field(name="👑 CEO Request", value="Request CEO intervention", inline=False)
                
                await channel_eng.purge(limit=10)
                await channel_eng.send(embed=embed_eng, view=TicketViewENG())
            
            await interaction.edit_original_response(content="✅ Setup ticket completato!")
            
        except Exception as e:
            logger.error(f"Errore setup tickets: {e}")
            await interaction.edit_original_response(content=f"❌ Errore: {e}")

async def setup(bot):
    await bot.add_cog(Tickets(bot))
