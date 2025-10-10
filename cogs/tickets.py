import os
import discord
from discord.ext import commands
from discord import ui
import asyncio
from ticket_manager import ticket_manager

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if not value and default is None:
        print(f"⚠️ Variabile {var_name} non trovata")
    return value or default

class TicketView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
        # Configurazione pulsanti in base alla lingua
        button_configs = {
            "it": {
                "report": {"label": "🚨 Segnala", "style": discord.ButtonStyle.danger},
                "ceo_request": {"label": "👑 Richiesta CEO", "style": discord.ButtonStyle.success},
                "bot_creator": {"label": "🤖 Crea Bot", "style": discord.ButtonStyle.primary},
                "server_creator": {"label": "🖥️ Crea Server", "style": discord.ButtonStyle.primary},
                "partnership": {"label": "🤝 Partnership", "style": discord.ButtonStyle.secondary}
            },
            "en": {
                "report": {"label": "🚨 Report", "style": discord.ButtonStyle.danger},
                "ceo_request": {"label": "👑 CEO Request", "style": discord.ButtonStyle.success},
                "bot_creator": {"label": "🤖 Create Bot", "style": discord.ButtonStyle.primary},
                "server_creator": {"label": "🖥️ Create Server", "style": discord.ButtonStyle.primary},
                "partnership": {"label": "🤝 Partnership", "style": discord.ButtonStyle.secondary}
            }
        }
        
        config = button_configs.get(language, button_configs["it"])
        
        # Crea i pulsanti
        self.add_item(TicketButton("report", config["report"]["label"], config["report"]["style"], f"report_{language}", language))
        self.add_item(TicketButton("ceo_request", config["ceo_request"]["label"], config["ceo_request"]["style"], f"ceo_request_{language}", language))
        self.add_item(TicketButton("bot_creator", config["bot_creator"]["label"], config["bot_creator"]["style"], f"bot_creator_{language}", language))
        self.add_item(TicketButton("server_creator", config["server_creator"]["label"], config["server_creator"]["style"], f"server_creator_{language}", language))
        self.add_item(TicketButton("partnership", config["partnership"]["label"], config["partnership"]["style"], f"partnership_{language}", language))

class TicketButton(ui.Button):
    def __init__(self, ticket_type: str, label: str, style: discord.ButtonStyle, custom_id: str, language: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.ticket_type = ticket_type
        self.language = language
    
    async def callback(self, interaction: discord.Interaction):
        await self.create_ticket(interaction, self.ticket_type, self.language)
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        guild = interaction.guild
        
        # Ottieni la categoria dove creare i ticket
        category_id = get_env_var('TICKETS_CATEGORY_ID')
        if not category_id:
            error_msg = {
                "it": "❌ Errore: categoria ticket non configurata.",
                "en": "❌ Error: tickets category not configured."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        category = guild.get_channel(int(category_id))
        if not category or not isinstance(category, discord.CategoryChannel):
            error_msg = {
                "it": "❌ Categoria ticket non trovata.",
                "en": "❌ Tickets category not found."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        if ticket_type == "ceo_request":
            await self.create_ceo_ticket(interaction, language, category)
        elif ticket_type == "report":
            await self.create_report_ticket(interaction, language, category)
        else:
            await self.create_normal_ticket(interaction, ticket_type, language, category)
    
    async def create_ceo_ticket(self, interaction: discord.Interaction, language: str, category: discord.CategoryChannel):
        """Crea ticket CEO"""
        guild = interaction.guild
        ceo_role_id = get_env_var('CEO_ROLE_ID')
        
        if not ceo_role_id:
            error_msg = {
                "it": "❌ Errore: ruolo CEO non configurato.",
                "en": "❌ Error: CEO role not configured."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        ceo_role = guild.get_role(int(ceo_role_id))
        if not ceo_role:
            error_msg = {
                "it": "❌ Ruolo CEO non trovato.",
                "en": "❌ CEO role not found."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        # Crea canale privato solo per CEO nella categoria specificata
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            ceo_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }
        
        channel_name = f"ceo-request-{interaction.user.name}"[:100]
        
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"CEO Request - {language.upper()} - {interaction.user.display_name}"
        )
        
        # Testi per ticket CEO
        texts = {
            "it": {
                "title": "👑 Richiesta CEO",
                "description": "**Richiesta riservata per i CEO**\n\nDescrivi la tua richiesta in dettaglio. Solo i CEO potranno vedere questo ticket.",
                "created_by": "Creato da",
                "type": "Tipo",
                "language": "Lingua",
                "instructions": "📋 **Istruzioni:**\n• Descrivi la tua richiesta in modo dettagliato\n• Fornisci tutte le informazioni necessarie\n• I CEO ti risponderanno presto",
                "success": "✅ Ticket CEO creato! {channel.mention}"
            },
            "en": {
                "title": "👑 CEO Request",
                "description": "**Confidential request for CEOs**\n\nDescribe your request in detail. Only CEOs will be able to see this ticket.",
                "created_by": "Created by",
                "type": "Type",
                "language": "Language",
                "instructions": "📋 **Instructions:**\n• Describe your request in detail\n• Provide all necessary information\n• CEOs will respond soon",
                "success": "✅ CEO ticket created! {channel.mention}"
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.gold()
        )
        
        embed.add_field(name=lang_texts["created_by"], value=interaction.user.mention, inline=True)
        embed.add_field(name=lang_texts["type"], value="Richiesta CEO" if self.language == "it" else "CEO Request", inline=True)
        embed.add_field(name=lang_texts["language"], value="Italiano" if self.language == "it" else "English", inline=True)
        
        embed.add_field(
            name=lang_texts["instructions"],
            value=" ",
            inline=False
        )
        
        embed.add_field(
            name="🔒 **Privato**",
            value="Questo ticket è visibile solo a te e ai CEO.",
            inline=False
        )
        
        view = TicketManagementView(self.language)
        
        message = await channel.send(f"{ceo_role.mention} {interaction.user.mention}", embed=embed, view=view)
        
        # SALVA IL TICKET NEL DATABASE
        ticket_data = {
            "channel_id": channel.id,
            "message_id": message.id,
            "ticket_type": "ceo_request",
            "language": self.language,
            "user_id": interaction.user.id,
            "guild_id": guild.id,
            "role_id": ceo_role_id,
            "category_id": category.id,
            "embed_data": {
                "title": lang_texts["title"],
                "description": lang_texts["description"],
                "color": discord.Color.gold().value
            }
        }
        ticket_manager.add_ticket(channel.id, ticket_data)
        
        await interaction.response.send_message(lang_texts["success"].format(channel=channel), ephemeral=True)
    
    async def create_report_ticket(self, interaction: discord.Interaction, language: str, category: discord.CategoryChannel):
        """Crea ticket segnalazione"""
        guild = interaction.guild
        security_role_id = get_env_var('REPORT_ROLE_ID')
        
        if not security_role_id:
            error_msg = {
                "it": "❌ Errore: ruolo segnalazioni non configurato.",
                "en": "❌ Error: report role not configured."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        security_role = guild.get_role(int(security_role_id))
        if not security_role:
            error_msg = {
                "it": "❌ Ruolo segnalazioni non trovato.",
                "en": "❌ Report role not found."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        # Crea canale segnalazione nella categoria specificata
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            security_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }
        
        channel_name = f"segnalazione-{interaction.user.name}"[:100]
        
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Segnalazione - {language.upper()} - {interaction.user.display_name}"
        )
        
        # Testi per segnalazione
        texts = {
            "it": {
                "title": "🚨 Segnalazione",
                "description": "Grazie per aver aperto una segnalazione. Per favore fornisci:\n\n• **Descrizione dettagliata**\n• **Prove (screenshot, etc.)**\n• **Quando è successo**\n• **Utenti coinvolti**",
                "created_by": "Creato da",
                "type": "Tipo",
                "language": "Lingua",
                "instructions": "📋 **Istruzioni:**\n• Fornisci tutte le informazioni richieste\n• Carica le prove come screenshot\n• Sii dettagliato e preciso",
                "success": "✅ Segnalazione creata! {channel.mention}"
            },
            "en": {
                "title": "🚨 Report",
                "description": "Thank you for opening a report. Please provide:\n\n• **Detailed description**\n• **Evidence (screenshots, etc.)**\n• **When it happened**\n• **Users involved**",
                "created_by": "Created by",
                "type": "Type",
                "language": "Language",
                "instructions": "📋 **Instructions:**\n• Provide all requested information\n• Upload evidence as screenshots\n• Be detailed and precise",
                "success": "✅ Report created! {channel.mention}"
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.red()
        )
        
        embed.add_field(name=lang_texts["created_by"], value=interaction.user.mention, inline=True)
        embed.add_field(name=lang_texts["type"], value="Segnalazione" if self.language == "it" else "Report", inline=True)
        embed.add_field(name=lang_texts["language"], value="Italiano" if self.language == "it" else "English", inline=True)
        
        embed.add_field(
            name=lang_texts["instructions"],
            value=" ",
            inline=False
        )
        
        view = TicketManagementView(self.language)
        
        message = await channel.send(f"{security_role.mention} {interaction.user.mention}", embed=embed, view=view)
        
        # SALVA IL TICKET NEL DATABASE
        ticket_data = {
            "channel_id": channel.id,
            "message_id": message.id,
            "ticket_type": "report",
            "language": self.language,
            "user_id": interaction.user.id,
            "guild_id": guild.id,
            "role_id": security_role_id,
            "category_id": category.id,
            "embed_data": {
                "title": lang_texts["title"],
                "description": lang_texts["description"],
                "color": discord.Color.red().value
            }
        }
        ticket_manager.add_ticket(channel.id, ticket_data)
        
        await interaction.response.send_message(lang_texts["success"].format(channel=channel), ephemeral=True)
    
    async def create_normal_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str, category: discord.CategoryChannel):
        """Crea ticket normali"""
        guild = interaction.guild
        staff_role_id = get_env_var('STAFF_ROLE_ID')
        
        if not staff_role_id:
            error_msg = {
                "it": "❌ Errore: ruolo staff non configurato.",
                "en": "❌ Error: staff role not configured."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        staff_role = guild.get_role(int(staff_role_id))
        if not staff_role:
            error_msg = {
                "it": "❌ Ruolo staff non trovato.",
                "en": "❌ Staff role not found."
            }
            await interaction.response.send_message(error_msg.get(self.language, error_msg["it"]), ephemeral=True)
            return
        
        # Crea canale ticket normale nella categoria specificata
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }
        
        # Nomi dei tipi di ticket
        type_names = {
            "it": {
                "bot_creator": "creazione-bot",
                "server_creator": "creazione-server",
                "partnership": "partnership"
            },
            "en": {
                "bot_creator": "bot-creation",
                "server_creator": "server-creation",
                "partnership": "partnership"
            }
        }
        
        lang_type_names = type_names.get(self.language, type_names["it"])
        channel_name = f"{lang_type_names[ticket_type]}-{interaction.user.name}"[:100]
        
        channel = await guild.create_text_channel(
            name=channel_name,
            category=category,
            overwrites=overwrites,
            topic=f"Ticket {ticket_type} - {language.upper()} - {interaction.user.display_name}"
        )
        
        # Testi per ticket normali
        texts = {
            "it": {
                "bot_creator": {
                    "title": "🤖 Richiesta Bot",
                    "description": "Grazie per la richiesta! Descrivi il bot che desideri:\n\n• Tipo di bot\n• Funzionalità richieste\n• Budget e tempistiche"
                },
                "server_creator": {
                    "title": "🖥️ Richiesta Server",
                    "description": "Grazie per la richiesta! Descrivi il server che desideri:\n\n• Tipo di server\n• Numero di membri\n• Funzionalità speciali"
                },
                "partnership": {
                    "title": "🤝 Richiesta Partnership",
                    "description": "Grazie per la richiesta! Descrivi:\n\n• Tipo di partnership\n• Il tuo progetto\n• Cosa offri e cosa cerchi"
                },
                "created_by": "Creato da",
                "type": "Tipo",
                "language": "Lingua",
                "instructions": "📋 **Istruzioni:**\n• Descrivi dettagliatamente la tua richiesta\n• Fornisci tutte le informazioni necessarie",
                "success": "✅ Ticket creato! {channel.mention}"
            },
            "en": {
                "bot_creator": {
                    "title": "🤖 Bot Request",
                    "description": "Thank you for your request! Describe the bot you want:\n\n• Bot type\n• Required features\n• Budget and timeline"
                },
                "server_creator": {
                    "title": "🖥️ Server Request",
                    "description": "Thank you for your request! Describe the server you want:\n\n• Server type\n• Member count\n• Special features"
                },
                "partnership": {
                    "title": "🤝 Partnership Request",
                    "description": "Thank you for your request! Describe:\n\n• Partnership type\n• Your project\n• What you offer and seek"
                },
                "created_by": "Created by",
                "type": "Type",
                "language": "Language",
                "instructions": "📋 **Instructions:**\n• Describe your request in detail\n• Provide all necessary information",
                "success": "✅ Ticket created! {channel.mention}"
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        ticket_texts = lang_texts.get(ticket_type, lang_texts["bot_creator"])
        
        embed = discord.Embed(
            title=ticket_texts["title"],
            description=ticket_texts["description"],
            color=discord.Color.blue()
        )
        
        embed.add_field(name=lang_texts["created_by"], value=interaction.user.mention, inline=True)
        embed.add_field(name=lang_texts["type"], value=self._get_ticket_type_name(ticket_type, self.language), inline=True)
        embed.add_field(name=lang_texts["language"], value="Italiano" if self.language == "it" else "English", inline=True)
        
        embed.add_field(
            name=lang_texts["instructions"],
            value=" ",
            inline=False
        )
        
        view = TicketManagementView(self.language)
        
        message = await channel.send(f"{staff_role.mention} {interaction.user.mention}", embed=embed, view=view)
        
        # SALVA IL TICKET NEL DATABASE
        ticket_data = {
            "channel_id": channel.id,
            "message_id": message.id,
            "ticket_type": ticket_type,
            "language": self.language,
            "user_id": interaction.user.id,
            "guild_id": guild.id,
            "role_id": staff_role_id,
            "category_id": category.id,
            "embed_data": {
                "title": ticket_texts["title"],
                "description": ticket_texts["description"],
                "color": discord.Color.blue().value
            }
        }
        ticket_manager.add_ticket(channel.id, ticket_data)
        
        await interaction.response.send_message(lang_texts["success"].format(channel=channel), ephemeral=True)
    
    def _get_ticket_type_name(self, ticket_type: str, language: str) -> str:
        type_names = {
            "it": {
                "bot_creator": "Creazione Bot",
                "server_creator": "Creazione Server",
                "partnership": "Partnership",
                "report": "Segnalazione",
                "ceo_request": "Richiesta CEO"
            },
            "en": {
                "bot_creator": "Bot Creation",
                "server_creator": "Server Creation",
                "partnership": "Partnership",
                "report": "Report",
                "ceo_request": "CEO Request"
            }
        }
        
        lang_names = type_names.get(language, type_names["it"])
        return lang_names.get(ticket_type, "Unknown")

class TicketManagementView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
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
        # RIMUOVI IL TICKET DAL DATABASE
        ticket_manager.remove_ticket(interaction.channel.id)
        
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
        # Registra le view
        self.bot.add_view(TicketView("it"))
        self.bot.add_view(TicketView("en"))
        self.bot.add_view(TicketManagementView("it"))
        self.bot.add_view(TicketManagementView("en"))
        
        # RICARICA TUTTI I TICKET ATTIVI
        await self.restore_active_tickets()
        print("✅ Sistema Ticket pronto!")
    
    async def restore_active_tickets(self):
        """Ricarica tutti i ticket attivi quando il bot si riavvia"""
        print("🔄 Ricaricamento ticket attivi...")
        
        active_tickets = ticket_manager.get_all_tickets()
        if not active_tickets:
            print("✅ Nessun ticket attivo da ricaricare")
            return
        
        restored_count = 0
        
        for channel_id_str, ticket_data in active_tickets.items():
            try:
                channel_id = int(channel_id_str)
                channel = self.bot.get_channel(channel_id)
                
                if channel is None:
                    print(f"❌ Canale {channel_id} non trovato, rimuovendo dal database")
                    ticket_manager.remove_ticket(channel_id)
                    continue
                
                # Verifica se il messaggio esiste ancora
                try:
                    message = await channel.fetch_message(ticket_data["message_id"])
                    # Se il messaggio esiste, non fare nulla
                    restored_count += 1
                    continue
                except discord.NotFound:
                    # Il messaggio è stato cancellato, ricrea l'embed
                    pass
                
                # Ricrea l'embed e i pulsanti
                guild = channel.guild
                role_id = ticket_data.get("role_id")
                role = guild.get_role(int(role_id)) if role_id else None
                user = guild.get_member(ticket_data["user_id"])
                
                embed_data = ticket_data["embed_data"]
                embed = discord.Embed(
                    title=embed_data["title"],
                    description=embed_data["description"],
                    color=embed_data["color"]
                )
                
                # Aggiungi campi base
                lang_texts = {
                    "it": {"created_by": "Creato da", "type": "Tipo", "language": "Lingua"},
                    "en": {"created_by": "Created by", "type": "Type", "language": "Language"}
                }
                texts = lang_texts.get(ticket_data["language"], lang_texts["it"])
                
                embed.add_field(name=texts["created_by"], value=user.mention if user else "Utente sconosciuto", inline=True)
                embed.add_field(name=texts["type"], value=ticket_data["ticket_type"], inline=True)
                embed.add_field(name=texts["language"], value="Italiano" if ticket_data["language"] == "it" else "English", inline=True)
                
                # Aggiungi istruzioni
                instructions = {
                    "it": "📋 **Istruzioni:**\n• Descrivi dettagliatamente la tua richiesta\n• Fornisci tutte le informazioni necessarie",
                    "en": "📋 **Instructions:**\n• Describe your request in detail\n• Provide all necessary information"
                }
                embed.add_field(name=instructions.get(ticket_data["language"], instructions["it"]), value=" ", inline=False)
                
                view = TicketManagementView(ticket_data["language"])
                
                # Invia il nuovo messaggio
                mention_text = f"{role.mention} {user.mention}" if role and user else (user.mention if user else "")
                new_message = await channel.send(mention_text, embed=embed, view=view)
                
                # Aggiorna il database con il nuovo message_id
                ticket_data["message_id"] = new_message.id
                ticket_manager.add_ticket(channel_id, ticket_data)
                
                restored_count += 1
                print(f"✅ Ticket {channel_id} ripristinato")
                
            except Exception as e:
                print(f"❌ Errore ripristino ticket {channel_id_str}: {e}")
                # Se c'è un errore, rimuovi il ticket dal database
                ticket_manager.remove_ticket(channel_id_str)
        
        print(f"✅ Ripristinati {restored_count} ticket attivi")
    
    @discord.app_commands.command(name="setup_tickets", description="Setup del sistema di ticket")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup del sistema di ticket"""
        
        embed = discord.Embed(
            title="🎫 Sistema Ticket - Scegli il tipo",
            description="**Seleziona il tipo di ticket che vuoi aprire:**",
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
        
        view = TicketView("it")
        await interaction.response.send_message(embed=embed, view=view)
    
    @discord.app_commands.command(name="setup_tickets_eng", description="Setup ticket system in English")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets_eng(self, interaction: discord.Interaction):
        """Setup ticket system in English"""
        
        embed = discord.Embed(
            title="🎫 Ticket System - Choose type",
            description="**Select the type of ticket you want to open:**",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="🚨 **Reports**",
            value="• **Report** - Issues, abuses, violations",
            inline=False
        )
        
        embed.add_field(
            name="👑 **Special Requests**",
            value="• **CEO Request** - Confidential matters for CEOs",
            inline=False
        )
        
        embed.add_field(
            name="🛠️ **Services**",
            value="• **Create Bot** - Custom bot development\n• **Create Server** - Discord server creation\n• **Partnership** - Collaborations and partnerships",
            inline=False
        )
        
        embed.set_footer(text="Click a button to open a private ticket")
        
        view = TicketView("en")
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
    print("✅ Cog Ticket caricata!")
