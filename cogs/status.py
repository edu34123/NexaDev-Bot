import discord
from discord.ext import commands
import os

class StatusCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def status(self, ctx, nome: str, modalità: str):
        """Aggiorna lo status di un progetto
        nome: server, bot, "server e bot"
        modalità: "appena iniziato", "a metà", "finito"
        """
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
        
        emoji_status = status_emojis.get(modalità.lower(), "⚪")
        emoji_project = project_emojis.get(nome.lower(), "📁")
        
        embed = discord.Embed(
            title=f"{emoji_project} Stato Progetto - {nome.title()}",
            description=f"**Stato:** {emoji_status} {modalità.title()}",
            color=self.get_status_color(modalità.lower())
        )
        embed.set_footer(text=f"Aggiornato da {ctx.author.display_name}")
        
        channel = self.bot.get_channel(int(os.getenv('STATUS_CHANNEL_ID')))
        if channel:
            await channel.send(embed=embed)
            await ctx.send("Status aggiornato con successo!", ephemeral=True)
        else:
            await ctx.send("Canale status non trovato!", ephemeral=True)
    
    def get_status_color(self, status: str) -> discord.Color:
        colors = {
            "appena iniziato": discord.Color.yellow(),
            "a metà": discord.Color.orange(),
            "finito": discord.Color.green()
        }
        return colors.get(status, discord.Color.default())
    
    @status.error
    async def status_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Utilizzo: `/status <nome> <modalità>`\n\n**Nomi validi:** server, bot, \"server e bot\"\n**Modalità:** appena iniziato, a metà, finito")

async def setup(bot):
    await bot.add_cog(StatusCog(bot))
