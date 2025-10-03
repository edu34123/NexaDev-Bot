import discord
from discord import app_commands
from discord.ext import commands
from utils.config import Config

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='🇮🇹 Italiano', style=discord.ButtonStyle.primary, custom_id='italian')
    async def italian_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_verification(interaction, 'italian')

    @discord.ui.button(label='🇬🇧 English', style=discord.ButtonStyle.primary, custom_id='english')
    async def english_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.handle_verification(interaction, 'english')

    async def handle_verification(self, interaction: discord.Interaction, language: str):
        # Qui puoi aggiungere ruoli specifici per lingua
        if language == 'italian':
            await interaction.response.send_message("✅ Sezione italiana selezionata! Benvenuto in NexaDev!", ephemeral=True)
        else:
            await interaction.response.send_message("✅ English section selected! Welcome to NexaDev!", ephemeral=True)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(VerificationView())

    @app_commands.command(name="setup_verify", description="Setup verification system")
    async def setup_verify(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Non hai i permessi per eseguire questo comando!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🌍 **Seleziona la tua lingua / Select your language**",
            description="Clicca il pulsante corrispondente alla tua lingua per accedere al server.\nClick the button corresponding to your language to access the server.",
            color=0x00ff00
        )

        await interaction.channel.send(embed=embed, view=VerificationView())
        await interaction.response.send_message("Sistema di verifica impostato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Verification(bot))
