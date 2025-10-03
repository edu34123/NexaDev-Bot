import discord
from discord.ext import commands
from discord import ui
import os

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
        staff_role = guild.get_role(int(os.getenv('STAFF_ROLE_ID')))
        
        # Crea il canale ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages
