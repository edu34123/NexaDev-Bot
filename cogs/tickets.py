import os
import discord
from discord.ext import commands
from discord import ui
import asyncio

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if not value and default is None:
        print(f"⚠️ Variabile {var_name} non trovata")
    return value or default

class LanguageSelect(ui.Select):
    def __init__(self, ticket_view):
        options = [
            discord.SelectOption(label="Italiano", value="it", emoji="🇮🇹"),
            discord.SelectOption(label="English", value="en", emoji="🇬🇧")
        ]
        super().__init__(placeholder="Seleziona lingua / Select language", options=options)
        self.ticket_view = ticket_view
    
    async def callback(self, interaction: discord.Interaction):
        await self.ticket_view.create_ticket(interaction, self.ticket_view.ticket_type, self.values[0])

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Bot Creator', style=discord.ButtonStyle.primary, custom_id='bot_creator')
    async def bot_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_language_selection(interaction, "Bot Creator")
    
    @discord.ui.button(label='Server Creator', style=discord.ButtonStyle.success, custom_id='server_creator')
    async def server_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_language_selection(interaction, "Server Creator")
    
    @discord.ui.button(label='Server/Bot Creator', style=discord.ButtonStyle.secondary, custom_id='both_creator')
    async def both_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_language_selection(interaction, "Server/Bot Creator")
    
    @discord.ui.button(label='Partnership', style=discord.ButtonStyle.danger, custom_id='partnership')
    async def partnership(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.show_language_selection(interaction, "Partnership")
    
    async def show_language_selection(self, interaction: discord.Interaction, ticket_type: str):
        self.ticket_type = ticket_type
        view = ui.View()
        view.add_item(LanguageSelect(self))
        
        embed = discord.Embed(
            title="Seleziona lingua / Select language",
            description="Scegli la lingua per il ticket / Choose the language for the ticket",
            color=discord.Color.blue()
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        guild = interaction.guild
        staff_role_id = get_env_var('STAFF_ROLE_ID')
        
        if not staff_role_id:
            await interaction.response.send_message(
                "❌ Errore di configurazione: ruolo staff non configurato.\n❌ Configuration error: staff role not configured.",
                ephemeral=True
            )
            return
        
        staff_role = guild.get_role(int(staff_role_id))
        if not staff_role:
            await interaction.response.send_message(
                "❌ Ruolo staff non trovato nel server.\n❌ Staff role not found in the server.",
                ephemeral=True
            )
            return
        
        # Crea il canale ticket / Create ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        channel_name = f"ticket-{ticket_type.lower().replace('/', '-')}-{interaction.user.name}"
        channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            topic=f"Ticket {ticket_type} - {language.upper()} - {interaction.user.display_name}"
        )
        
        # Testi multilingua / Multilingual texts
        texts = {
            "it": {
                "title": f"Ticket {ticket_type}",
                "description": f"Grazie per aver aperto un ticket {ticket_type}!\nLo staff ti aiuterà al più presto.",
                "created_by": "Creato da",
                "type": "Tipo",
                "language": "Lingua",
                "success": f"✅ Ticket creato! {channel.mention}"
            },
            "en": {
                "title": f"Ticket {ticket_type}",
                "description": f"Thank you for opening a {ticket_type} ticket!\nStaff will help you as soon as possible.",
                "created_by": "Created by",
                "type": "Type", 
                "language": "Language",
                "success": f"✅ Ticket created! {channel.mention}"
            }
        }
        
        lang_texts = texts.get(language, texts["it"])
        
        # Embed del ticket / Ticket embed
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.blue()
        )
        embed.add_field(name=lang_texts["created_by"], value=interaction.user.mention, inline=True)
        embed.add_field(name=lang_texts["type"], value=ticket_type, inline=True)
        embed.add_field(name=lang_texts["language"], value="Italiano" if language == "it" else "English", inline=True)
        
        view = TicketManagementView(language)
        
        await channel.send(f"{staff_role.mention} {interaction.user.mention}", embed=embed, view=view)
        await interaction.followup.send(lang_texts["success"], ephemeral=True)

class TicketManagementView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
        # Testi multilingua per i pulsanti / Multilingual texts for buttons
        button_texts = {
            "it": {
                "claim": "Claim",
                "close": "Chiudi"
            },
            "en": {
                "claim": "Claim", 
                "close": "Close"
            }
        }
        
        texts = button_texts.get(language, button_texts["it"])
        
        # Modifica i pulsanti con le label corrette / Modify buttons with correct labels
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.custom_id == 'claim_ticket':
                    item.label = texts["claim"]
                elif item.custom_id == 'close_ticket':
                    item.label = texts["close"]
    
    @discord.ui.button(label='Claim', style=discord.ButtonStyle.success, custom_id='claim_ticket')
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        texts = {
            "it": {
                "title": "Ticket Preso in Carico",
                "description": f"Il ticket è stato preso in carico da {interaction.user.mention}"
            },
            "en": {
                "title": "Ticket Claimed", 
                "description": f"The ticket has been claimed by {interaction.user.mention}"
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label='Close', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        texts = {
            "it": {
                "title": "Ticket Chiuso",
                "description": "Il ticket verrà chiuso in 5 secondi..."
            },
            "en": {
                "title": "Ticket Closed",
                "description": "The ticket will be closed in 5 seconds..."
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())
        # Registra le view per tutte le lingue / Register views for all languages
        self.bot.add_view(TicketManagementView("it"))
        self.bot.add_view(TicketManagementView("en"))
    
    @discord.app_commands.command(name="setup_tickets", description="Setup del sistema di ticket / Setup ticket system")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup del sistema di ticket in multilingua / Multilingual ticket system setup"""
        
        # Embed bilingue / Bilingual embed
        embed = discord.Embed(
            title="NexaDev - Supporto / Support",
            description="Seleziona il tipo di assistenza di cui hai bisogno:\nSelect the type of assistance you need:",
            color=discord.Color.blue()
        )
        
        # Campi bilingui / Bilingual fields
        embed.add_field(
            name="Bot Creator", 
            value="Richiedi la creazione di un bot\nRequest bot creation", 
            inline=True
        )
        embed.add_field(
            name="Server Creator", 
            value="Richiedi la creazione di un server\nRequest server creation", 
            inline=True
        )
        embed.add_field(
            name="Server/Bot Creator", 
            value="Richiedi entrambi i servizi\nRequest both services", 
            inline=True
        )
        embed.add_field(
            name="Partnership", 
            value="Richiedi una partnership\nRequest a partnership", 
            inline=True
        )
        
        view = TicketView()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
