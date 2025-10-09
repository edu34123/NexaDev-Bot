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
                "bot_creator": {"label": "🤖 Crea Bot", "style": discord.ButtonStyle.primary},
                "server_creator": {"label": "🖥️ Crea Server", "style": discord.ButtonStyle.success},
                "both_creator": {"label": "⚡ Bot & Server", "style": discord.ButtonStyle.secondary},
                "partnership": {"label": "🤝 Partnership", "style": discord.ButtonStyle.danger}
            },
            "en": {
                "bot_creator": {"label": "🤖 Create Bot", "style": discord.ButtonStyle.primary},
                "server_creator": {"label": "🖥️ Create Server", "style": discord.ButtonStyle.success},
                "both_creator": {"label": "⚡ Bot & Server", "style": discord.ButtonStyle.secondary},
                "partnership": {"label": "🤝 Partnership", "style": discord.ButtonStyle.danger}
            }
        }
        
        config = button_configs.get(language, button_configs["it"])
        
        # Crea i pulsanti con le label corrette
        self.add_item(TicketButton("bot_creator", config["bot_creator"]["label"], config["bot_creator"]["style"], f"bot_creator_{language}", language))
        self.add_item(TicketButton("server_creator", config["server_creator"]["label"], config["server_creator"]["style"], f"server_creator_{language}", language))
        self.add_item(TicketButton("both_creator", config["both_creator"]["label"], config["both_creator"]["style"], f"both_creator_{language}", language))
        self.add_item(TicketButton("partnership", config["partnership"]["label"], config["partnership"]["style"], f"partnership_{language}", language))

class TicketButton(ui.Button):
    def __init__(self, button_type: str, label: str, style: discord.ButtonStyle, custom_id: str, language: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
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
        
        # Crea il canale ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }
        
        # Nomi dei tipi di ticket per il nome del canale
        type_names = {
            "it": {
                "bot_creator": "creazione-bot",
                "server_creator": "creazione-server",
                "both_creator": "bot-e-server", 
                "partnership": "partnership"
            },
            "en": {
                "bot_creator": "bot-creation",
                "server_creator": "server-creation",
                "both_creator": "bot-and-server",
                "partnership": "partnership"
            }
        }
        
        lang_type_names = type_names.get(language, type_names["it"])
        channel_name = f"{lang_type_names[ticket_type]}-{interaction.user.name}"[:100]
        
        channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            topic=f"Ticket {ticket_type} - {language.upper()} - {interaction.user.display_name}"
        )
        
        # Testi multilingua
        texts = {
            "it": {
                "bot_creator": {
                    "title": "🤖 Ticket Creazione Bot",
                    "description": "Grazie per aver aperto un ticket per la creazione di un bot!\n\n**Per favore specifica:**\n• Tipo di bot desiderato\n• Funzionalità richieste\n• Budget (se applicabile)\n• Tempistiche"
                },
                "server_creator": {
                    "title": "🖥️ Ticket Creazione Server", 
                    "description": "Grazie per aver aperto un ticket per la creazione di un server!\n\n**Per favore specifica:**\n• Tipo di server\n• Numero di membri\n• Funzionalità speciali\n• Budget (se applicabile)"
                },
                "both_creator": {
                    "title": "⚡ Ticket Bot & Server",
                    "description": "Grazie per aver aperto un ticket per entrambi i servizi!\n\n**Per favore specifica:**\n• Tipo di progetto\n• Funzionalità richieste\n• Budget (se applicabile)\n• Tempistiche"
                },
                "partnership": {
                    "title": "🤝 Ticket Partnership",
                    "description": "Grazie per aver aperto un ticket per partnership!\n\n**Per favore specifica:**\n• Tipo di partnership\n• Il tuo server/progetto\n• Cosa offri\n• Cosa cerchi"
                },
                "created_by": "Creato da",
                "type": "Tipo",
                "language": "Lingua",
                "instructions": "📋 **Istruzioni:**\n• Descrivi dettagliatamente la tua richiesta\n• Fornisci tutte le informazioni necessarie\n• Lo staff ti risponderà al più presto",
                "success": "✅ Ticket creato! {channel.mention}"
            },
            "en": {
                "bot_creator": {
                    "title": "🤖 Bot Creation Ticket",
                    "description": "Thank you for opening a bot creation ticket!\n\n**Please specify:**\n• Type of bot needed\n• Required features\n• Budget (if applicable)\n• Timeline"
                },
                "server_creator": {
                    "title": "🖥️ Server Creation Ticket",
                    "description": "Thank you for opening a server creation ticket!\n\n**Please specify:**\n• Server type\n• Member count\n• Special features\n• Budget (if applicable)"
                },
                "both_creator": {
                    "title": "⚡ Bot & Server Ticket",
                    "description": "Thank you for opening a ticket for both services!\n\n**Please specify:**\n• Project type\n• Required features\n• Budget (if applicable)\n• Timeline"
                },
                "partnership": {
                    "title": "🤝 Partnership Ticket", 
                    "description": "Thank you for opening a partnership ticket!\n\n**Please specify:**\n• Partnership type\n• Your server/project\n• What you offer\n• What you're looking for"
                },
                "created_by": "Created by",
                "type": "Type",
                "language": "Language", 
                "instructions": "📋 **Instructions:**\n• Describe your request in detail\n• Provide all necessary information\n• Staff will respond as soon as possible",
                "success": "✅ Ticket created! {channel.mention}"
            }
        }
        
        lang_texts = texts.get(language, texts["it"])
        ticket_texts = lang_texts.get(ticket_type, lang_texts["bot_creator"])
        
        # Embed del ticket
        embed = discord.Embed(
            title=ticket_texts["title"],
            description=ticket_texts["description"],
            color=discord.Color.blue()
        )
        embed.add_field(name=lang_texts["created_by"], value=interaction.user.mention, inline=True)
        embed.add_field(name=lang_texts["type"], value=self._get_ticket_type_name(ticket_type, language), inline=True)
        embed.add_field(name=lang_texts["language"], value="Italiano" if language == "it" else "English", inline=True)
        
        embed.add_field(
            name=lang_texts["instructions"],
            value=" ",
            inline=False
        )
        
        view = TicketManagementView(language)
        
        await channel.send(f"{staff_role.mention} {interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(lang_texts["success"].format(channel=channel), ephemeral=True)
    
    def _get_ticket_type_name(self, ticket_type: str, language: str) -> str:
        """Restituisce il nome del tipo di ticket nella lingua corretta"""
        type_names = {
            "it": {
                "bot_creator": "Creazione Bot",
                "server_creator": "Creazione Server",
                "both_creator": "Bot & Server",
                "partnership": "Partnership"
            },
            "en": {
                "bot_creator": "Bot Creation",
                "server_creator": "Server Creation", 
                "both_creator": "Bot & Server",
                "partnership": "Partnership"
            }
        }
        
        lang_names = type_names.get(language, type_names["it"])
        return lang_names.get(ticket_type, "Unknown")

class TicketManagementView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
        # Testi multilingua per i pulsanti
        button_texts = {
            "it": {
                "claim": {"label": "👤 Prendi in Carico", "style": discord.ButtonStyle.success},
                "close": {"label": "🔒 Chiudi Ticket", "style": discord.ButtonStyle.danger}
            },
            "en": {
                "claim": {"label": "👤 Claim Ticket", "style": discord.ButtonStyle.success},
                "close": {"label": "🔒 Close Ticket", "style": discord.ButtonStyle.danger}
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
                "title": "👤 Ticket Preso in Carico",
                "description": f"Il ticket è stato preso in carico da {interaction.user.mention}"
            },
            "en": {
                "title": "👤 Ticket Claimed",
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
                "title": "🔒 Ticket Chiuso",
                "description": "Il ticket verrà chiuso in 5 secondi..."
            },
            "en": {
                "title": "🔒 Ticket Closed",
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
            title="🎫 NexaDev - Sistema Ticket",
            description="**Scegli il tipo di assistenza di cui hai bisogno:**\n*Ticket privati e riservati*",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🤖 Crea Bot",
            value="Richiedi la creazione di un bot personalizzato",
            inline=True
        )
        embed.add_field(
            name="🖥️ Crea Server", 
            value="Richiedi la creazione di un server Discord",
            inline=True
        )
        embed.add_field(
            name=" ",
            value=" ",
            inline=True
        )
        embed.add_field(
            name="⚡ Bot & Server",
            value="Richiedi entrambi i servizi",
            inline=True
        )
        embed.add_field(
            name="🤝 Partnership", 
            value="Richiedi una partnership",
            inline=True
        )
        
        embed.set_footer(text="Clicca su un pulsante per aprire un ticket privato")
        
        view = TicketView("it")
        await interaction.response.send_message(embed=embed, view=view)
    
    @discord.app_commands.command(name="setup_tickets_eng", description="Setup ticket system in English")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets_eng(self, interaction: discord.Interaction):
        """Setup ticket system in English"""
        
        embed = discord.Embed(
            title="🎫 NexaDev - Ticket System",
            description="**Choose the type of assistance you need:**\n*Private and confidential tickets*",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🤖 Create Bot",
            value="Request creation of a custom bot",
            inline=True
        )
        embed.add_field(
            name="🖥️ Create Server",
            value="Request creation of a Discord server", 
            inline=True
        )
        embed.add_field(
            name=" ",
            value=" ",
            inline=True
        )
        embed.add_field(
            name="⚡ Bot & Server",
            value="Request both services",
            inline=True
        )
        embed.add_field(
            name="🤝 Partnership",
            value="Request a partnership",
            inline=True
        )
        
        embed.set_footer(text="Click a button to open a private ticket")
        
        view = TicketView("en")
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
