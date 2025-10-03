import os
import discord
from discord.ext import commands

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if not value and default is None:
        print(f"⚠️ Variabile {var_name} non trovata")
    return value or default

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @discord.app_commands.command(name="status", description="Aggiorna lo status di un progetto")
    @discord.app_commands.describe(
        nome="Tipo di progetto",
        modalità="Stato del progetto"
    )
    @discord.app_commands.choices(
        nome=[
            discord.app_commands.Choice(name="server", value="server"),
            discord.app_commands.Choice(name="bot", value="bot"),
            discord.app_commands.Choice(name="server e bot", value="server e bot")
        ],
        modalità=[
            discord.app_commands.Choice(name="appena iniziato", value="appena iniziato"),
            discord.app_commands.Choice(name="a metà", value="a metà"),
            discord.app_commands.Choice(name="finito", value="finito")
        ]
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def status(self, interaction: discord.Interaction, nome: str, modalità: str):
        """Aggiorna lo status di un progetto"""
        # Mappa per le emoji
        status_emojis = {
            "appena iniziato": "🟡",
            "a metà": "🟠", 
            "finito": "🟢"
        }
        
        project_emojis = {
            "server": "🖥️",
            "bot": "🤖",
            "server e bot": "⚡"
        }
        
        emoji_status = status_emojis.get(modalità, "⚪")
        emoji_project = project_emojis.get(nome, "📁")
        
        embed = discord.Embed(
            title=f"{emoji_project} Stato Progetto - {nome.title()}",
            description=f"**Stato:** {emoji_status} {modalità.title()}",
            color=self.get_status_color(modalità)
        )
        embed.set_footer(text=f"Aggiornato da {interaction.user.display_name}")
        
        channel_id = get_env_var('STATUS_CHANNEL_ID')
        if channel_id:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=embed)
                await interaction.response.send_message("✅ Status aggiornato con successo!", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Canale status non trovato!", ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed)
    
    def get_status_color(self, status: str) -> discord.Color:
        colors = {
            "appena iniziato": discord.Color.yellow(),
            "a metà": discord.Color.orange(),
            "finito": discord.Color.green()
        }
        return colors.get(status, discord.Color.default())

async def setup(bot):
    await bot.add_cog(StatusCog(bot))
