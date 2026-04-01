from discord import Interaction
from discord.ext import commands
from utils.constants import blank_color
from utils.mc_api import ServerKey
from utils.utils import config_change_log
import discord

class CustomModal(discord.ui.Modal, title="Edit Reason"):
    def __init__(self, title, options, epher_args: dict = None):
        # 🏗️ Initializing Custom Modal...
        super().__init__(title=title)
        if epher_args is None:
            epher_args = {}
        self.saved_items = {}
        self.epher_args = epher_args
        self.interaction = None

        # 🧩 Adding items to modal...
        for name, option in options:
            self.add_item(option)
            self.saved_items[name] = option

    async def on_submit(self, interaction: discord.Interaction):
        # 📤 Handling modal submission...
        for key, item in self.saved_items.items():
            setattr(self, key, item)
        self.interaction = interaction
        # ⏳ Deferring response...
        await interaction.response.defer(**self.epher_args)
        self.stop()

class MapleCountyConfiguration(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, settings: dict = None):
        # ⚙️ Initializing Maple County Configuration view...
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.settings = settings or {}

    @discord.ui.button(label="Automatic Discord Checks", style=discord.ButtonStyle.secondary)
    async def automatic_discord_checks(self, interaction: Interaction, button: discord.ui.Button):
        # 🔍 Opening automatic discord checks configuration...
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            sett = {"_id": interaction.guild.id}
        
        view = MCDiscordCheckConfig(self.bot, interaction.user.id, sett)
        
        discord_checks = sett.get('MC', {}).get('discord_checks', {})
        
        # 📄 Sending configuration message...
        embed = discord.Embed(
            title="Automatic Discord Checks",
            description=(
                "> This module allows for automatic checks on Discord accounts of players in your Maple County server."
            ),
            color=blank_color,
        ).add_field(
            name="Alert Channel",
            value=f"> Players that aren't in the Discord server will be sent in this channel.",
            inline=False,
        )
        
        await interaction.response.send_message(
            embed=embed,
            view=view,
            ephemeral=True,
        )

class MCDiscordCheckConfig(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, settings: dict = None):
        # 🛠️ Initializing MC Discord Check Config view...
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id
        self.settings = settings or {}
        
        # ➕ Adding dropdowns to view...
        self.add_item(self.create_select())
        self.add_item(self.create_channel_select())
    
    def create_select(self):
        # 🔘 Creating enable/disable selection dropdown...
        select = discord.ui.Select(
            placeholder="Enable/Disable Discord Checks",
            options=[
                discord.SelectOption(
                    label="Enable Discord Checks", 
                    value="enable",
                    default=self.settings.get('MC', {}).get('discord_checks', {}).get('enabled', False)
                ),
                discord.SelectOption(
                    label="Disable Discord Checks", 
                    value="disable",
                    default=not self.settings.get('MC', {}).get('discord_checks', {}).get('enabled', False)
                ),
            ],
            row=0
        )
        select.callback = self.select_callback
        return select
    
    def create_channel_select(self):
        # 📺 Creating channel selection dropdown...
        current_channel_id = self.settings.get('MC', {}).get('discord_checks', {}).get('channel_id')
        default_values = [discord.Object(id=current_channel_id)] if current_channel_id else None
        
        channel_select = discord.ui.ChannelSelect(
            placeholder="Select Alert Channel",
            channel_types=[discord.ChannelType.text],
            max_values=1,
            default_values=default_values,
            row=1
        )
        channel_select.callback = self.channel_select_callback
        return channel_select
    
    async def select_callback(self, interaction: Interaction):
        # 🔄 Handling status selection change...
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You are not permitted to interact with this dropdown.",
                ephemeral=True
            )
            return
            
        if interaction.data['values']:
            selected_value = interaction.data['values'][0]

            sett = await self.bot.settings.find_by_id(interaction.guild.id)
            if not sett:
                sett = {"_id": interaction.guild.id}

            if "MC" not in sett:
                sett["MC"] = {}
            if "discord_checks" not in sett["MC"]:
                sett["MC"]["discord_checks"] = {"enabled": False}
            
            # 💾 Updating status in database...
            if selected_value == "enable":
                sett["MC"]["discord_checks"]["enabled"] = True
                status = "enabled"
            elif selected_value == "disable":
                sett["MC"]["discord_checks"]["enabled"] = False
                status = "disabled"
            
            await self.bot.settings.upsert(sett)
            
            # 📝 Logging update...
            await config_change_log(
                self.bot, 
                interaction.guild, 
                interaction.user, 
                f"MC Discord Checks have been {status}."
            )
            
            await interaction.response.send_message(
                f"Discord Checks have been {status}.",
                ephemeral=True,
            )
        else:
            await interaction.response.send_message("No option selected.", ephemeral=True)

    async def channel_select_callback(self, interaction: Interaction):
        # 📡 Handling alert channel selection change...
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(
                "You are not permitted to interact with this dropdown.",
                ephemeral=True
            )
            return

        channel_select = None
        for component in self.children:
            if isinstance(component, discord.ui.ChannelSelect):
                channel_select = component
                break
        
        channel_id = channel_select.values[0].id if channel_select and channel_select.values else None

        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            sett = {"_id": interaction.guild.id}

        if "MC" not in sett:
            sett["MC"] = {}
        if "discord_checks" not in sett["MC"]:
            sett["MC"]["discord_checks"] = {"enabled": False}

        # 💾 Updating channel in database...
        sett["MC"]["discord_checks"]["channel_id"] = channel_id # 💾 Saving channel ID

        await self.bot.settings.upsert(sett) # 📥 Upserting settings

        # 📝 Logging update...
        await config_change_log( # 📜 Logging the change
            self.bot, # 🤖 Bot instance
            interaction.guild, # 🏰 Guild instance
            interaction.user, # 👤 User instance
            f"MC Discord Checks alert channel set to <#{channel_id}>." # ✍️ Log message
        )


        await interaction.response.send_message(
            f"Alert channel set to <#{channel_id}>.",
            ephemeral=True
        )