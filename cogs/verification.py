import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
import logging

logger = logging.getLogger(__name__)

class VerificationView(View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="Italiano", style=discord.ButtonStyle.primary, emoji="🇮🇹", custom_id="verify_it")
    async def verify_it(self, interaction: discord.Interaction, button: Button):
        await self.assign_role(interaction, "it")
    
    @discord.ui.button(label="English", style=discord.ButtonStyle.primary, emoji="🇬🇧", custom_id="verify_eng")
    async def verify_eng(self, interaction: discord.Interaction, button: Button):
        await self.assign_role(interaction, "eng")

    async def assign_role(self, interaction: discord.Interaction, language: str):
        try:
            # ID dei ruoli (MODIFICA QUESTI CON I TUOI ID)
            MEMBER_ROLE_ID = 1423395890546081995
            ITA_ROLE_ID = 1423717246261264509
            ENG_ROLE_ID = 1423743289475076318
            
            member_role = interaction.guild.get_role(MEMBER_ROLE_ID)
            
            if language == "it":
                role = interaction.guild.get_role(ITA_ROLE_ID)
                success_message = "✅ Verifica completata! Ti è stato assegnato il ruolo Italiano e il ruolo Membro!"
            else:
                role = interaction.guild.get_role(ENG_ROLE_ID)
                success_message = "✅ Verification completed! You have been assigned the English role and the Member role!"
            
            if role and member_role:
                await interaction.user.add_roles(role, member_role)
                await interaction.response.send_message(success_message, ephemeral=True)
                logger.info(f"Utente {interaction.user} verificato come {language}")
            else:
                await interaction.response.send_message("❌ Ruolo non trovato", ephemeral=True)
                
        except Exception as e:
            logger.error(f"Errore verifica: {e}")
            await interaction.response.send_message("❌ Errore nella verifica", ephemeral=True)

class Verification(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Aggiungi la view persistente
        self.bot.add_view(VerificationView())
        logger.info("✅ Verification view caricata")

async def setup(bot):
    await bot.add_cog(Verification(bot))
