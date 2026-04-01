from discord.ext import commands
from utils.constants import blank_color
from utils.utils import config_change_log
import discord

class callSignCheck(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, settings: dict = None):
        # 🚀 Initializing the Call Sign Check view...
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.settings = settings or {}

        # 🔘 Creating the selection dropdown...
        self.enabled_select = discord.ui.Select(
            placeholder="Select an option...",
            options=[
                discord.SelectOption(label="Enabled", value="enabled"),
                discord.SelectOption(label="Disabled", value="disabled"),
            ]
        )
        self.enabled_select.callback = self.enabled_callback
        self.add_item(self.enabled_select)

        # ➕ Creating the add whitelist button...
        self.add_whitelist_button = discord.ui.Button(
            label="Add Whitelist",
            style=discord.ButtonStyle.green,
            custom_id="add_whitelist"
        )
        self.add_whitelist_button.callback = self.add_whitelist_callback
        self.add_item(self.add_whitelist_button)

        # ❌ Creating the delete whitelist button...
        self.delete_whitelist_button = discord.ui.Button(
            label="Delete Whitelist",
            style=discord.ButtonStyle.red,
            custom_id="delete_whitelist"
        )
        self.delete_whitelist_button.callback = self.delete_whitelist_callback
        self.add_item(self.delete_whitelist_button)

    async def enabled_callback(self, interaction: discord.Interaction):
        # 🔄 Handling selection changes...
        selected_value = self.enabled_select.values[0]
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            sett = {}
        
        # 💾 Updating settings in the database...
        sett['ERLC']['callsign_check'] = {
            'enabled': selected_value == 'enabled'
        }
        await self.bot.settings.update_by_id(sett)

        # 📄 Creating response embed...
        embed = discord.Embed(
            title="Call Sign Check Status Updated",
            description=f"Call Sign Check is now **{selected_value.capitalize()}**.",
            color=blank_color
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def add_whitelist_callback(self, interaction: discord.Interaction):
        # 📝 Opening whitelist addition UI...
        embed = discord.Embed(
            title="This is a add whitelist UI",
            description="DUMMY",
            color=blank_color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def delete_whitelist_callback(self, interaction: discord.Interaction):
        # 🗑️ Opening whitelist deletion UI...
        embed = discord.Embed(
            title="This is a delete whitelist UI",
            description="DUMMY",
            color=blank_color
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)