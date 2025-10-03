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
    
    async def get_custom_emoji(self, guild: discord.Guild, emoji_names: list) -> str:
        """Cerca emoji personalizzate nel server con fallback"""
        for emoji_name in emoji_names:
            # Cerca l'emoji nel server
            for emoji in guild.emojis:
                if emoji.name.lower() == emoji_name.lower():
                    return str(emoji)
        
        # Fallback a Unicode
        fallback_emojis = {
            "red_loading1": "🟡",
            "loading_orange": "🟠", 
            "green_loading1": "🟢",
            "computer": "🖥️",
            "robot": "🤖",
            "zap": "⚡"
        }
        
        # Cerca il fallback per il primo nome nella lista
        for emoji_name in emoji_names:
            if emoji_name.lower() in fallback_emojis:
                return fallback_emojis[emoji_name.lower()]
        
        return "⚪"
    
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
            discord.app_commands.Choice(name="Appena iniziato", value="Appena iniziato"),
            discord.app_commands.Choice(name="A metà con il progetto", value="A metà con il progetto"),
            discord.app_commands.Choice(name="Finito", value="Finito")
        ]
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def status(self, interaction: discord.Interaction, nome: str, modalità: str):
        """Aggiorna lo status di un progetto"""
        
        guild = interaction.guild
        
        # Configurazione emoji di stato con i tuoi nomi specifici
        status_emoji_config = {
            "appena iniziato": ["Red_Loading1", "red_loading1", "yellow_circle"],
            "a metà": ["loading_orange", "orange_circle"], 
            "finito": ["Green_Loading1", "green_loading1", "green_circle"]
        }
        
        # Configurazione emoji progetti
        project_emoji_config = {
            "server": ["computer", "server", "desktop"],
            "bot": ["robot", "bot", "robot_face"],
            "server e bot": ["zap", "lightning", "both"]
        }
        
        # Ottieni le emoji
        emoji_status = await self.get_custom_emoji(guild, status_emoji_config.get(modalità, ["yellow_circle"]))
        emoji_project = await self.get_custom_emoji(guild, project_emoji_config.get(nome, ["computer"]))
        
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
            await interaction.response.send_message("⚠️ Canale status non configurato. Imposta STATUS_CHANNEL_ID.", ephemeral=True)
    
    def get_status_color(self, status: str) -> discord.Color:
        colors = {
            "appena iniziato": discord.Color.yellow(),
            "a metà": discord.Color.orange(),
            "finito": discord.Color.green()
        }
        return colors.get(status, discord.Color.default())
    
    @discord.app_commands.command(name="emoji_list", description="Mostra le emoji disponibili nel server")
    async def emoji_list(self, interaction: discord.Interaction):
        """Mostra tutte le emoji del server per aiutare la configurazione"""
        guild = interaction.guild
        emojis = guild.emojis
        
        if not emojis:
            await interaction.response.send_message("❌ Nessuna emoji personalizzata trovata nel server.", ephemeral=True)
            return
        
        # Filtra le emoji che ci interessano
        target_emojis = ["Red_Loading1", "loading_orange", "Green_Loading1", "computer", "robot", "zap"]
        found_emojis = []
        other_emojis = []
        
        for emoji in emojis:
            if any(target in emoji.name.lower() for target in [name.lower() for name in target_emojis]):
                found_emojis.append(emoji)
            else:
                other_emojis.append(emoji)
        
        embed = discord.Embed(
            title="🎨 Emoji del Server NexaDev",
            description="Emoji trovate per il sistema di status:",
            color=discord.Color.blue()
        )
        
        # Mostra prima le emoji rilevanti
        if found_emojis:
            relevant_list = []
            for emoji in found_emojis[:10]:
                relevant_list.append(f"{emoji} `:{emoji.name}:`")
            
            embed.add_field(
                name="✅ Emoji Rilevanti",
                value="\n".join(relevant_list),
                inline=False
            )
        
        # Poi altre emoji
        if other_emojis:
            other_list = []
            for emoji in other_emojis[:10]:
                other_list.append(f"{emoji} `:{emoji.name}:`")
            
            embed.add_field(
                name="📋 Altre Emoji",
                value="\n".join(other_list),
                inline=False
            )
        
        if len(emojis) > 20:
            embed.set_footer(text=f"Totali: {len(emojis)} emoji nel server")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.app_commands.command(name="check_status_emojis", description="Verifica se le emoji di status sono configurate correttamente")
    async def check_status_emojis(self, interaction: discord.Interaction):
        """Verifica la configurazione delle emoji di status"""
        guild = interaction.guild
        emojis = guild.emojis
        
        embed = discord.Embed(
            title="🔍 Verifica Emoji Status",
            description="Stato delle emoji richieste per il sistema di status:",
            color=discord.Color.blue()
        )
        
        # Lista delle emoji richieste
        required_emojis = {
            "Appena Iniziato": ["Red_Loading1", "red_loading1"],
            "A Metà": ["loading_orange", "loading_orange"],
            "Finito": ["Green_Loading1", "green_loading1"],
            "Server": ["computer", "server"],
            "Bot": ["robot", "bot"],
            "Server e Bot": ["zap", "lightning"]
        }
        
        status_messages = []
        
        for status_type, emoji_names in required_emojis.items():
            found = False
            found_emoji = None
            
            for emoji_name in emoji_names:
                for emoji in emojis:
                    if emoji.name.lower() == emoji_name.lower():
                        found = True
                        found_emoji = emoji
                        break
                if found:
                    break
            
            if found and found_emoji:
                status_messages.append(f"✅ **{status_type}:** {found_emoji} `:{found_emoji.name}:`")
            else:
                status_messages.append(f"❌ **{status_type}:** Emoji non trovata (cercate: {', '.join(emoji_names)})")
        
        embed.add_field(
            name="Stato Configurazione",
            value="\n".join(status_messages),
            inline=False
        )
        
        embed.set_footer(text="Usa /emoji_list per vedere tutte le emoji disponibili")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(StatusCog(bot))
