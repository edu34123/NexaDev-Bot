import discord
from discord import app_commands
from discord.ext import commands
from utils.config import Config

class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='🤖 Bot Creator', style=discord.ButtonStyle.primary, custom_id='bot_creator')
    async def bot_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Bot Creator")

    @discord.ui.button(label='🖥️ Server Creator', style=discord.ButtonStyle.primary, custom_id='server_creator')
    async def server_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Server Creator")

    @discord.ui.button(label='⚡ Server/Bot Creator', style=discord.ButtonStyle.success, custom_id='both_creator')
    async def both_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Server/Bot Creator")

    @discord.ui.button(label='🤝 Partnership', style=discord.ButtonStyle.secondary, custom_id='partnership')
    async def partnership(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Partnership")

    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        guild = interaction.guild
        category = discord.utils.get(guild.categories, name="TICKETS")
        
        if not category:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                guild.me: discord.PermissionOverwrite(view_channel=True)
            }
            category = await guild.create_category("TICKETS", overwrites=overwrites)

        ticket_channel = await category.create_text_channel(
            f"{ticket_type.lower().replace('/', '-')}-{interaction.user.name}",
            topic=f"Ticket creato da {interaction.user.mention} | Tipo: {ticket_type}"
        )

        # Imposta i permessi del canale
        await ticket_channel.set_permissions(interaction.user, view_channel=True, send_messages=True)
        await ticket_channel.set_permissions(guild.default_role, view_channel=False)

        embed = discord.Embed(
            title=f"🎫 Ticket - {ticket_type}",
            description=f"Grazie per aver aperto un ticket! Lo staff ti aiuterà al più presto.\n\n**Tipo:** {ticket_type}\n**Creato da:** {interaction.user.mention}",
            color=0x00ff00
        )

        view = TicketManagementView()
        await ticket_channel.send(f"<@&{Config.STAFF_ROLE_ID}> {interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(f"Ticket creato: {ticket_channel.mention}", ephemeral=True)

class TicketManagementView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='✅ Claim', style=discord.ButtonStyle.success, custom_id='claim_ticket')
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description=f"🎫 Ticket preso in carico da {interaction.user.mention}",
            color=0x00ff00
        )
        await interaction.response.send_message(embed=embed)
        await interaction.channel.edit(name=f"✅-{interaction.channel.name}")

    @discord.ui.button(label='🔒 Close', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            description="🔒 Ticket in chiusura...",
            color=0xff0000
        )
        await interaction.response.send_message(embed=embed)
        
        # Chiudi il ticket dopo 5 secondi
        await interaction.channel.send("Il ticket verrà chiuso in 5 secondi...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(TicketManagementView())

    @app_commands.command(name="setup_tickets", description="Setup ticket system")
    async def setup_tickets(self, interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message("Non hai i permessi per eseguire questo comando!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🎫 **Sistema Ticket NexaDev**",
            description="Seleziona il tipo di ticket che vuoi aprire:\n\n"
                       "🤖 **Bot Creator** - Richiedi la creazione di un bot\n"
                       "🖥️ **Server Creator** - Richiedi la creazione di un server\n"
                       "⚡ **Server/Bot Creator** - Richiedi entrambi\n"
                       "🤝 **Partnership** - Richiedi una partnership",
            color=0x7289da
        )

        await interaction.channel.send(embed=embed, view=TicketView())
        await interaction.response.send_message("Sistema ticket impostato!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
