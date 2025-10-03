import os
import discord
from discord.ext import commands
from discord import ui

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
        guild = interaction.guild
        
        if language == "italiano":
            role_name = "Italiano"
            embed_title = "Benvenuto in NexaDev!"
            embed_description = "Seleziona il tipo di assistenza di cui hai bisogno:"
        else:
            role_name = "English"
            embed_title = "Welcome to NexaDev!"
            embed_description = "Select the type of assistance you need:"
        
        # Cerca il ruolo
        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            try:
                role = await guild.create_role(name=role_name)
            except discord.Forbidden:
                await interaction.response.send_message(
                    "❌ Non ho i permessi per creare ruoli.",
                    ephemeral=True
                )
                return
        
        # Assegna il ruolo
        try:
            await interaction.user.add_roles(role)
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ Non ho i permessi per assegnare ruoli.",
                ephemeral=True
            )
            return
        
        # Crea embed per i ticket
        if language == "italiano":
            embed = discord.Embed(
                title=embed_title,
                description=embed_description,
                color=discord.Color.blue()
            )
            embed.add_field(name="🤖 Bot Creator", value="Richiedi un bot", inline=True)
            embed.add_field(name="🖥️ Server Creator", value="Richiedi un server", inline=True)
            embed.add_field(name="⚡ Server/Bot Creator", value="Richiedi entrambi", inline=True)
            embed.add_field(name="🤝 Partnership", value="Richiedi partnership", inline=True)
        else:
            embed = discord.Embed(
                title=embed_title,
                description=embed_description,
                color=discord.Color.blue()
            )
            embed.add_field(name="🤖 Bot Creator", value="Request a bot", inline=True)
            embed.add_field(name="🖥️ Server Creator", value="Request a server", inline=True)
            embed.add_field(name="⚡ Server/Bot Creator", value="Request both", inline=True)
            embed.add_field(name="🤝 Partnership", value="Request partnership", inline=True)
        
        from .ticket import TicketView
        view = TicketView()
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class VerifyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(LanguageSelectView())
        print("✅ VerifyCog - View registrate")
    
    @discord.app_commands.command(name="setup_verify", description="Crea il pannello di verifica")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_verify(self, interaction: discord.Interaction):
        """Crea il pannello di verifica"""
        embed = discord.Embed(
            title="NexaDev - Verifica",
            description="**Seleziona la tua lingua / Select your language:**\n\n"
                       "**Italiano** - Per la sezione italiana\n"
                       "**English** - For the English section",
            color=discord.Color.gold()
        )
        
        view = LanguageSelectView()
        await interaction.response.send_message(embed=embed, view=view)
        await interaction.followup.send("✅ Pannello verifica creato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(VerifyCog(bot))
    print("✅ VerifyCog caricato")
