import os
import discord
from discord.ext import commands
from discord import ui
import asyncio
from datetime import datetime, timedelta
import json

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if not value and default is None:
        print(f"⚠️ Variabile {var_name} non trovata")
    return value or default

class SecurityTicketView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
        # Configurazione pulsanti in base alla lingua
        button_configs = {
            "it": {
                "report_user": {"label": "🚨 Segnala Utente", "style": discord.ButtonStyle.danger},
                "report_scam": {"label": "💀 Segnala Scam", "style": discord.ButtonStyle.danger},
                "report_content": {"label": "🔞 Contenuto Inappropriato", "style": discord.ButtonStyle.danger},
                "report_harassment": {"label": "⚖️ Harassment", "style": discord.ButtonStyle.danger},
                "security_help": {"label": "🛡️ Aiuto Sicurezza", "style": discord.ButtonStyle.primary},
                "appeal": {"label": "📝 Ricorso/Appello", "style": discord.ButtonStyle.secondary},
                "other": {"label": "❓ Altro", "style": discord.ButtonStyle.secondary}
            },
            "en": {
                "report_user": {"label": "🚨 Report User", "style": discord.ButtonStyle.danger},
                "report_scam": {"label": "💀 Report Scam", "style": discord.ButtonStyle.danger},
                "report_content": {"label": "🔞 Inappropriate Content", "style": discord.ButtonStyle.danger},
                "report_harassment": {"label": "⚖️ Harassment", "style": discord.ButtonStyle.danger},
                "security_help": {"label": "🛡️ Security Help", "style": discord.ButtonStyle.primary},
                "appeal": {"label": "📝 Appeal", "style": discord.ButtonStyle.secondary},
                "other": {"label": "❓ Other", "style": discord.ButtonStyle.secondary}
            }
        }
        
        config = button_configs.get(language, button_configs["it"])
        
        # Crea i pulsanti
        self.add_item(SecurityTicketButton("report_user", config["report_user"]["label"], config["report_user"]["style"], f"report_user_{language}", language))
        self.add_item(SecurityTicketButton("report_scam", config["report_scam"]["label"], config["report_scam"]["style"], f"report_scam_{language}", language))
        self.add_item(SecurityTicketButton("report_content", config["report_content"]["label"], config["report_content"]["style"], f"report_content_{language}", language))
        self.add_item(SecurityTicketButton("report_harassment", config["report_harassment"]["label"], config["report_harassment"]["style"], f"report_harassment_{language}", language))
        self.add_item(SecurityTicketButton("security_help", config["security_help"]["label"], config["security_help"]["style"], f"security_help_{language}", language))
        self.add_item(SecurityTicketButton("appeal", config["appeal"]["label"], config["appeal"]["style"], f"appeal_{language}", language))
        self.add_item(SecurityTicketButton("other", config["other"]["label"], config["other"]["style"], f"other_{language}", language))

class SecurityTicketButton(ui.Button):
    def __init__(self, ticket_type: str, label: str, style: discord.ButtonStyle, custom_id: str, language: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.button_type = ticket_type
        self.language = language
    
    async def callback(self, interaction: discord.Interaction):
        await self.create_security_ticket(interaction, self.button_type, self.language)
    
    async def create_security_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        guild = interaction.guild
        security_role_id = get_env_var('SECURITY_ROLE_ID')
        
        if not security_role_id:
            error_msg = {
                "it": "❌ Errore di configurazione: ruolo security non configurato.",
                "en": "❌ Configuration error: security role not configured."
            }
            await interaction.response.send_message(error_msg.get(language, error_msg["it"]), ephemeral=True)
            return
        
        security_role = guild.get_role(int(security_role_id))
        if not security_role:
            error_msg = {
                "it": "❌ Ruolo security non trovato nel server.",
                "en": "❌ Security role not found in the server."
            }
            await interaction.response.send_message(error_msg.get(language, error_msg["it"]), ephemeral=True)
            return
        
        # Crea il canale ticket security
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            security_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }
        
        # Nomi dei tipi di ticket
        type_names = {
            "it": {
                "report_user": "segnalazione-utente",
                "report_scam": "segnalazione-scam", 
                "report_content": "contenuto-inappropriato",
                "report_harassment": "harassment",
                "security_help": "aiuto-sicurezza",
                "appeal": "ricorso-appello",
                "other": "altro"
            },
            "en": {
                "report_user": "user-report",
                "report_scam": "scam-report",
                "report_content": "inappropriate-content", 
                "report_harassment": "harassment",
                "security_help": "security-help",
                "appeal": "appeal",
                "other": "other"
            }
        }
        
        lang_type_names = type_names.get(language, type_names["it"])
        channel_name = f"{lang_type_names[ticket_type]}-{interaction.user.name}"[:100]
        
        channel = await guild.create_text_channel(
            name=channel_name,
            overwrites=overwrites,
            topic=f"Security Ticket - {ticket_type} - {language.upper()} - {interaction.user.display_name}"
        )
        
        # Testi multilingua
        texts = {
            "it": {
                "report_user": {
                    "title": "🚨 Segnalazione Utente",
                    "description": "Grazie per aver aperto una segnalazione utente. Per favore fornisci:\n\n• **ID o menzione dell'utente**\n• **Prove (screenshot, etc.)**\n• **Descrizione dettagliata**\n• **Quando è successo**"
                },
                "report_scam": {
                    "title": "💀 Segnalazione Scam",
                    "description": "Grazie per aver segnalato uno scam. Per favore fornisci:\n\n• **Dettagli dello scam**\n• **Prove (screenshot, messaggi)**\n• **Utente/server coinvolto**\n• **Cosa è stato rubato**"
                },
                "report_content": {
                    "title": "🔞 Contenuto Inappropriato",
                    "description": "Grazie per aver segnalato contenuto inappropriato. Per favore fornisci:\n\n• **Link o descrizione contenuto**\n• **Prove (screenshot)**\n• **Dove è stato trovato**\n• **Utente coinvolto**"
                },
                "report_harassment": {
                    "title": "⚖️ Segnalazione Harassment",
                    "description": "Grazie per aver segnalato harassment. Per favore fornisci:\n\n• **Utente che molesta**\n• **Prove (messaggi, screenshot)**\n• **Da quanto tempo continua**\n• **Impatto su di te**"
                },
                "security_help": {
                    "title": "🛡️ Aiuto Sicurezza",
                    "description": "Grazie per aver richiesto aiuto sicurezza. Descrivi il tuo problema:\n\n• **Quale problema di sicurezza?**\n• **Account compromesso?**\n• **Hai bisogno di consigli?**\n• **Altri dettagli**"
                },
                "appeal": {
                    "title": "📝 Ricorso/Appello",
                    "description": "Grazie per aver aperto un ricorso. Per favore fornisci:\n\n• **Motivo del ricorso**\n• **ID sanzione (se applicabile)**\n• **La tua versione dei fatti**\n• **Prove a supporto**"
                },
                "other": {
                    "title": "❓ Altro - Sicurezza",
                    "description": "Grazie per aver contattato la sicurezza. Descrivi il tuo problema:"
                },
                "created_by": "Creato da",
                "type": "Tipo",
                "language": "Lingua",
                "instructions": "📋 **Istruzioni:**\n• Fornisci tutte le informazioni richieste\n• Carica le prove come screenshot\n• Sii dettagliato e preciso\n• Lo staff ti risponderà presto",
                "success": "✅ Ticket sicurezza creato! {channel.mention}"
            },
            "en": {
                "report_user": {
                    "title": "🚨 User Report",
                    "description": "Thank you for opening a user report. Please provide:\n\n• **User ID or mention**\n• **Evidence (screenshots, etc.)**\n• **Detailed description**\n• **When it happened**"
                },
                "report_scam": {
                    "title": "💀 Scam Report", 
                    "description": "Thank you for reporting a scam. Please provide:\n\n• **Scam details**\n• **Evidence (screenshots, messages)**\n• **User/server involved**\n• **What was stolen**"
                },
                "report_content": {
                    "title": "🔞 Inappropriate Content",
                    "description": "Thank you for reporting inappropriate content. Please provide:\n\n• **Content link or description**\n• **Evidence (screenshots)**\n• **Where it was found**\n• **User involved**"
                },
                "report_harassment": {
                    "title": "⚖️ Harassment Report",
                    "description": "Thank you for reporting harassment. Please provide:\n\n• **Harassing user**\n• **Evidence (messages, screenshots)**\n• **How long it's been going on**\n• **Impact on you**"
                },
                "security_help": {
                    "title": "🛡️ Security Help",
                    "description": "Thank you for requesting security help. Describe your issue:\n\n• **What security problem?**\n• **Account compromised?**\n• **Need advice?**\n• **Other details**"
                },
                "appeal": {
                    "title": "📝 Appeal",
                    "description": "Thank you for opening an appeal. Please provide:\n\n• **Appeal reason**\n• **Sanction ID (if applicable)**\n• **Your side of the story**\n• **Supporting evidence**"
                },
                "other": {
                    "title": "❓ Other - Security", 
                    "description": "Thank you for contacting security. Describe your issue:"
                },
                "created_by": "Created by",
                "type": "Type", 
                "language": "Language",
                "instructions": "📋 **Instructions:**\n• Provide all requested information\n• Upload evidence as screenshots\n• Be detailed and precise\n• Staff will respond soon",
                "success": "✅ Security ticket created! {channel.mention}"
            }
        }
        
        lang_texts = texts.get(language, texts["it"])
        ticket_texts = lang_texts.get(ticket_type, lang_texts["other"])
        
        # Embed del ticket security
        embed = discord.Embed(
            title=ticket_texts["title"],
            description=ticket_texts["description"],
            color=discord.Color.red() if "report" in ticket_type else discord.Color.blue()
        )
        
        embed.add_field(name=lang_texts["created_by"], value=interaction.user.mention, inline=True)
        embed.add_field(name=lang_texts["type"], value=self._get_ticket_type_name(ticket_type, language), inline=True)
        embed.add_field(name=lang_texts["language"], value="Italiano" if language == "it" else "English", inline=True)
        
        embed.add_field(
            name="🔒 **Confidential**",
            value="This ticket is confidential and only visible to you and security staff.",
            inline=False
        )
        
        embed.add_field(
            name=lang_texts["instructions"],
            value=" ",
            inline=False
        )
        
        view = SecurityTicketManagementView(language)
        
        await channel.send(f"{security_role.mention} {interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(lang_texts["success"].format(channel=channel), ephemeral=True)
    
    def _get_ticket_type_name(self, ticket_type: str, language: str) -> str:
        """Restituisce il nome del tipo di ticket nella lingua corretta"""
        type_names = {
            "it": {
                "report_user": "Segnalazione Utente",
                "report_scam": "Segnalazione Scam",
                "report_content": "Contenuto Inappropriato",
                "report_harassment": "Harassment", 
                "security_help": "Aiuto Sicurezza",
                "appeal": "Ricorso/Appello",
                "other": "Altro"
            },
            "en": {
                "report_user": "User Report",
                "report_scam": "Scam Report",
                "report_content": "Inappropriate Content",
                "report_harassment": "Harassment",
                "security_help": "Security Help", 
                "appeal": "Appeal",
                "other": "Other"
            }
        }
        
        lang_names = type_names.get(language, type_names["it"])
        return lang_names.get(ticket_type, "Unknown")

class SecurityTicketManagementView(ui.View):
    def __init__(self, language: str = "it"):
        super().__init__(timeout=None)
        self.language = language
        
        # Testi multilingua per i pulsanti
        button_texts = {
            "it": {
                "claim": {"label": "🛡️ Prendi in Carico", "style": discord.ButtonStyle.success},
                "close": {"label": "🔒 Chiudi Ticket", "style": discord.ButtonStyle.danger},
                "warning": {"label": "⚠️ Emetti Avviso", "style": discord.ButtonStyle.primary},
                "evidence": {"label": "📸 Richiedi Prove", "style": discord.ButtonStyle.secondary}
            },
            "en": {
                "claim": {"label": "🛡️ Claim Ticket", "style": discord.ButtonStyle.success},
                "close": {"label": "🔒 Close Ticket", "style": discord.ButtonStyle.danger},
                "warning": {"label": "⚠️ Issue Warning", "style": discord.ButtonStyle.primary},
                "evidence": {"label": "📸 Request Evidence", "style": discord.ButtonStyle.secondary}
            }
        }
        
        texts = button_texts.get(language, button_texts["it"])
        
        # Aggiungi pulsanti di gestione security
        self.add_item(SecurityManagementButton("claim", texts["claim"]["label"], texts["claim"]["style"], f"security_claim_{language}", language))
        self.add_item(SecurityManagementButton("evidence", texts["evidence"]["label"], texts["evidence"]["style"], f"security_evidence_{language}", language))
        self.add_item(SecurityManagementButton("warning", texts["warning"]["label"], texts["warning"]["style"], f"security_warning_{language}", language))
        self.add_item(SecurityManagementButton("close", texts["close"]["label"], texts["close"]["style"], f"security_close_{language}", language))

class SecurityManagementButton(ui.Button):
    def __init__(self, button_type: str, label: str, style: discord.ButtonStyle, custom_id: str, language: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.button_type = button_type
        self.language = language
    
    async def callback(self, interaction: discord.Interaction):
        if self.button_type == "claim":
            await self.claim_ticket(interaction)
        elif self.button_type == "close":
            await self.close_ticket(interaction)
        elif self.button_type == "warning":
            await self.issue_warning(interaction)
        elif self.button_type == "evidence":
            await self.request_evidence(interaction)
    
    async def claim_ticket(self, interaction: discord.Interaction):
        texts = {
            "it": {
                "title": "🛡️ Ticket Preso in Carico",
                "description": f"Il ticket è stato preso in carico da {interaction.user.mention}",
                "log": f"**🛡️ Preso in carico da:** {interaction.user.mention}"
            },
            "en": {
                "title": "🛡️ Ticket Claimed", 
                "description": f"The ticket has been claimed by {interaction.user.mention}",
                "log": f"**🛡️ Claimed by:** {interaction.user.mention}"
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.green()
        )
        
        # Log nell'channel
        log_embed = discord.Embed(
            description=lang_texts["log"],
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(embed=log_embed)
    
    async def close_ticket(self, interaction: discord.Interaction):
        texts = {
            "it": {
                "title": "🔒 Ticket Chiuso",
                "description": "Il ticket verrà chiuso in 5 secondi...",
                "log": f"**🔒 Chiuso da:** {interaction.user.mention}"
            },
            "en": {
                "title": "🔒 Ticket Closed",
                "description": "The ticket will be closed in 5 seconds...", 
                "log": f"🔒 Closed by:** {interaction.user.mention}"
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.red()
        )
        
        # Log finale
        log_embed = discord.Embed(
            description=lang_texts["log"],
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        await interaction.response.send_message(embed=embed)
        await interaction.channel.send(embed=log_embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()
    
    async def issue_warning(self, interaction: discord.Interaction):
        """Emetti un avviso di condotta come nell'immagine"""
        
        texts = {
            "it": {
                "title": "⚠️ Emetti Avviso di Condotta",
                "placeholder_user": "ID o menzione utente",
                "placeholder_reason": "Motivo sintetico (es. Tossicità, Scam, etc.)",
                "placeholder_details": "Dettagli dell'accaduto", 
                "label_user": "Utente",
                "label_reason": "Motivo",
                "label_details": "Dettagli",
                "button": "📄 Emetti Avviso"
            },
            "en": {
                "title": "⚠️ Issue Conduct Warning",
                "placeholder_user": "User ID or mention", 
                "placeholder_reason": "Brief reason (e.g., Toxicity, Scam, etc.)",
                "placeholder_details": "Details of what happened",
                "label_user": "User",
                "label_reason": "Reason", 
                "label_details": "Details",
                "button": "📄 Issue Warning"
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        modal = WarningModal(lang_texts)
        await interaction.response.send_modal(modal)
    
    async def request_evidence(self, interaction: discord.Interaction):
        texts = {
            "it": {
                "title": "📸 Richiesta Prove",
                "description": f"{interaction.user.mention} ha richiesto prove aggiuntive.\n\n**Per favore carica:**\n• Screenshot\n• Messaggi\n• Altro materiale rilevante",
                "ping": "L'utente è stato pingato per fornire prove aggiuntive."
            },
            "en": {
                "title": "📸 Evidence Request",
                "description": f"{interaction.user.mention} has requested additional evidence.\n\n**Please upload:**\n• Screenshots\n• Messages\n• Other relevant material",
                "ping": "The user has been pinged to provide additional evidence."
            }
        }
        
        lang_texts = texts.get(self.language, texts["it"])
        
        embed = discord.Embed(
            title=lang_texts["title"],
            description=lang_texts["description"],
            color=discord.Color.orange()
        )
        
        # Trova l'utente che ha aperto il ticket (primo utente menzionato dopo il ruolo)
        for member in interaction.channel.members:
            if not member.bot and member != interaction.user:
                await interaction.channel.send(f"{member.mention}", embed=embed)
                break
        
        await interaction.response.send_message(lang_texts["ping"], ephemeral=True)

class WarningModal(ui.Modal, title='⚠️ Avviso di Condotta'):
    def __init__(self, texts):
        super().__init__(timeout=None)
        self.texts = texts
        
        self.user_input = ui.TextInput(
            label=texts["label_user"],
            placeholder=texts["placeholder_user"],
            style=discord.TextStyle.short,
            required=True
        )
        
        self.reason_input = ui.TextInput(
            label=texts["label_reason"],
            placeholder=texts["placeholder_reason"], 
            style=discord.TextStyle.short,
            required=True
        )
        
        self.details_input = ui.TextInput(
            label=texts["label_details"],
            placeholder=texts["placeholder_details"],
            style=discord.TextStyle.paragraph,
            required=True
        )
        
        self.add_item(self.user_input)
        self.add_item(self.reason_input)
        self.add_item(self.details_input)
    
    async def on_submit(self, interaction: discord.Interaction):
        # Genera ID report
        report_id = f"R-{interaction.user.id}{datetime.now().strftime('%H%M%S')}"[-8:]
        
        # Data di scadenza (6 mesi)
        expiry_date = datetime.now() + timedelta(days=180)
        
        embed = discord.Embed(
            title="NEXUS – Avviso di Condotta",
            description="## Avviso ufficiale alla community\n- [ ] Avviso emesso per prevenzione e tutela dell'ambiente comunitario.\n- [x] Non è una sanzione automatica né un invito a comportamenti ostili.\n- [ ] I dati sono presentati in forma limitata nel rispetto della privacy.",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="---",
            value="### Dettagli dell'avviso",
            inline=False
        )
        
        embed.add_field(
            name="**ID Segnalazione:**",
            value=report_id,
            inline=True
        )
        
        embed.add_field(
            name="**Utente:**",
            value=self.user_input.value,
            inline=True
        )
        
        embed.add_field(
            name="**Motivo sintetico:**", 
            value=self.reason_input.value,
            inline=True
        )
        
        embed.add_field(
            name="**Dettaglio:**",
            value=self.details_input.value,
            inline=False
        )
        
        embed.add_field(
            name="**Data di emissione:**",
            value=datetime.now().strftime("%B %d, %Y %I:%M %p"),
            inline=True
        )
        
        embed.add_field(
            name="**Scadenza dell'avviso:**",
            value=expiry_date.strftime("%d %B %Y – ore %H:%M"),
            inline=True
        )
        
        embed.add_field(
            name="**Contesto e Finalità**",
            value="• Raccolta di prove concrete\n• Analisi da parte di più membri dello staff\n• Emissione dell'avviso solo se fondato",
            inline=False
        )
        
        embed.add_field(
            name="**Nota legale**",
            value="Base giuridica: art. 6(1)(1) GDPR – Legittimo interesse. Nessuna azione automatica viene intrapresa dal bot.",
            inline=False
        )
        
        embed.set_footer(text="NEXUS – Unità di Sicurezza Digitale - Registro aggiornato alla data di emissione")
        
        await interaction.response.send_message(embed=embed)
        
        # Salva nel database (semplificato)
        warning_data = {
            "report_id": report_id,
            "user": self.user_input.value,
            "reason": self.reason_input.value,
            "details": self.details_input.value,
            "issued_by": interaction.user.id,
            "issued_at": datetime.now().isoformat(),
            "expires_at": expiry_date.isoformat(),
            "channel_id": interaction.channel_id
        }
        
        # Qui puoi salvare in un database reale
        print(f"⚠️ Avviso emesso: {warning_data}")

class SecurityCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        # Registra tutte le view per entrambe le lingue
        self.bot.add_view(SecurityTicketView("it"))
        self.bot.add_view(SecurityTicketView("en"))
        self.bot.add_view(SecurityTicketManagementView("it"))
        self.bot.add_view(SecurityTicketManagementView("en"))
    
    @discord.app_commands.command(name="setup_security_ita", description="Setup del sistema security/ticket in italiano")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_security_ita(self, interaction: discord.Interaction):
        """Setup del sistema security in italiano"""
        
        embed = discord.Embed(
            title="🛡️ NEXUS – Ticket Center Sicurezza",
            description="### Sistema di Segnalazione e Sicurezza\n**Assistenza riservata, risposta tracciata.**",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🚨 **Segnalazioni Rapide**",
            value="• **Segnala Utente** - Comportamenti inappropriati\n• **Segnala Scam** - Truffe e inganni\n• **Contenuto Inappropriato** - Materiale non consentito\n• **Harassment** - Molestie e bullismo",
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Supporto e Assistenza**", 
            value="• **Aiuto Sicurezza** - Problemi account e sicurezza\n• **Ricorso/Appello** - Contestazioni sanzioni\n• **Altro** - Altri problemi di sicurezza",
            inline=False
        )
        
        embed.add_field(
            name="🔒 **Confidenzialità**",
            value="Tutti i ticket sono privati e visibili solo a te e allo staff di sicurezza.",
            inline=False
        )
        
        embed.set_footer(text="Scegli una categoria per aprire un ticket riservato")
        
        view = SecurityTicketView("it")
        await interaction.response.send_message(embed=embed, view=view)
    
    @discord.app_commands.command(name="setup_security_eng", description="Setup security/ticket system in English")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_security_eng(self, interaction: discord.Interaction):
        """Setup security system in English"""
        
        embed = discord.Embed(
            title="🛡️ NEXUS – Security Ticket Center", 
            description="### Reporting and Security System\n**Confidential assistance, tracked response.**",
            color=discord.Color.red()
        )
        
        embed.add_field(
            name="🚨 **Quick Reports**",
            value="• **Report User** - Inappropriate behavior\n• **Report Scam** - Frauds and scams\n• **Inappropriate Content** - Prohibited material\n• **Harassment** - Harassment and bullying", 
            inline=False
        )
        
        embed.add_field(
            name="🛡️ **Support & Assistance**",
            value="• **Security Help** - Account and security issues\n• **Appeal** - Sanction appeals\n• **Other** - Other security matters",
            inline=False
        )
        
        embed.add_field(
            name="🔒 **Confidentiality**",
            value="All tickets are private and visible only to you and security staff.",
            inline=False
        )
        
        embed.set_footer(text="Choose a category to open a confidential ticket")
        
        view = SecurityTicketView("en")
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(SecurityCog(bot))
