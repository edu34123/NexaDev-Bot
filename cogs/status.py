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
        # Prima cerca le emoji personalizzate nel server
        for emoji_name in emoji_names:
            for emoji in guild.emojis:
                if emoji.name.lower() == emoji_name.lower():
                    return str(emoji)
        
        # Fallback a Unicode solo se non trova emoji personalizzate
        fallback_emojis = {
            "red_loading1": "🟡",
            "loading_orange": "🟠", 
            "green_loading1": "🟢",
            "computer": "🖥️",
            "robot": "🤖",
            "zap": "⚡",
            "caricamento": "⏳",
            "loading": "⏳",
            "waiting": "⏳",
            "hourglass": "⏳"
        }
        
        for emoji_name in emoji_names:
            if emoji_name.lower() in fallback_emojis:
                return fallback_emojis[emoji_name.lower()]
        
        return "⚪"  # Fallback ultima risorsa
    
    # COMANDO ITALIANO
    @discord.app_commands.command(name="status_ita", description="Aggiorna lo status di un progetto in italiano")
    @discord.app_commands.describe(
        nome="Tipo di progetto",
        modalità="Stato del progetto",
        persona="Persona per cui è il progetto (menzione)",
        descrizione="Descrizione del progetto (opzionale)",
        invito="Link invito server Discord (opzionale)"
    )
    @discord.app_commands.choices(
        nome=[
            discord.app_commands.Choice(name="server", value="server"),
            discord.app_commands.Choice(name="bot", value="bot"),
            discord.app_commands.Choice(name="server e bot", value="server e bot")
        ],
        modalità=[
            discord.app_commands.Choice(name="in attesa", value="in attesa"),
            discord.app_commands.Choice(name="appena iniziato", value="appena iniziato"),
            discord.app_commands.Choice(name="a metà", value="a metà"),
            discord.app_commands.Choice(name="finito", value="finito")
        ]
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def status_ita(self, interaction: discord.Interaction, nome: str, modalità: str, persona: discord.Member, descrizione: str = None, invito: str = None):
        """Aggiorna lo status di un progetto in italiano"""
        await self._handle_status(interaction, nome, modalità, persona, descrizione, invito, "it")
    
    # COMANDO INGLESE
    @discord.app_commands.command(name="status_eng", description="Update project status in English")
    @discord.app_commands.describe(
        name="Project type",
        mode="Project status", 
        person="Person for whom the project is (mention)",
        description="Project description (optional)",
        invite="Discord server invite link (optional)"
    )
    @discord.app_commands.choices(
        name=[
            discord.app_commands.Choice(name="server", value="server"),
            discord.app_commands.Choice(name="bot", value="bot"),
            discord.app_commands.Choice(name="server and bot", value="server e bot")
        ],
        mode=[
            discord.app_commands.Choice(name="waiting", value="in attesa"),
            discord.app_commands.Choice(name="just started", value="appena iniziato"),
            discord.app_commands.Choice(name="halfway", value="a metà"),
            discord.app_commands.Choice(name="finished", value="finito")
        ]
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def status_eng(self, interaction: discord.Interaction, name: str, mode: str, person: discord.Member, description: str = None, invite: str = None):
        """Update project status in English"""
        await self._handle_status(interaction, name, mode, person, description, invite, "en")
    
    async def _handle_status(self, interaction: discord.Interaction, nome: str, modalità: str, persona: discord.Member, descrizione: str = None, invito: str = None, language: str = "it"):
        """Gestisce lo status in base alla lingua"""
        
        guild = interaction.guild
        
        # Configurazione emoji di stato - PRIMA cerca queste nel server
        status_emoji_config = {
            "in attesa": ["caricamento", "loading", "waiting", "hourglass"],
            "appena iniziato": ["red_loading1", "redloading", "loading_red"],
            "a metà": ["loading_orange", "orange_loading", "loading_orange"], 
            "finito": ["green_loading1", "greenloading", "loading_green"]
        }
        
        # Configurazione emoji progetti - PRIMA cerca queste nel server
        project_emoji_config = {
            "server": ["computer", "server", "desktop"],
            "bot": ["robot", "bot", "robot_face"],
            "server e bot": ["zap", "lightning", "both"],
            "server and bot": ["zap", "lightning", "both"]
        }
        
        # Ottieni le emoji - PRIMA cerca nel server
        emoji_status = await self.get_custom_emoji(guild, status_emoji_config.get(modalità, ["yellow_circle"]))
        emoji_project = await self.get_custom_emoji(guild, project_emoji_config.get(nome, ["computer"]))
        
        # Testi multilingua
        texts = {
            "it": {
                "title": f"{emoji_project} {nome.title()} - {modalità.title()}",
                "client": "👤 Cliente",
                "status": "📊 Stato", 
                "type": "🛠️ Tipo",
                "description": "📝 Descrizione",
                "invite": "🔗 Invito",
                "updated_by": "Aggiornato da",
                "success": "✅ Status aggiornato con successo!",
                "channel_not_found": "❌ Canale status italiano non trovato!",
                "channel_not_configured": "⚠️ Canale status italiano non configurato.",
                "dm_error": "❌ Impossibile inviare DM a {mention}",
                "progress_notification": "✅ Notifica di progresso inviata a {mention}",
                "start_notification": "✅ Notifica di inizio inviata a {mention}",
                "waiting_notification": "✅ Notifica di attesa inviata a {mention}",
                "completion_notification": "✅ Notifica di completamento inviata in DM a {mention}",
                "status_names": {
                    "in attesa": "In Attesa",
                    "appena iniziato": "Appena Iniziato",
                    "a metà": "A Metà", 
                    "finito": "Finito"
                },
                "project_names": {
                    "server": "Server",
                    "bot": "Bot",
                    "server e bot": "Server e Bot"
                },
                "dm_titles": {
                    "in attesa": f"{emoji_status} Progetto in Attesa",
                    "appena iniziato": f"{emoji_status} Progetto Iniziato!",
                    "a metà": f"{emoji_status} Progresso Progetto", 
                    "finito": f"{emoji_status} Il tuo progetto è pronto!"
                },
                "dm_descriptions": {
                    "in attesa": "Il tuo **{nome}** è in attesa di essere preso in carico!",
                    "appena iniziato": "Abbiamo iniziato a lavorare sul tuo **{nome}**!",
                    "a metà": "Il tuo **{nome}** è a metà del sviluppo!",
                    "finito": "Il tuo **{nome}** è stato completato!"
                },
                "dm_status": {
                    "in attesa": "In Attesa",
                    "appena iniziato": "Appena Iniziato",
                    "a metà": "In Lavorazione", 
                    "finito": "Completato"
                },
                "dm_footers": {
                    "in attesa": "NexaDev - Ti contatteremo presto!",
                    "appena iniziato": "NexaDev - Sviluppo in corso!",
                    "a metà": "NexaDev - Ti terremo aggiornato!",
                    "finito": "Grazie per aver scelto NexaDev!"
                }
            },
            "en": {
                "title": f"{emoji_project} {nome.replace('server e bot', 'Server & Bot').title()} - {self._get_english_status(modalità)}",
                "client": "👤 Client", 
                "status": "📊 Status",
                "type": "🛠️ Type",
                "description": "📝 Description",
                "invite": "🔗 Invite",
                "updated_by": "Updated by",
                "success": "✅ Status updated successfully!",
                "channel_not_found": "❌ English status channel not found!",
                "channel_not_configured": "⚠️ English status channel not configured.",
                "dm_error": "❌ Cannot send DM to {mention}",
                "progress_notification": "✅ Progress notification sent to {mention}",
                "start_notification": "✅ Start notification sent to {mention}",
                "waiting_notification": "✅ Waiting notification sent to {mention}",
                "completion_notification": "✅ Completion notification sent via DM to {mention}",
                "status_names": {
                    "in attesa": "Waiting",
                    "appena iniziato": "Just Started",
                    "a metà": "Halfway",
                    "finito": "Finished"
                },
                "project_names": {
                    "server": "Server",
                    "bot": "Bot", 
                    "server e bot": "Server & Bot",
                    "server and bot": "Server & Bot"
                },
                "dm_titles": {
                    "in attesa": f"{emoji_status} Project Waiting",
                    "appena iniziato": f"{emoji_status} Project Started!",
                    "a metà": f"{emoji_status} Project Progress",
                    "finito": f"{emoji_status} Your Project is Ready!"
                },
                "dm_descriptions": {
                    "in attesa": "Your **{nome}** is waiting to be taken over!",
                    "appena iniziato": "We've started working on your **{nome}**!",
                    "a metà": "Your **{nome}** is halfway through development!",
                    "finito": "Your **{nome}** has been completed!"
                },
                "dm_status": {
                    "in attesa": "Waiting",
                    "appena iniziato": "Just Started",
                    "a metà": "In Progress",
                    "finito": "Completed"
                },
                "dm_footers": {
                    "in attesa": "NexaDev - We'll contact you soon!",
                    "appena iniziato": "NexaDev - Development in progress!",
                    "a metà": "NexaDev - We'll keep you updated!",
                    "finito": "Thank you for choosing NexaDev!"
                }
            }
        }
        
        lang_texts = texts.get(language, texts["it"])
        
        # Crea l'embed per il canale status
        embed = discord.Embed(
            title=lang_texts["title"],
            color=self.get_status_color(modalità)
        )
        
        embed.add_field(name=lang_texts["client"], value=persona.mention, inline=True)
        embed.add_field(name=lang_texts["status"], value=f"{emoji_status} {lang_texts['status_names'][modalità]}", inline=True)
        embed.add_field(name=lang_texts["type"], value=lang_texts["project_names"].get(nome, nome.title()), inline=True)
        
        if descrizione:
            embed.add_field(name=lang_texts["description"], value=descrizione, inline=False)
            
        if invito:
            embed.add_field(name=lang_texts["invite"], value=f"[{lang_texts['invite'].replace('🔗 ', '')}]({invito})", inline=True)
        
        embed.set_footer(text=f"{lang_texts['updated_by']} {interaction.user.display_name}")
        
        # CANALI SEPARATI PER LINGUA
        if language == "it":
            channel_id = get_env_var('STATUS_CHANNEL_ITA_ID')
            fallback_channel_id = get_env_var('STATUS_CHANNEL_ID')
        else:  # en
            channel_id = get_env_var('STATUS_CHANNEL_ENG_ID')
            fallback_channel_id = get_env_var('STATUS_CHANNEL_ID')
        
        target_channel_id = channel_id or fallback_channel_id
        
        if target_channel_id:
            channel = self.bot.get_channel(int(target_channel_id))
            if channel:
                await channel.send(embed=embed)
                await interaction.response.send_message(lang_texts["success"], ephemeral=True)
                
                # Notifica la persona via DM in base allo stato
                try:
                    dm_embed = discord.Embed(
                        title=lang_texts["dm_titles"][modalità],
                        description=lang_texts["dm_descriptions"][modalità].format(nome=lang_texts["project_names"].get(nome, nome.title())),
                        color=self.get_status_color(modalità)
                    )
                    dm_embed.add_field(name=lang_texts["status"], value=f"{emoji_status} {lang_texts['dm_status'][modalità]}", inline=True)
                    dm_embed.add_field(name=lang_texts["type"], value=lang_texts["project_names"].get(nome, nome.title()), inline=True)
                    
                    if descrizione:
                        dm_embed.add_field(name=lang_texts["description"], value=descrizione, inline=False)
                    
                    if invito and modalità == "finito":
                        dm_embed.add_field(name=lang_texts["invite"], value=f"[{lang_texts['invite'].replace('🔗 ', '')}]({invito})", inline=False)
                    
                    dm_embed.set_footer(text=lang_texts["dm_footers"][modalità])
                    
                    await persona.send(embed=dm_embed)
                    
                    # Se c'è l'invito e il progetto è finito, invialo anche come messaggio separato
                    if invito and modalità == "finito":
                        invite_texts = {
                            "it": f"**🔗 Invito al tuo server:** {invito}",
                            "en": f"**🔗 Invite to your server:** {invito}"
                        }
                        await persona.send(invite_texts.get(language, invite_texts["it"]))
                    
                    # Messaggio di conferma
                    if modalità == "finito":
                        await interaction.followup.send(lang_texts["completion_notification"].format(mention=persona.mention), ephemeral=True)
                    elif modalità == "a metà":
                        await interaction.followup.send(lang_texts["progress_notification"].format(mention=persona.mention), ephemeral=True)
                    elif modalità == "appena iniziato":
                        await interaction.followup.send(lang_texts["start_notification"].format(mention=persona.mention), ephemeral=True)
                    elif modalità == "in attesa":
                        await interaction.followup.send(lang_texts["waiting_notification"].format(mention=persona.mention), ephemeral=True)
                        
                except discord.Forbidden:
                    await interaction.followup.send(lang_texts["dm_error"].format(mention=persona.mention), ephemeral=True)
            else:
                await interaction.response.send_message(lang_texts["channel_not_found"], ephemeral=True)
        else:
            await interaction.response.send_message(lang_texts["channel_not_configured"], ephemeral=True)
    
    def _get_english_status(self, status: str) -> str:
        """Converte lo status in inglese"""
        status_map = {
            "in attesa": "Waiting",
            "appena iniziato": "Just Started",
            "a metà": "Halfway", 
            "finito": "Finished"
        }
        return status_map.get(status, status.title())
    
    # COMANDI STATUS FINITO
    @discord.app_commands.command(name="statusfinito_ita", description="Marca un progetto come finito e invia invito al cliente (Italiano)")
    @discord.app_commands.describe(
        persona="Persona per cui è il progetto (menzione)",
        descrizione="Descrizione del progetto",
        invito="Invito al server Discord",
        nome="Tipo di progetto (opzionale)"
    )
    @discord.app_commands.choices(
        nome=[
            discord.app_commands.Choice(name="server", value="server"),
            discord.app_commands.Choice(name="bot", value="bot"),
            discord.app_commands.Choice(name="server e bot", value="server e bot")
        ]
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def statusfinito_ita(self, interaction: discord.Interaction, persona: discord.Member, descrizione: str, invito: str, nome: str = "server"):
        """Marca un progetto come finito in italiano"""
        await self._handle_finished_status(interaction, persona, descrizione, invito, nome, "it")
    
    @discord.app_commands.command(name="statusfinished_eng", description="Mark project as finished and send invite to client (English)")
    @discord.app_commands.describe(
        person="Person for whom the project is (mention)",
        description="Project description", 
        invite="Discord server invite",
        name="Project type (optional)"
    )
    @discord.app_commands.choices(
        name=[
            discord.app_commands.Choice(name="server", value="server"),
            discord.app_commands.Choice(name="bot", value="bot"),
            discord.app_commands.Choice(name="server and bot", value="server e bot")
        ]
    )
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def statusfinished_eng(self, interaction: discord.Interaction, person: discord.Member, description: str, invite: str, name: str = "server"):
        """Mark project as finished in English"""
        await self._handle_finished_status(interaction, person, description, invite, name, "en")
    
    async def _handle_finished_status(self, interaction: discord.Interaction, persona: discord.Member, descrizione: str, invito: str, nome: str, language: str):
        """Gestisce lo status finito in base alla lingua"""
        
        guild = interaction.guild
        
        # Configurazione emoji - PRIMA cerca nel server
        status_emoji_config = {
            "finito": ["green_loading1", "greenloading", "loading_green"]
        }
        
        project_emoji_config = {
            "server": ["computer", "server", "desktop"],
            "bot": ["robot", "bot", "robot_face"],
            "server e bot": ["zap", "lightning", "both"]
        }
        
        # Ottieni le emoji - PRIMA cerca nel server
        emoji_status = await self.get_custom_emoji(guild, status_emoji_config.get("finito", ["green_circle"]))
        emoji_project = await self.get_custom_emoji(guild, project_emoji_config.get(nome, ["computer"]))
        
        # Testi multilingua
        texts = {
            "it": {
                "status_title": f"{emoji_project} {nome.title()} - Completato {emoji_status}",
                "client": "👤 Cliente",
                "status": "📊 Stato",
                "type": "🛠️ Tipo", 
                "description": "📝 Descrizione",
                "invite": "🔗 Invito",
                "completed_by": "Completato da",
                "dm_title": f"{emoji_status} Il tuo progetto è pronto!",
                "dm_description": f"Il tuo **{nome.title()}** è stato completato con successo!",
                "developer": "🛠️ Sviluppatore",
                "footer": "Grazie per aver scelto NexaDev! 💫",
                "invite_title": "🔗 Invito al Tuo Server",
                "invite_description": f"**Clicca sul link qui sotto per entrare nel server:**\n{invito}",
                "success": f"✅ Progetto marcato come completato e notifica inviata a {persona.mention}!",
                "dm_error": f"❌ Impossibile inviare DM a {persona.mention}. Il progetto è stato comunque marcato come completato.",
                "channel_error": "❌ Canale status italiano non trovato!",
                "config_error": "⚠️ Canale status italiano non configurato."
            },
            "en": {
                "status_title": f"{emoji_project} {nome.replace('server e bot', 'Server & Bot').title()} - Completed {emoji_status}",
                "client": "👤 Client",
                "status": "📊 Status", 
                "type": "🛠️ Type",
                "description": "📝 Description",
                "invite": "🔗 Invite",
                "completed_by": "Completed by",
                "dm_title": f"{emoji_status} Your Project is Ready!",
                "dm_description": f"Your **{nome.replace('server e bot', 'Server & Bot').title()}** has been successfully completed!",
                "developer": "🛠️ Developer",
                "footer": "Thank you for choosing NexaDev! 💫",
                "invite_title": "🔗 Invite to Your Server", 
                "invite_description": f"**Click the link below to join the server:**\n{invito}",
                "success": f"✅ Project marked as completed and notification sent to {persona.mention}!",
                "dm_error": f"❌ Cannot send DM to {persona.mention}. Project was still marked as completed.",
                "channel_error": "❌ English status channel not found!",
                "config_error": "⚠️ English status channel not configured."
            }
        }
        
        lang_texts = texts.get(language, texts["it"])
        
        # Embed per il canale status
        status_embed = discord.Embed(
            title=lang_texts["status_title"],
            color=discord.Color.green()
        )
        
        status_embed.add_field(name=lang_texts["client"], value=persona.mention, inline=True)
        status_embed.add_field(name=lang_texts["status"], value=f"{emoji_status} Completato", inline=True)
        status_embed.add_field(name=lang_texts["type"], value=nome.replace('server e bot', 'Server & Bot').title(), inline=True)
        status_embed.add_field(name=lang_texts["description"], value=descrizione, inline=False)
        status_embed.add_field(name=lang_texts["invite"], value=f"[{lang_texts['invite'].replace('🔗 ', '')}]({invito})", inline=True)
        
        status_embed.set_footer(text=f"{lang_texts['completed_by']} {interaction.user.display_name}")
        
        # Embed per il DM del cliente
        dm_embed = discord.Embed(
            title=lang_texts["dm_title"],
            description=lang_texts["dm_description"],
            color=discord.Color.green()
        )
        
        dm_embed.add_field(name=lang_texts["description"], value=descrizione, inline=False)
        dm_embed.add_field(name=lang_texts["invite"], value=f"[{lang_texts['invite'].replace('🔗 ', '')}]({invito})", inline=True)
        dm_embed.add_field(name=lang_texts["developer"], value=interaction.user.mention, inline=True)
        
        dm_embed.set_footer(text=lang_texts["footer"])
        
        # CANALI SEPARATI PER LINGUA
        if language == "it":
            channel_id = get_env_var('STATUS_CHANNEL_ITA_ID')
            fallback_channel_id = get_env_var('STATUS_CHANNEL_ID')
        else:  # en
            channel_id = get_env_var('STATUS_CHANNEL_ENG_ID')
            fallback_channel_id = get_env_var('STATUS_CHANNEL_ID')
        
        target_channel_id = channel_id or fallback_channel_id
        
        if target_channel_id:
            channel = self.bot.get_channel(int(target_channel_id))
            if channel:
                await channel.send(embed=status_embed)
                
                # Invia DM al cliente
                try:
                    await persona.send(embed=dm_embed)
                    
                    # Invia anche l'invito come messaggio separato
                    invite_embed = discord.Embed(
                        title=lang_texts["invite_title"],
                        description=lang_texts["invite_description"],
                        color=discord.Color.blue()
                    )
                    await persona.send(embed=invite_embed)
                    
                    await interaction.response.send_message(lang_texts["success"], ephemeral=True)
                    
                except discord.Forbidden:
                    await interaction.response.send_message(lang_texts["dm_error"], ephemeral=True)
            else:
                await interaction.response.send_message(lang_texts["channel_error"], ephemeral=True)
        else:
            await interaction.response.send_message(lang_texts["config_error"], ephemeral=True)
    
    def get_status_color(self, status: str) -> discord.Color:
        colors = {
            "in attesa": discord.Color.light_gray(),
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
        
        # Crea una lista di emoji con i loro nomi
        emoji_list = []
        for emoji in emojis[:20]:  # Mostra massimo 20 emoji
            emoji_list.append(f"{emoji} `:{emoji.name}:`")
        
        embed = discord.Embed(
            title="🎨 Emoji del Server Disponibili",
            description="Ecco le emoji che puoi usare nei comandi status:",
            color=discord.Color.blue()
        )
        
        embed.add_field(
            name="Emoji (clicca per copiare il nome)",
            value="\n".join(emoji_list),
            inline=False
        )
        
        if len(emojis) > 20:
            embed.set_footer(text=f"e altre {len(emojis) - 20} emoji...")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(StatusCog(bot))
