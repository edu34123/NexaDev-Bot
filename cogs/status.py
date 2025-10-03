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
        
        for emoji_name in emoji_names:
            if emoji_name.lower() in fallback_emojis:
                return fallback_emojis[emoji_name.lower()]
        
        return "⚪"
    
    @discord.app_commands.command(name="status", description="Aggiorna lo status di un progetto")
    @discord.app_commands.describe(
        nome="Tipo di progetto",
        modalità="Stato del progetto",
        persona="Persona per cui è il progetto (menzione)",
        descrizione="Descrizione del progetto (opzionale)"
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
    async def status(self, interaction: discord.Interaction, nome: str, modalità: str, persona: discord.Member, descrizione: str = None):
        """Aggiorna lo status di un progetto"""
        
        guild = interaction.guild
        
        # Configurazione emoji di stato
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
        
        # Crea l'embed per il canale status
        embed = discord.Embed(
            title=f"{emoji_project} {nome.title()} - {modalità.title()}",
            color=self.get_status_color(modalità)
        )
        
        embed.add_field(name="👤 Cliente", value=persona.mention, inline=True)
        embed.add_field(name="📊 Stato", value=f"{emoji_status} {modalità.title()}", inline=True)
        embed.add_field(name="🛠️ Tipo", value=nome.title(), inline=True)
        
        if descrizione:
            embed.add_field(name="📝 Descrizione", value=descrizione, inline=False)
        
        embed.set_footer(text=f"Aggiornato da {interaction.user.display_name}")
        
        # Invia nel canale status
        channel_id = get_env_var('STATUS_CHANNEL_ID')
        if channel_id:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=embed)
                await interaction.response.send_message("✅ Status aggiornato con successo!", ephemeral=True)
                
                # Notifica la persona via DM se lo status è "finito"
                if modalità == "finito":
                    try:
                        dm_embed = discord.Embed(
                            title="🎉 Il tuo progetto è pronto!",
                            description=f"Il tuo {nome} è stato completato!",
                            color=discord.Color.green()
                        )
                        dm_embed.add_field(name="📊 Stato", value="Completato ✅", inline=True)
                        dm_embed.add_field(name="🛠️ Tipo", value=nome.title(), inline=True)
                        
                        if descrizione:
                            dm_embed.add_field(name="📝 Descrizione", value=descrizione, inline=False)
                        
                        dm_embed.set_footer(text="Grazie per aver scelto NexaDev!")
                        
                        await persona.send(embed=dm_embed)
                        await interaction.followup.send(f"✅ Notifica inviata in DM a {persona.mention}", ephemeral=True)
                    except discord.Forbidden:
                        await interaction.followup.send(f"❌ Impossibile inviare DM a {persona.mention}", ephemeral=True)
            else:
                await interaction.response.send_message("❌ Canale status non trovato!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Canale status non configurato.", ephemeral=True)
    
    @discord.app_commands.command(name="statusfinito", description="Marca un progetto come finito e invia invito al cliente")
    @discord.app_commands.describe(
        persona="Persona per cui è il progetto (menzione)",
        descrizione="Descrizione del progetto",
        invito="Invito al server Discord"
    )
    @discord.app_commands.choices(
        nome=[
            discord.app_commands.Choice(name="server", value="server"),
            discord.app_commands.Choice(name="bot", value="bot"),
            discord.app_commands.Choice(name="server e bot", value="server e bot")
        ]
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def statusfinito(self, interaction: discord.Interaction, persona: discord.Member, descrizione: str, invito: str, nome: str = "server"):
        """Marca un progetto come finito e invia tutto al cliente"""
        
        guild = interaction.guild
        
        # Configurazione emoji
        status_emoji_config = {
            "finito": ["Green_Loading1", "green_loading1", "green_circle"]
        }
        
        project_emoji_config = {
            "server": ["computer", "server", "desktop"],
            "bot": ["robot", "bot", "robot_face"],
            "server e bot": ["zap", "lightning", "both"]
        }
        
        # Ottieni le emoji
        emoji_status = await self.get_custom_emoji(guild, status_emoji_config.get("finito", ["green_circle"]))
        emoji_project = await self.get_custom_emoji(guild, project_emoji_config.get(nome, ["computer"]))
        
        # Embed per il canale status
        status_embed = discord.Embed(
            title=f"{emoji_project} {nome.title()} - Completato 🎉",
            color=discord.Color.green()
        )
        
        status_embed.add_field(name="👤 Cliente", value=persona.mention, inline=True)
        status_embed.add_field(name="📊 Stato", value=f"{emoji_status} Completato", inline=True)
        status_embed.add_field(name="🛠️ Tipo", value=nome.title(), inline=True)
        status_embed.add_field(name="📝 Descrizione", value=descrizione, inline=False)
        
        status_embed.set_footer(text=f"Completato da {interaction.user.display_name}")
        
        # Embed per il DM del cliente
        dm_embed = discord.Embed(
            title="🎉 Il tuo progetto è pronto!",
            description=f"Il tuo **{nome.title()}** è stato completato con successo!",
            color=discord.Color.green()
        )
        
        dm_embed.add_field(name="📝 Descrizione", value=descrizione, inline=False)
        dm_embed.add_field(name="🔗 Invito Server", value=f"[Clicca qui per entrare]({invito})", inline=True)
        dm_embed.add_field(name="🛠️ Sviluppatore", value=interaction.user.mention, inline=True)
        
        dm_embed.set_footer(text="Grazie per aver scelto NexaDev! 💫")
        
        # Invia nel canale status
        channel_id = get_env_var('STATUS_CHANNEL_ID')
        if channel_id:
            channel = self.bot.get_channel(int(channel_id))
            if channel:
                await channel.send(embed=status_embed)
                
                # Invia DM al cliente
                try:
                    await persona.send(embed=dm_embed)
                    
                    # Invia anche l'invito come messaggio separato (più visibile)
                    invite_embed = discord.Embed(
                        title="🔗 Invito al Server",
                        description=f"**Clicca sul link qui sotto per entrare nel server:**\n{invito}",
                        color=discord.Color.blue()
                    )
                    await persona.send(embed=invite_embed)
                    
                    await interaction.response.send_message(
                        f"✅ Progetto marcato come completato e notifica inviata a {persona.mention}!", 
                        ephemeral=True
                    )
                    
                except discord.Forbidden:
                    await interaction.response.send_message(
                        f"❌ Impossibile inviare DM a {persona.mention}. Il progetto è stato comunque marcato come completato.", 
                        ephemeral=True
                    )
            else:
                await interaction.response.send_message("❌ Canale status non trovato!", ephemeral=True)
        else:
            await interaction.response.send_message("⚠️ Canale status non configurato.", ephemeral=True)
    
    def get_status_color(self, status: str) -> discord.Color:
        colors = {
            "appena iniziato": discord.Color.yellow(),
            "a metà": discord.Color.orange(),
            "finito": discord.Color.green()
        }
        return colors.get(status, discord.Color.default())
    
    @discord.app_commands.command(name="emoji_list", description="Mostra le emoji disponibili nel server")
    async def emoji_list(self, interaction: discord.Interaction):
        """Mostra tutte le emoji del server"""
        guild = interaction.guild
        emojis = guild.emojis
        
        if not emojis:
            await interaction.response.send_message("❌ Nessuna emoji personalizzata trovata nel server.", ephemeral=True)
            return
        
        embed = discord.Embed(
            title="🎨 Emoji del Server",
            description="Ecco le emoji disponibili:",
            color=discord.Color.blue()
        )
        
        emoji_list = []
        for emoji in emojis[:15]:  # Limita a 15 per non superare i limiti
            emoji_list.append(f"{emoji} `:{emoji.name}:`")
        
        embed.add_field(
            name="Emoji",
            value="\n".join(emoji_list),
            inline=False
        )
        
        if len(emojis) > 15:
            embed.set_footer(text=f"e altre {len(emojis) - 15} emoji...")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(StatusCog(bot))
