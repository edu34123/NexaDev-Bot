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
        await self.assign_role(interaction, 1423717246261264509, "Italiano")  # ita_id
    
    @discord.ui.button(label="English", style=discord.ButtonStyle.primary, emoji="🇬🇧", custom_id="verify_eng")
    async def verify_eng(self, interaction: discord.Interaction, button: Button):
        await self.assign_role(interaction, 1423743289475076318, "English")  # eng_id

    async def assign_role(self, interaction: discord.Interaction, role_id: int, language: str):
        try:
            role = interaction.guild.get_role(role_id)
            member_role = interaction.guild.get_role(1423395890546081995)  # member_id
            
            if role and member_role:
                await interaction.user.add_roles(role, member_role)
                
                embed = discord.Embed(
                    title="✅ Verifica Completata",
                    description=f"Ti è stato assegnato il ruolo {language} e il ruolo Membro!",
                    color=0x00ff00
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
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
        self.bot.add_view(VerificationView())
        logger.info("✅ Verification view caricata")

async def setup(bot):
    await bot.add_cog(Verification(bot))
