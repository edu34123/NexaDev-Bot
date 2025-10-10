import os
import discord
from discord.ext import commands
from discord import ui
import asyncio
from datetime import datetime, timedelta

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
        self.ticket_type = ticket_type
        self.language = language
    
    async def callback(self, interaction: discord.Interaction):
        await self.create_security_ticket(interaction, self.ticket_type, self.language)
    
    async def create_security_ticket(self, interaction: discord.Interaction, ticket_type: str, language: str):
        guild = interaction.guild
        # CORREZIONE: usa REPORT_ROLE_ID invece di SECURITY_ROLE_ID
        security_role_id = get_env_var('REPORT_ROLE_ID')
        
        if not security_role_id:
            error_msg = {
                "it": "❌ Errore di configurazione: ruolo report non configurato.",
                "en": "❌ Configuration error: report role not configured."
            }
            await interaction.response.send_message(error_msg.get(language, error_msg["it"]), ephemeral=True)
            return
        
        security_role = guild.get_role(int(security_role_id))
        if not security_role:
            error_msg = {
                "it": "❌ Ruolo report non trovato nel server.",
                "en": "❌ Report role not found in the server."
            }
            await interaction.response.send_message(error_msg.get(language, error_msg["it"]), ephemeral=True)
            return
        
        # Resto del codice rimane uguale...
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            security_role: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True, manage_messages=True)
        }
        
        # ... resto del codice ...

# Resto delle classi rimangono uguali...

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
        print("✅ Sistema Security pronto!")
    
    @discord.app_commands.command(name="setup_security_ita", description="Setup del sistema security/ticket in italiano")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_security_ita(self, interaction: discord.Interaction):
        """Setup del sistema security in italiano"""
        # ... codice del comando ...

    @discord.app_commands.command(name="setup_security_eng", description="Setup security/ticket system in English")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_security_eng(self, interaction: discord.Interaction):
        """Setup security system in English"""
        # ... codice del comando ...

async def setup(bot):
    await bot.add_cog(SecurityCog(bot))
    print("✅ Cog Security caricata!")
