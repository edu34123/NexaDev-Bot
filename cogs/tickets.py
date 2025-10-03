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

class TicketView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
        # Imposta le label dei pulsanti in base alla lingua
        button_configs = {
            "it": {
                "bot_creator": {"label": "Bot Creator", "style": discord.ButtonStyle.primary},
                "server_creator": {"label": "Server Creator", "style": discord.ButtonStyle.success},
                "both_creator": {"label": "Server/Bot Creator", "style": discord.ButtonStyle.secondary},
                "partnership": {"label": "Partnership", "style": discord.ButtonStyle.danger}
            },
            "en": {
                "bot_creator": {"label": "Bot Creator", "style": discord.ButtonStyle.primary},
                "server_creator": {"label": "Server Creator", "style": discord.ButtonStyle.success},
                "both_creator": {"label": "Server/Bot Creator", "style": discord.ButtonStyle.secondary},
                "partnership": {"label": "Partnership", "style": discord.ButtonStyle.danger}
            }
        }
        
        config = button_configs.get(language, button_configs["it"])
        
        # Crea i pulsanti con le label corrette
        self.add_item(TicketButton("bot_creator", config["bot_creator"]["label"], config["bot_creator"]["style"], "bot_creator", language))
        self.add_item(TicketButton("server_creator", config["server_creator"]["label"], config["server_creator"]["style"], "server_creator", language))
        self.add_item(TicketButton("both_creator", config["both_creator"]["label"], config["both_creator"]["style"], "both_creator", language))
        self.add_item(TicketButton("partnership", config["partnership"]["label"], config["partnership"]["style"], "partnership", language))

class TicketButton(ui.Button):
    def __init__(self, button_type: str, label: str, style: discord.ButtonStyle, custom_id: str, language: str):
        super().__init__(label=label, style=style, custom_id=f"{custom_id}_{language}")
        self.button_type = button_type
        self.language = language
    
    async def callback(self, interaction: discord.Interaction):
        await self.create_ticket(interaction, self.button_type, self.language)
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        guild = interaction.guild
        staff_role_id = get_env_var('STAFF_ROLE_ID')
        
        if not staff_role_id:
            error_msg = {
                "it": "❌ Errore di configurazione: ruolo staff non configurato.",
                "en": "❌ Configuration error: staff role not configured."
            }
            await interaction.response.send_message(error_msg.get(language, error_msg["it"]), ephemeral=True)
            return
        
        staff_role = guild.get_role(int(staff_role_id))
        if not staff_role:
            error_msg = {
                "it": "❌ Ruolo staff non trovato nel server.",
                "en": "❌ Staff role not found in the server."
            }
            await interaction.response.send_message(error_msg.get(language, error_msg["it"]), ephemeral=True)
            return
        
        # Crea il canale ticket / Create ticket channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        # Nomi dei tipi di ticket per il nome del canale
        type_names = {
            "bot_creator": "Bot Creator",
            "server_creator": "Server Creator", 
            "both_creator": "Server-Bot Creator",
            "partnership": "Partnership"
        }
        
        channel_name = f"ticket-{type_names[ticket_type].lower().replace(' ', '-')}-{interaction.user.name}"
        channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            topic=f"Ticket {type_names[ticket_type]} - {language.upper()} - {interaction.user.display_name}"
        )
        
        # Testi multilingua / Multilingual texts
        texts = {
            "it": {
                "bot_creator": {
                    "title": "Ticket Bot Creator",
                    "description": "Grazie per aver aperto un ticket per la creazione di un bot!\nLo staff ti aiuterà al più presto."
                },
                "server_creator": {
                    "title": "Ticket Server Creator", 
                    "description": "Grazie per aver aperto un ticket per la creazione di un server!\nLo staff ti aiuterà al più presto."
                },
                "both_creator": {
                    "title": "Ticket Server/Bot Creator",
                    "description": "Grazie per aver aperto un ticket per entrambi i servizi!\nLo staff ti aiuterà al più presto."
                },
                "partnership": {
                    "title": "Ticket Partnership",
                    "description": "Grazie per aver aperto un ticket per partnership!\nLo staff ti aiuterà al più presto."
                },
                "created_by": "Creato da",
                "type": "Tipo",
                "language": "Lingua",
                "success": f"✅ Ticket creato! {channel.mention}"
            },
            "en": {
                "bot_creator": {
                    "title": "Bot Creator Ticket",
                    "description": "Thank you for opening a bot creation ticket!\nStaff will help you as soon as possible."
                },
                "server_creator": {
                    "title": "Server Creator Ticket",
                    "description": "Thank you for opening a server creation ticket!\nStaff will help you as soon as possible."
                },
                "both_creator": {
                    "title": "Server/Bot Creator Ticket",
                    "description": "Thank you for opening a ticket for both services!\nStaff will help you as soon as possible."
                },
                "partnership": {
                    "title": "Partnership Ticket", 
                    "description": "Thank you for opening a partnership ticket!\nStaff will help you as soon as possible."
                },
                "created_by": "Created by",
                "type": "Type",
                "language": "Language", 
                "success": f"✅ Ticket created! {channel.mention}"
            }
        }
        
        lang_texts = texts.get(language, texts["it"])
        ticket_texts = lang_texts.get(ticket_type, lang_texts["bot_creator"])
        
        # Embed del ticket / Ticket embed
        embed = discord.Embed(
            title=ticket_texts["title"],
            description=ticket_texts["description"],
            color=discord.Color.blue()
        )
        embed.add_field(name=lang_texts["created_by"], value=interaction.user.mention, inline=True)
        embed.add_field(name=lang_texts["type"], value=type_names[ticket_type], inline=True)
        embed.add_field(name=lang_texts["language"], value="Italiano" if language == "it" else "English", inline=True)
        
        view = TicketManagementView(language)
        
        await channel.send(f"{staff_role.mention} {interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(lang_texts["success"], ephemeral=True)

class TicketManagementView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
        # Testi multilingua per i pulsanti / Multilingual texts for buttons
        button_texts = {
            "it": {
                "claim": {"label": "Claim", "style": discord.ButtonStyle.success},
                "close": {"label": "Chiudi", "style": discord.ButtonStyle.danger}
            },
            "en": {
                "claim": {"label": "Claim", "style": discord.ButtonStyle.success},
                "close": {"label": "Close", "style": discord.ButtonStyle.danger}
            }
        }
        
        texts = button_texts.get(language, button_texts["it"])
        
        # Aggiungi pulsanti con le label corrette
        self.add_item(ManagementButton("claim", texts["claim"]["label"], texts["claim"]["style"], f"claim_ticket_{language}", language))
        self.add_item(ManagementButton("close", texts["close"]["label"], texts["close"]["style"], f"close_ticket_{language}", language))

class ManagementButton(ui.Button):
    def __init__(self, button_type: str, label: str, style: discord.ButtonStyle, custom_id: str, language: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.button_type = button_type
        self.language = language
    
    async def callback(self, interaction: discord.Interaction):
        if self.button_type == "claim":
            await self.claim_ticket(interaction)
        elif self.button_type == "close":
            await self.close_ticket(interaction)
    
    async def claim_ticket(self, interaction: discord.Interaction):
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
    
    async def close_ticket(self, interaction: discord.Interaction):
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
        # Registra tutte le view per entrambe le lingue
        self.bot.add_view(TicketView("it"))
        self.bot.add_view(TicketView("en"))
        self.bot.add_view(TicketManagementView("it"))
        self.bot.add_view(TicketManagementView("en"))
    
    @discord.app_commands.command(name="setup_tickets_ita", description="Setup del sistema di ticket in italiano")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets_ita(self, interaction: discord.Interaction):
        """Setup del sistema di ticket in italiano"""
        
        embed = discord.Embed(
            title="NexaDev - Supporto",
            description="Seleziona il tipo di assistenza di cui hai bisogno:",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Bot Creator", value="Richiedi la creazione di un bot", inline=True)
        embed.add_field(name="Server Creator", value="Richiedi la creazione di un server", inline=True)
        embed.add_field(name="Server/Bot Creator", value="Richiedi entrambi i servizi", inline=True)
        embed.add_field(name="Partnership", value="Richiedi una partnership", inline=True)
        
        view = TicketView("it")
        await interaction.response.send_message(embed=embed, view=view)
    
    @discord.app_commands.command(name="setup_tickets_eng", description="Setup ticket system in English")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets_eng(self, interaction: discord.Interaction):
        """Setup ticket system in English"""
        
        embed = discord.Embed(
            title="NexaDev - Support",
            description="Select the type of assistance you need:",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Bot Creator", value="Request bot creation", inline=True)
        embed.add_field(name="Server Creator", value="Request server creation", inline=True)
        embed.add_field(name="Server/Bot Creator", value="Request both services", inline=True)
        embed.add_field(name="Partnership", value="Request a partnership", inline=True)
        
        view = TicketView("en")
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
