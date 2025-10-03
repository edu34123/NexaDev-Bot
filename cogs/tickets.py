import os
import discord
from discord.ext import commands
from discord import ui
import asyncio

def get_env_var(var_name, default=None):
    value = os.getenv(var_name)
    if not value and default is None:
        print(f"⚠️ Variabile {var_name} non trovata")
    return value or default

class TicketView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Bot Creator', style=discord.ButtonStyle.primary, custom_id='bot_creator')
    async def bot_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Bot Creator")
    
    @discord.ui.button(label='Server Creator', style=discord.ButtonStyle.success, custom_id='server_creator')
    async def server_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Server Creator")
    
    @discord.ui.button(label='Server/Bot Creator', style=discord.ButtonStyle.secondary, custom_id='both_creator')
    async def both_creator(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Server/Bot Creator")
    
    @discord.ui.button(label='Partnership', style=discord.ButtonStyle.danger, custom_id='partnership')
    async def partnership(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.create_ticket(interaction, "Partnership")
    
    async def create_ticket(self, interaction: discord.Interaction, ticket_type: str):
        guild = interaction.guild
        staff_role_id = get_env_var('STAFF_ROLE_ID')
        
        if not staff_role_id:
            await interaction.response.send_message(
                "❌ Errore di configurazione: ruolo staff non configurato.",
                ephemeral=True
            )
            return
        
        staff_role = guild.get_role(int(staff_role_id))
        if not staff_role:
            await interaction.response.send_message(
                "❌ Ruolo staff non trovato nel server.",
                ephemeral=True
            )
            return
        
        # Crea il canale ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            staff_role: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        channel = await guild.create_text_channel(
            name=f"ticket-{ticket_type.lower()}-{interaction.user.name}",
            overwrites=overwrites,
            topic=f"Ticket {ticket_type} di {interaction.user.display_name}"
        )
        
        # Embed del ticket
        embed = discord.Embed(
            title=f"Ticket {ticket_type}",
            description=f"Grazie per aver aperto un ticket {ticket_type}!\nLo staff ti aiuterà al più presto.",
            color=discord.Color.blue()
        )
        embed.add_field(name="Creato da", value=interaction.user.mention, inline=True)
        embed.add_field(name="Tipo", value=ticket_type, inline=True)
        
        view = TicketManagementView()
        
        await channel.send(f"{staff_role.mention} {interaction.user.mention}", embed=embed, view=view)
        await interaction.response.send_message(f"✅ Ticket creato! {channel.mention}", ephemeral=True)

class TicketManagementView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label='Claim', style=discord.ButtonStyle.success, custom_id='claim_ticket')
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Ticket Claimed",
            description=f"Il ticket è stato preso in carico da {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    
    @discord.ui.button(label='Close', style=discord.ButtonStyle.danger, custom_id='close_ticket')
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="Ticket Chiuso",
            description="Il ticket verrà chiuso in 5 secondi...",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class TicketCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketView())
        self.bot.add_view(TicketManagementView())
    
    @discord.app_commands.command(name="setup_tickets", description="Setup del sistema di ticket")
    @discord.app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction):
        """Setup del sistema di ticket"""
        embed = discord.Embed(
            title="NexaDev - Supporto",
            description="Seleziona il tipo di assistenza di cui hai bisogno:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Bot Creator", value="Richiedi la creazione di un bot", inline=True)
        embed.add_field(name="Server Creator", value="Richiedi la creazione di un server", inline=True)
        embed.add_field(name="Server/Bot Creator", value="Richiedi entrambi i servizi", inline=True)
        embed.add_field(name="Partnership", value="Richiedi una partnership", inline=True)
        
        view = TicketView()
        await interaction.response.send_message(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(TicketCog(bot))
