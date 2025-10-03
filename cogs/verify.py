import os
import discord
from discord.ext import commands
from discord import ui

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if not value and default is None:
        print(f"⚠️ Variabile {var_name} non trovata")
    return value or default

class LanguageSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Italiano', style=discord.ButtonStyle.primary, custom_id='italian')
    async def italian(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.setup_language_section(interaction, "italiano")
    
    @discord.ui.button(label='English', style=discord.ButtonStyle.secondary, custom_id='english')
    async def english(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.setup_language_section(interaction, "english")
    
    async def setup_language_section(self, interaction: discord.Interaction, language: str):
        # Assegna il ruolo in base alla lingua
        guild = interaction.guild
        
        if language == "italiano":
            role_name = "Italiano"
            embed_title = "Benvenuto in NexaDev!"
            embed_description = "Seleziona il tipo di assistenza di cui hai bisogno:"
        else:
            role_name = "English"
            embed_title = "Welcome to NexaDev!"
            embed_description = "Select the type of assistance you need:"
        
        # Cerca o crea il ruolo
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(name=role_name)
                print(f"✅ Ruolo {role_name} creato")
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ Non ho i permessi per creare ruoli. Contatta un amministratore.",
                    ephemeral=True
                )
                return
        
        # Assegna il ruolo all'utente
        try:
            await interaction.user.add_roles(role)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Non ho i permessi per assegnare ruoli. Contatta un amministratore.",
                ephemeral=True
            )
            return
        
        # Invia il messaggio dei ticket nella lingua corretta
        if language == "italiano":
            embed = discord.Embed(
                title=embed_title,
                description=embed_description,
                color=discord.Color.blue()
            )
            embed.add_field(name="🤖 Bot Creator", value="Richiedi la creazione di un bot", inline=True)
            embed.add_field(name="🖥️ Server Creator", value="Richiedi la creazione di un server", inline=True)
            embed.add_field(name="⚡ Server/Bot Creator", value="Richiedi entrambi i servizi", inline=True)
            embed.add_field(name="🤝 Partnership", value="Richiedi una partnership", inline=True)
        else:
            embed = discord.Embed(
                title=embed_title,
                description=embed_description,
                color=discord.Color.blue()
            )
            embed.add_field(name="🤖 Bot Creator", value="Request a bot creation", inline=True)
            embed.add_field(name="🖥️ Server Creator", value="Request a server creation", inline=True)
            embed.add_field(name="⚡ Server/Bot Creator", value="Request both services", inline=True)
            embed.add_field(name="🤝 Partnership", value="Request a partnership", inline=True)
        
        from .ticket import TicketView
        view = TicketView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class VerifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(LanguageSelectView())
        print("✅ VerifyCog pronto e view registrate")
    
    @discord.app_commands.command(name="setup_verify", description="Setup del sistema di verifica nel canale")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_verify(self, interaction: discord.Interaction):
        """Setup del sistema di verifica"""
        
        embed = discord.Embed(
            title="NexaDev - Verifica",
            description="**Seleziona la tua lingua / Select your language:**\n\n"
                       "**Italiano** - Seleziona per la sezione italiana\n"
                       "**English** - Select for the English section\n\n"
                       "*Clicca sul pulsante corrispondente alla tua lingua*",
            color=discord.Color.gold()
        )
        
        embed.set_footer(text="NexaDev - Scegli la tua lingua / Choose your language")
        
        view = LanguageSelectView()
        
        await interaction.response.send_message(embed=embed, view=view)
        await interaction.followup.send("✅ Sistema di verifica configurato con successo!", ephemeral=True)
    
    @discord.app_commands.command(name="test_verify", description="Test del sistema di verifica (solo admin)")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def test_verify(self, interaction: discord.Interaction):
        """Test del sistema di verifica"""
        
        embed = discord.Embed(
            title="🧪 Test Sistema Verifica",
            description="Questo è un test del sistema di verifica.",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="✅ Status", value="Sistema funzionante correttamente", inline=False)
        embed.add_field(name="🔧 Comandi", value="`/setup_verify` - Configura il sistema\n`/test_verify` - Test del sistema", inline=False)
        
        view = LanguageSelectView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

async def setup(bot):
    await bot.add_cog(VerifyCog(bot))
