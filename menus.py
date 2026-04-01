import asyncio  # ⏳ Importing asyncio...
import datetime  # 📅 Importing datetime...
import string  # 🔠 Importing string utilities...
import typing  # ⌨️ Importing typing support...
import discord  # 🎮 Importing discord library...
import pytz  # 🌍 Importing timezone utilities...
import logging  # 📝 Importing logging module...
import roblox  # 🧱 Importing Roblox API...
from discord import Interaction  # 🖱️ Importing Interaction type...
from discord.ext import commands  # 🛠️ Importing extension commands...
from oauth2client.service_account import ServiceAccountCredentials  # 🔑 Importing auth credentials...
from bson import ObjectId  # 🆔 Importing MongoDB ObjectId...
from datamodels.ShiftManagement import ShiftItem  # ⏱️ Importing ShiftItem model...
from utils.constants import (  # 📦 Importing constants...
    blank_color,  # ⚪ Color constant...
    BLANK_COLOR,  # ⚪ Color constant...
    GREEN_COLOR,  # 🟢 Color constant...
    ORANGE_COLOR,  # 🟠 Color constant...
    RED_COLOR,  # 🔴 Color constant...
    SERVER_CONDITIONS as server_conditions,  # 📋 Server conditions...
    RELEVANT_DESCRIPTIONS as relevant_descriptions,  # 📝 Relevant descriptions...
    CONDITION_OPTIONS as condition_options,  # ⚙️ Condition options...
    OPTION_DESCRIPTIONS as option_descriptions,  # 📖 Option descriptions...
)
from utils.timestamp import td_format  # ⏰ Importing time formatter...
from utils.utils import (  # 🛠️ Importing general utilities...
    int_invis_embed,  # 👻 Invisible embed utility...
    int_failure_embed,  # ❌ Failure embed utility...
    int_pending_embed,  # ⏳ Pending embed utility...
    time_converter,  # 🕒 Time conversion utility...
    get_elapsed_time,  # ⌛ Elapsed time utility...
    generalised_interaction_check_failure,  # ⚠️ Failure handler...
    generator,  # 🔄 Generator utility...
    ArgumentMockingInstance,  # 🎭 Argument mocking...
    config_change_log,  # 📜 Config change logger...
    admin_check,  # 🛡️ Admin check utility...
)
import gspread  # 📊 Importing gspread for sheets...
import random  # 🎲 Importing random utilities...

from ui.ERLC import (  # 📁 Importing ERLC UI...
    callSignCheck  # 🆔 Call sign validator...
)

REQUIREMENTS = ["gspread", "oauth2client"]  # 📋 Dependency requirements...


class Setup(discord.ui.View):  # 🏗️ Setup view class...
    def __init__(self, user_id):  # 🛠️ Initializing view...
        # 🏗️ Initializing Setup view...
        super().__init__(timeout=600.0)  # ⏰ Setting view timeout...
        self.value = None  # 💾 Initializing value...
        self.user_id = user_id  # 👤 Storing user ID...

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="All", style=discord.ButtonStyle.green)  # 🟢 'All' button...
    async def all(self, interaction: discord.Interaction, button: discord.ui.Button):  # 🔘 Button callback...
        # ✅ Handling 'All' button press...
        if interaction.user.id != self.user_id:  # 🔐 Check user authorization...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            return await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...

        await interaction.response.defer()  # 🔄 Deferring interaction...
        self.value = "all"  # 💾 Setting value to 'all'...
        self.stop()  # 🛑 Stopping the view...

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Punishments", style=discord.ButtonStyle.blurple)  # ⚖️ 'Punishments' button...
    async def punishments(  # 🔘 Button callback...
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🖱️ Handler params...
    ):
        # ⚖️ Handling 'Punishments' button press...
        if interaction.user.id != self.user_id:  # 🔐 Check user authorization...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            return await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...

        await interaction.response.defer()  # 🔄 Deferring interaction...
        self.value = "punishments"  # 💾 Setting value to 'punishments'...
        self.stop()  # 🛑 Stopping the view...

    @discord.ui.button(label="Staff Management", style=discord.ButtonStyle.blurple)  # 👥 'Staff' button...
    async def staff_management(  # 🔘 Button callback...
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🖱️ Handler params...
    ):
        # 👥 Handling 'Staff Management' button press...
        if interaction.user.id != self.user_id:  # 🔐 Check user authorization...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            return await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...

        await interaction.response.defer()  # 🔄 Deferring interaction...
        self.value = "staff management"  # 💾 Setting value to 'staff management'...
        self.stop()  # 🛑 Stopping the view...

    @discord.ui.button(label="Shift Management", style=discord.ButtonStyle.blurple)  # ⏱️ 'Shift' button...
    async def shift_management(  # 🔘 Button callback...
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🖱️ Handler params...
    ):
        # ⏱️ Handling 'Shift Management' button press...
        if interaction.user.id != self.user_id: # 🔐 Checking user authorization
            await interaction.response.defer(ephemeral=True, thinking=True) # ⏳ Deferring response
            return await generalised_interaction_check_failure(interaction.followup) # ⚠️ Failing check

        # 📄 Finalizing selection...
        await interaction.response.defer() # 🔄 Deferring interaction
        self.value = "shift management" # 💾 Setting value to 'shift management'
        self.stop() # 🛑 Stopping the view



class Dropdown(discord.ui.Select):  # 🔘 Dropdown class...
    def __init__(self, user_id):  # 🛠️ Initializing...
        # 🏗️ Initializing Dropdown...
        self.user_id = user_id  # 👤 Storing user ID...
        options = [  # 📋 Defining menu options...
            discord.SelectOption(  # 👥 Staff option...
                label="Staff Management",  # 📝 Label...
                value="staff_management",  # 🏷️ Value...
                description="Inactivity Notices, and managing staff members",  # 📜 Description...
            ),
            discord.SelectOption(  # 🔔 Anti-ping option...
                label="Anti-ping",  # 📝 Label...
                value="antiping",  # 🏷️ Value...
                description="Responding to certain pings, ping immunity",  # 📜 Description...
            ),
            discord.SelectOption(  # ⚖️ Punishments option...
                label="Punishments",  # 📝 Label...
                value="punishments",  # 🏷️ Value...
                description="Punishing community members for rule infractions",  # 📜 Description...
            ),
            discord.SelectOption(  # 🔄 Sync option...
                label="Moderation Sync",  # 📝 Label...
                value="moderation_sync",  # 🏷️ Value...
                description="Syncing moderation actions from Roblox to Discord",  # 📜 Description...
            ),
            discord.SelectOption(  # 🕒 Shifts option...
                label="Shift Management",  # 📝 Label...
                value="shift_management",  # 🏷️ Value...
                description="Shifts (duty on, duty off), and where logs should go",  # 📜 Description...
            ),
            discord.SelectOption(  # ⚙️ Shift types...
                label="Shift Types",  # 📝 Label...
                value="shift_types",  # 🏷️ Value...
                description="View and customise shift types",  # 📜 Description...
            ),
            discord.SelectOption(  # 🔐 Verification...
                label="Verification",  # 📝 Label...
                value="verification",  # 🏷️ Value...
                description="Roblox Verification, simplified!",  # 📜 Description...
            ),
            discord.SelectOption(  # 🎮 Game logging...
                label="Game Logging",  # 📝 Label...
                value="game_logging",  # 🏷️ Value...
                description="Game Logging! Messages, STS, Events, and more!",  # 📜 Description...
            ),
            discord.SelectOption(  # 🎨 Customisation...
                label="Customisation",  # 📝 Label...
                value="customisation",  # 🏷️ Value...
                description="Colours, branding, prefix, to customise to your liking",  # 📜 Description...
            ),
            discord.SelectOption(  # 🛡️ Security...
                label="Game Security",  # 📝 Label...
                value="security",  # 🏷️ Value...
                description="Anti-abuse detection, and security measures",  # 📜 Description...
            ),
            discord.SelectOption(  # 🕵️ Privacy...
                label="Privacy",  # 📝 Label...
                value="privacy",  # 🏷️ Value...
                description="Disable global warnings, privacy features",  # 📜 Description...
            ),
        ]

        # 🔘 Configuring select menu...
        super().__init__(  # 🏗️ Calling parent init...
            placeholder="Select a category", min_values=1, max_values=1, options=options  # ⚙️ Menu settings...
        )

    async def callback(self, interaction: discord.Interaction):  # 🕹️ Callback handler...
        # 🔄 Handling dropdown selection...
        if interaction.user.id == self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer()  # 🔄 Deferring...
            self.view.value = self.values[0]  # 💾 Storing selection...
            self.view.stop()  # 🛑 Stopping view...
        else:
            # ⚠️ Handling unauthorized interaction...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            return await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...


class ShiftModificationDropdown(discord.ui.Select):  # 🕒 Shift modification dropdown...
    def __init__(self, user_id, other=False):  # 🛠️ Initializing...
        # 🕒 Initializing Shift Modification Dropdown...
        self.user_id = user_id  # 👤 Storing user ID...
        if other is False:  # 🔘 Standard options...
            options = [  # 📋 Standard options list...
                discord.SelectOption(  # 🟢 On duty...
                    label="On Duty",  # 📝 Label...
                    value="on",  # 🏷️ Value...
                    description="Start your in-game shift",  # 📜 Description...
                ),
                discord.SelectOption(  # ☕ Break...
                    label="Toggle Break",  # 📝 Label...
                    value="break",  # 🏷️ Value...
                    description="Taking a break? Toggle your break status",  # 📜 Description...
                ),
                discord.SelectOption(  # 🔴 Off duty...
                    label="Off Duty",  # 📝 Label...
                    value="off",  # 🏷️ Value...
                    description="End your in-game shift",  # 📜 Description...
                ),
                discord.SelectOption(  # 🗑️ Void...
                    label="Void shift",  # 📝 Label...
                    value="void",  # 🏷️ Value...
                    description="Void your in-game shift. This is irreversible.",  # 📜 Description...
                ),
            ]
        else:  # 🛠️ Administrative options...
            options = [  # 📋 Admin options list...
                discord.SelectOption(  # 🟢 On duty...
                    label="On Duty",  # 📝 Label...
                    value="on",  # 🏷️ Value...
                    description="Start their in-game shift",  # 📜 Description...
                ),
                discord.SelectOption(  # ☕ Break...
                    label="Toggle Break",  # 📝 Label...
                    value="break",  # 🏷️ Value...
                    description="Taking a break? Toggle their break status",  # 📜 Description...
                ),
                discord.SelectOption(  # 🔴 Off duty...
                    label="Off Duty",  # 📝 Label...
                    value="off",  # 🏷️ Value...
                    description="End their in-game shift",  # 📜 Description...
                ),
            ]

        # 🔘 Configuring select menu...
        super().__init__(  # 🏗️ Parent init...
            placeholder="Select an option", min_values=1, max_values=1, options=options  # ⚙️ Settings...
        )

    async def callback(self, interaction: discord.Interaction):  # 🕹️ Interaction handler...
        # 🔄 Handling shift status change...
        if interaction.user.id == self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer()  # 🔄 Deferring...
            self.view.value = self.values[0]  # 💾 Setting value...
            self.disabled = True  # 🔒 Disabling dropdown...
            for option in self.options:  # 🔍 Finding selected option...
                if option.value == self.values[0]:  # ✅ Matching value...
                    option.default = True  # 📌 Marking default...

            # 📄 Updating message view...
            await interaction.message.edit(view=self.view)  # 🔄 Editing message...
            self.view.stop()  # 🛑 Stopping view...
        else:
            # ⚠️ Handling unauthorized interaction...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            return await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...


class AdministrativeActionsDropdown(discord.ui.Select):  # 🛠️ Admin actions dropdown...
    def __init__(self, user_id):  # 🛠️ Initializing...
        # 🛠️ Initializing Administrative Actions Dropdown...
        self.user_id = user_id  # 👤 Storing user ID...
        options = [  # 📋 Admin action options...
            discord.SelectOption(  # ➕ Add time...
                label="Add time",  # 📝 Label...
                value="add",  # 🏷️ Value...
                description="Add time to their current shift",  # 📜 Description...
            ),
            discord.SelectOption(  # ➖ Remove time...
                label="Remove time",  # 📝 Label...
                value="remove",  # 🏷️ Value...
                description="Remove time from their current shift",  # 📜 Description...
            ),
            discord.SelectOption(  # 🗑️ Void shift...
                label="Void shift",  # 📝 Label...
                value="void",  # 🏷️ Value...
                description="Void their shift, and remove it from the leaderboard",  # 📜 Description...
            ),
            discord.SelectOption(  # 🧹 Clear shifts...
                label="Clear Member Shifts",  # 📝 Label...
                value="clear",  # 🏷️ Value...
                description="Clear all of their shifts from the leaderboard",  # 📜 Description...
            ),
        ]

        # 🔘 Configuring select menu...
        super().__init__(  # 🏗️ Parent init...
            placeholder="Administrative Actions",  # 🏷️ Placeholder...
            min_values=1,  # 📉 Min values...
            max_values=1,  # 📈 Max values...
            options=options,  # 📋 Applying options...
        )

    async def callback(self, interaction: discord.Interaction):  # 🕹️ Interaction handler...
        # 🔄 Handling administrative action...
        if interaction.user.id == self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer()  # 🔄 Deferring...
            self.view.admin_value = self.values[0]  # 💾 Setting admin value...
            self.disabled = True  # 🔒 Disabling dropdown...
            for option in self.options:  # 🔍 Finding selected option...
                if option.value == self.values[0]:  # ✅ Matching value...
                    option.default = True  # 📌 Marking default...

            # 🛠️ Disabling other selection menus...
            for item in self.view.children:  # 🔄 Iterating children...
                if isinstance(item, discord.ui.Select):  # 🔘 Checking if select...
                    if item is not self:  # 🚫 Not this item...
                        item.disabled = True  # 🔒 Disabling other...

            await interaction.message.edit(view=self.view)  # 🔄 Updating view...
            self.view.stop()  # 🛑 Stopping view...
        else:
            # ⚠️ Handling unauthorized interaction...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            return await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...


class CustomDropdown(discord.ui.Select):  # 🎨 Custom dropdown class...
    def __init__(self, user_id, options: list, limit=1):  # 🛠️ Initializing...
        # 🎨 Initializing Custom Dropdown...
        self.user_id = user_id  # 👤 Storing user ID...
        optionList = []  # 📋 Option holder...

        # 🧩 Processing option list...
        for option in options:  # 🔄 Iterating options...
            if isinstance(option, str):  # 🔠 Checking if string...
                optionList.append(  # ➕ Adding option...
                    discord.SelectOption(  # 🔘 Creating option...
                        label=option.replace("_", " ").title(), value=option  # 📝 Setting labels...
                    )
                )
            elif isinstance(option, discord.SelectOption):  # 🔘 Checking if SelectOption...
                optionList.append(option)  # ➕ Adding directly...

        super().__init__(  # 🏗️ Parent init...
            placeholder="Select an option",  # 🏷️ Placeholder...
            min_values=1,  # 📉 Min values...
            max_values=limit,  # 📈 Max values...
            options=optionList,  # 📋 Applying options...
        )

    async def callback(self, interaction: discord.Interaction):  # 🕹️ Interaction handler...
        # 🔄 Handling custom selection...
        if interaction.user.id == self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer()  # 🔄 Deferring...
            if len(self.values) == 1:  # 🔢 Checking count...
                self.view.value = self.values[0]  # 💾 Single value...
            else:  # 🔢 Multiple items...
                self.view.value = self.values  # 💾 List of values...
            self.view.stop()  # 🛑 Stopping view...
        else:
            # ⚠️ Handling unauthorized interaction...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            return await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...


class MultiPaginatorDropdown(discord.ui.Select):  # 📖 Multi-paginator dropdown...
    def __init__(self, user_id, options: list, pages: dict, limit=1):  # 🛠️ Initializing...
        # 📖 Initializing Multi-Paginator Dropdown...
        self.user_id = user_id  # 👤 Storing user ID...
        self.pages = pages  # 📄 Holding pages mapping...
        optionList = []  # 📋 Options list...

        # 🧩 Processing options...
        for option in options:  # 🔄 Iterating options...
            if isinstance(option, str):  # 🔠 Checking if string...
                optionList.append(  # ➕ Adding option...
                    discord.SelectOption(  # 🔘 Creating SelectOption...
                        label=option.replace("_", " ").title(), value=option  # 📝 Formatting labels...
                    )
                )
            elif isinstance(option, discord.SelectOption):  # 🔘 Checking if SelectOption...
                optionList.append(option)  # ➕ Adding directly...

        super().__init__(  # 🏗️ Parent init...
            placeholder="Select an option",  # 🏷️ Placeholder...
            min_values=1,  # 📉 Min values...
            max_values=limit,  # 📈 Max values...
            options=optionList,  # 📋 Applying options...
        )

    async def callback(self, interaction: discord.Interaction):  # 🕹️ Interaction handler...
        # 🔄 Changing page on selection...
        if interaction.user.id == self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer()  # 🔄 Deferring...
            await interaction.message.edit(  # 📝 Editing message...
                content=f"<:ERMCheck:1111089850720976906>  **{interaction.user.name},** you're currently viewing the **{self.values[0].replace('_', ' ').title()}** commands!",  # 📢 Formatting content...
                embed=self.pages.get(self.values[0]),  # 🖼️ Setting embed...
            )
        else:
            # ⚠️ Handling unauthorized interaction...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...
            return


# noinspection PyUnresolvedReferences
class MultiDropdown(discord.ui.Select):  # 🧩 Multi-dropdown class...
    def __init__(self, user_id, options: list):  # 🛠️ Initializing...
        # 🧩 Initializing Multi-Dropdown...
        self.user_id = user_id  # 👤 Storing user ID...
        optionList = []  # 📋 Options list...

        for option in options:  # 🔄 Iterating options...
            if isinstance(option, str):  # 🔠 Checking if string...
                optionList.append(  # ➕ Adding option...
                    discord.SelectOption(  # 🔘 Creating SelectOption...
                        label=option.replace("_", " ").title(), value=option  # 📝 Formatting labels...
                    )
                )
            elif isinstance(option, discord.SelectOption):  # 🔘 Checking if SelectOption...
                optionList.append(option)  # ➕ Adding directly...

        super().__init__(  # 🏗️ Parent init...
            placeholder="Select an option",  # 🏷️ Placeholder...
            max_values=len(optionList),  # 📈 Max values based on count...
            options=optionList,  # 📋 Applying options...
        )

    async def callback(self, interaction: discord.Interaction):  # 🕹️ Interaction handler...
        # 🔄 Handling multiple selections...
        if interaction.user.id == self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer()  # 🔄 Deferring...
            if len(self.values) == 1:  # 🔢 Checking count...
                self.view.value = self.values[0]  # 💾 Storing single value...
            else:  # 🔢 Multiple items...
                self.view.value = self.values  # 💾 Storing list of values...
            self.view.stop()  # 🛑 Stopping view...
        else:
            # ⚠️ Handling unauthorized interaction...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...
            return


class SettingsSelectMenu(discord.ui.View):  # ⚙️ Settings view...
    def __init__(self, user_id):  # 🛠️ Initializing...
        # ⚙️ Initializing Settings Select Menu...
        super().__init__(timeout=600.0)  # ⏰ Setting timeout...
        self.value = None  # 💾 Initializing value...
        self.user_id = user_id  # 👤 Storing user ID...

        self.add_item(Dropdown(self.user_id))  # ➕ Adding dropdown item...


class ModificationSelectMenu(discord.ui.View):  # 🕒 Modification view...
    def __init__(self, user_id):  # 🛠️ Initializing...
        # 🕒 Initializing Modification Select Menu...
        super().__init__(timeout=600.00)  # ⏰ Setting timeout...
        self.value = None  # 💾 Initializing value...
        self.user_id = user_id  # 👤 Storing user ID...

        self.add_item(ShiftModificationDropdown(self.user_id))  # ➕ Adding dropdown item...


class AdministrativeSelectMenu(discord.ui.View):  # 🛠️ Admin view...
    def __init__(self, user_id):  # 🛠️ Initializing...
        # 🛠️ Initializing Administrative Select Menu...
        super().__init__(timeout=600.00)  # ⏰ Setting timeout...
        self.value = None  # 💾 Initializing value...
        self.admin_value = None  # 💾 Initializing admin value...
        self.user_id = user_id  # 👤 Storing user ID...

        # ➕ Adding dropdowns...
        self.add_item(ShiftModificationDropdown(self.user_id, other=True))  # ➕ Adding status dropdown...
        self.add_item(AdministrativeActionsDropdown(self.user_id))  # ➕ Adding action dropdown...


class YesNoMenu(discord.ui.View):  # ❓ Yes/No view...
    def __init__(self, user_id):  # 🛠️ Initializing...
        # ❓ Initializing Yes/No Menu...
        super().__init__(timeout=600.0)  # ⏰ Setting timeout...
        self.value = None  # 💾 Initializing value...
        self.user_id = user_id  # 👤 Storing user ID...

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)  # ✅ 'Yes' button...
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):  # 🔘 Button callback...
        # ✅ Handling affirmative response...
        if interaction.user.id != self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer(ephemeral=True, thinking=True)  # ⏳ Deferring...
            await generalised_interaction_check_failure(interaction.followup)  # ⚠️ Failure...
            return
        await interaction.response.defer()  # 🔄 Deferring interaction...
        # 🔒 Disabling inputs...
        for item in self.children:  # 🔄 Iterating children...
            item.disabled = True  # 🔒 Disabling each...
        self.value = True  # 💾 Setting value to True...
        await interaction.edit_original_response(view=self)  # 🔄 Editing response...
        self.stop()  # 🛑 Stopping view...

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)  # ❌ 'No' button...
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):  # 🔘 Button callback...
        # ❌ Handling negative response...
        if interaction.user.id != self.user_id:  # 🔐 Authorization check...
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        # 🔒 Disabling inputs...
        for item in self.children:
            item.disabled = True
        self.value = False
        await interaction.edit_original_response(view=self)
        self.stop()


class AcknowledgeMenu(discord.ui.View):
    def __init__(self, user_id, note: str):
        # 📢 Initializing Acknowledge Menu...
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        if note:
            # ✍️ Setting note label...
            for child in self.children:
                if child.label == "NOTE":
                    child.label = note

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(
        label="I acknowledge and understand", style=discord.ButtonStyle.green
    )
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = True
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(
        label="NOTE", style=discord.ButtonStyle.secondary, row=1, disabled=True
    )
    async def note(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass


class YesNoExpandedMenu(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes, continue", style=discord.ButtonStyle.primary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = True
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(
        label="I'll do this another time", style=discord.ButtonStyle.secondary
    )
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = False
        await interaction.edit_original_response(view=self)
        self.stop()


class YesNoColourMenu(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.primary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = True
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="No", style=discord.ButtonStyle.secondary)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return

        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = False
        await interaction.edit_original_response(view=self)
        self.stop()


class ColouredButton(discord.ui.Button):
    def __init__(self, user_id, label, style, emoji=None):
        super().__init__(label=label, style=style, emoji=emoji)
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            await interaction.response.defer()
            self.view.value = self.label
            self.view.stop()
        else:
            await generalised_interaction_check_failure(interaction.response)
            return


class CustomExecutionButton(discord.ui.Button):
    def __init__(self, user_id, label, style, emoji=None, func=None, row=0, disabled=False):
        """

        A button used for custom execution functions. This is often used to subvert pagination limitations.

        :param user_id: the user who can use this button
        :param label: the label of the button
        :param style: style of the button : discord.ButtonStyle
        :param emoji: emoji of the button
        :param func: function to be executed when pressed
        """

        super().__init__(label=label, style=style, emoji=emoji, row=row, disabled=disabled)
        self.func = func
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            await self.func(interaction, self)
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )


class ColouredMenu(discord.ui.View):
    def __init__(self, user_id, buttons: list[str]):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        for index, button in enumerate(buttons):
            if index == 0:
                self.add_item(
                    ColouredButton(
                        self.user_id, button, discord.ButtonStyle.primary, emoji=None
                    )
                )
            else:
                self.add_item(
                    ColouredButton(
                        self.user_id, button, discord.ButtonStyle.secondary, emoji=None
                    )
                )


class EnableDisableMenu(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Enable", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = True
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Disable", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = False
        await interaction.edit_original_response(view=self)
        self.stop()


class LinkPathwayMenu(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="ERM", style=discord.ButtonStyle.secondary)
    async def ERM(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "erm"
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Bloxlink", style=discord.ButtonStyle.danger)
    async def Bloxlink(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "bloxlink"
        await interaction.edit_original_response(view=self)
        self.stop()


class ShiftModify(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Add time (+)", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "add"
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Remove time (-)", style=discord.ButtonStyle.danger)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "remove"
        await interaction.edit_original_response(view=self)
        self.stop()

    @discord.ui.button(label="End shift", style=discord.ButtonStyle.danger)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "end"
        await interaction.edit_original_response(view=self)
        self.stop()

    @discord.ui.button(label="Void shift", style=discord.ButtonStyle.danger)
    async def void(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "void"
        await interaction.edit_original_response(view=self)
        self.stop()


class ActivityNoticeModification(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Add time (+)", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "add"
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Remove time (-)", style=discord.ButtonStyle.danger)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "remove"
        await interaction.edit_original_response(view=self)
        self.stop()

    @discord.ui.button(label="End Activity Notice", style=discord.ButtonStyle.danger)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "end"
        await interaction.edit_original_response(view=self)
        self.stop()

    @discord.ui.button(label="Void Activity Notice", style=discord.ButtonStyle.danger)
    async def void(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "void"
        await interaction.edit_original_response(view=self)
        self.stop()


class PartialShiftModify(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Add time (+)", style=discord.ButtonStyle.green)
    async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "add"
        await interaction.edit_original_response(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Remove time (-)", style=discord.ButtonStyle.danger)
    async def remove(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            await generalised_interaction_check_failure(interaction.followup)
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = "remove"
        await interaction.edit_original_response(view=self)
        self.stop()


class LOAMenu(discord.ui.View):
    def __init__(self, bot, roles, loa_roles, loa_object, user_id, code):

        super().__init__(timeout=None)
        self.value = None
        self.bot = bot
        self.loa_object = loa_object
        if isinstance(roles, list):
            self.roles = roles
        elif isinstance(roles, int):
            self.roles = [roles]
        self.loa_role = loa_roles
        self.user_id = user_id
        self.id = code

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(
        label="Accept", style=discord.ButtonStyle.green, custom_id="loamenu:accept"
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        # await interaction.response.defer()
        await interaction.response.defer(ephemeral=True, thinking=True)

        # checking for admin permission as opposed to roles - property kept for legacy
        if not await admin_check(self.bot, interaction.guild, interaction.user):
            await generalised_interaction_check_failure(interaction.followup)
            return

        for item in self.children:
            item.disabled = True
            if item.label == "Accept":
                item.label = "Accepted"
            else:
                self.remove_item(item)
        s_loa = None

        for loa in await self.bot.loas.get_all():
            if (
                loa["message_id"] == interaction.message.id
                and loa["guild_id"] == interaction.guild.id
            ):
                s_loa = loa

        s_loa["accepted"] = True
        guild = self.bot.get_guild(s_loa["guild_id"])
        try:
            user = await guild.fetch_member(s_loa["user_id"])
        except discord.NotFound:
            user = None
        if user is None:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Could not find member",
                    description="I could not find the staff member which requested this Leave of Absence.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        settings = await self.bot.settings.find_by_id(interaction.guild.id)
        mentionable = ""
        try:
            await user.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Activity Notice Accepted",
                    description=f"Your {s_loa['type']} request in **{interaction.guild.name}** was accepted!",
                    color=GREEN_COLOR,
                )
            )
        except:
            pass

        try:
            await self.bot.loas.update_by_id(s_loa)
            if isinstance(self.loa_role, int):
                role = [discord.utils.get(guild.roles, id=self.loa_role)]
            elif isinstance(self.loa_role, list):
                role = [
                    discord.utils.get(guild.roles, id=role) for role in self.loa_role
                ]

            for rl in role:
                if rl not in user.roles:
                    await user.add_roles(rl)

            self.value = True
        except discord.HTTPException:
            pass
        embed = interaction.message.embeds[0]
        embed.title = (
            f"{self.bot.emoji_controller.get_emoji('success')} {s_loa['type']} Accepted"
        )
        embed.colour = GREEN_COLOR
        embed.set_footer(text=f"Accepted by {interaction.user.name}")

        await interaction.message.edit(
            embed=embed,
            view=None,
        )

        await self.bot.views.delete_by_id(self.id)
        await interaction.followup.send(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Request Accepted",
                description=f"You have successfully accepted this staff member's {s_loa['type']} Request.",
                color=GREEN_COLOR,
            )
        )
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(
        label="Deny",
        style=discord.ButtonStyle.danger,
        custom_id="loamenu:deny",
    )
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        # checking for admin permission as opposed to roles - property kept for legacy
        if not await admin_check(self.bot, interaction.guild, interaction.user):
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)
        
        for item in self.children:
            item.disabled = True

        modal = CustomModal(
            f"Reason for Denial",
            [
                (
                    "value",
                    (
                        discord.ui.TextInput(
                            label="Reason for denial",
                            placeholder="Enter a reason for denying this person's request.",
                            required=True,
                        )
                    ),
                )
            ],
        )
        await interaction.response.send_modal(modal)

        timeout = await modal.wait()
        if timeout:
            return

        reason = modal.value.value

        for item in self.children:
            item.disabled = True
            if item.label == button.label:
                item.label = "Denied"
            else:
                self.remove_item(item)
        s_loa = None

        async for loa_item in self.bot.loas.db.find(
            {"guild_id": interaction.guild.id, "message_id": interaction.message.id}
        ):
            s_loa = loa_item

        if not s_loa:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Could not find LOA",
                    description="I could not find the activity notice associated with this menu.",
                ),
                ephemeral=True,
            )

        s_loa["denied"] = True
        s_loa["denial_reason"] = reason

        user = interaction.guild.get_member(s_loa["user_id"])
        if not user:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Could not find member",
                    description="I could not find the staff member who made this request.",
                ),
                ephemeral=True,
            )

        try:
            await user.send(
                embed=discord.Embed(
                    title="Activity Notice Denied",
                    description=f"Your {s_loa['type']} request in **{interaction.guild.name}** was denied.\n**Reason:** {reason}",
                    color=BLANK_COLOR,
                )
            )
        except:
            pass
        await self.bot.loas.update_by_id(s_loa)

        embed = interaction.message.embeds[0]
        embed.title = f"{s_loa['type']} Denied"
        embed.colour = BLANK_COLOR
        embed.set_footer(text=f"Denied by {interaction.user.name}")

        await interaction.message.edit(embed=embed, view=None)
        self.value = False
        await self.bot.views.delete_by_id(self.id)

        self.stop()


class AddReminder(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    @discord.ui.button(label="Create a reminder", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.response.defer()
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(view=self)
            self.value = "create"
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class ManageReminders(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        self.modal: typing.Union[None, CustomModal] = None

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.modal = CustomModal(
                f"Create a reminder",
                [
                    (
                        "name",
                        discord.ui.TextInput(
                            label="Name",
                            placeholder="Name of your reminder",
                            required=True,
                        ),
                    ),
                    (
                        "content",
                        discord.ui.TextInput(
                            label="Content",
                            style=discord.TextStyle.long,
                            placeholder="Content of your reminder",
                            required=True,
                        ),
                    ),
                    (
                        "time",
                        discord.ui.TextInput(
                            label="Interval",
                            placeholder="What would you like you like the interval to be? (e.g. 5m)",
                            required=True,
                            style=discord.TextStyle.short,
                        ),
                    ),
                ],
            )
            await interaction.response.send_modal(self.modal)
            await self.modal.wait()
            self.value = "create"
            self.stop()
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.primary)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.modal = CustomModal(
                f"Edit a reminder",
                [
                    (
                        "identifier",
                        discord.ui.TextInput(
                            label="ID",
                            placeholder="ID of your reminder",
                            required=True,
                        ),
                    ),
                ],
            )
            await interaction.response.send_modal(self.modal)
            await self.modal.wait()
            self.value = "edit"
            self.stop()
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )

    @discord.ui.button(label="Pause", style=discord.ButtonStyle.secondary)
    async def pause(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.modal = CustomModal(
                f"Pause a reminder",
                [
                    (
                        "id_value",
                        discord.ui.TextInput(
                            label="ID",
                            placeholder="ID of your reminder",
                            required=True,
                        ),
                    ),
                ],
            )
            await interaction.response.send_modal(self.modal)
            await self.modal.wait()
            self.value = "pause"
            self.stop()
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.modal = CustomModal(
                f"Delete a reminder",
                [
                    (
                        "id_value",
                        discord.ui.TextInput(
                            label="ID",
                            placeholder="ID of your reminder",
                            required=True,
                        ),
                    ),
                ],
            )
            await interaction.response.send_modal(self.modal)
            await self.modal.wait()
            self.value = "delete"
            self.stop()
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )


# Update ManageActions to add Discord Commands
class ManageActions(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.bot = bot
        self.user_id = user_id
        self.modal: typing.Union[None, CustomModal] = None
        self.toolkit: typing.Optional[ActionCreationToolkit] = None

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def create(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.modal = CustomModal(
                f"Create an Action",
                [
                    (
                        "name",
                        discord.ui.TextInput(
                            label="Name",
                            placeholder="Action Name",
                            required=True,
                        ),
                    )
                ],
            )
            await interaction.response.send_modal(self.modal)
            await self.modal.wait()
            self.value = "create"
            self.toolkit = ActionCreationToolkit(
                self.bot, self.modal.name.value, self.user_id
            )
            embed = discord.Embed(
                title="Create an Action",
                description="Using this panel, you can assign integrations to occur when you execute your action. These can affect your ER:LC servers, execute custom commands, and more. These actions will only run when you run `/actions execute` with your action.\n\n**On Execution:**\n > No Integrations",
                color=BLANK_COLOR,
            )
            await interaction.message.edit(embed=embed, view=self.toolkit)
            timeout = await self.toolkit.wait()
            if timeout:
                return
            await interaction.message.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Successfully Added",
                    description="I have successfully added this action.",
                    color=GREEN_COLOR,
                ),
                view=None,
            )
            self.toolkit.action_data["_id"] = ObjectId()
            await self.bot.actions.insert(self.toolkit.action_data)
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.secondary)
    async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.modal = CustomModal(
                f"Edit an Action",
                [
                    (
                        "name",
                        discord.ui.TextInput(
                            label="ID",
                            placeholder="Action ID",
                            required=True,
                        ),
                    )
                ],
            )
            await interaction.response.send_modal(self.modal)
            await self.modal.wait()
            actions = [
                i
                async for i in self.bot.actions.db.find({"Guild": interaction.guild.id})
            ]
            selected_action = None
            for item in actions:
                if item["ActionID"] == int(self.modal.name.value):
                    selected_action = item
                    break
            else:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Not Found",
                        description="I could not find an action with that ID.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )

            self.toolkit = ActionCreationToolkit(
                self.bot, self.modal.name.value, self.user_id
            )
            self.toolkit.action_data = selected_action
            embed = discord.Embed(
                title="Edit an Action",
                description="Using this panel, you can assign integrations to occur when you execute your action. These can affect your ER:LC servers, execute custom commands, and more. These actions will only run when you run `/actions execute` with your action.\n\n**On Execution:**\n ",
                color=BLANK_COLOR,
            )
            embed.description += "\n".join(
                [
                    f'> **{i["IntegrationName"]}{":** {}".format(i["ExtraInformation"]) if i["ExtraInformation"] is not None else "**"}'
                    for i in selected_action["Integrations"]
                ]
            )
            embed.description += "\n> *New Integration*"
            if len(selected_action.get("Conditions", []) or []) != 0:
                embed.add_field(
                    name="Conditions",
                    value="\n".join(
                        [
                            f"> **{('`{}`'.format(item.get('LogicGate', '')) + ' ') if item.get('LogicGate') else ''}{item['Variable']}** `{item['Operation']}` {item['Value']}"
                            for item in selected_action["Conditions"]
                        ]
                    ),
                    inline=False,
                )
                embed.add_field(
                    name="Execution Interval",
                    value=td_format(
                        datetime.timedelta(
                            seconds=selected_action.get(
                                "ConditionExecutionInterval", 300
                            )
                        )
                    ),
                    inline=False,
                )
            await interaction.message.edit(embed=embed, view=self.toolkit)
            timeout = await self.toolkit.wait()
            if timeout:
                return
            await interaction.message.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Successfully Edited",
                    description="I have successfully edited this action.",
                    color=GREEN_COLOR,
                ),
                view=None,
            )

            await self.bot.actions.update_by_id(self.toolkit.action_data)
        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.red)
    async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.modal = CustomModal(
                f"Delete an Action",
                [
                    (
                        "id_value",
                        discord.ui.TextInput(
                            label="ID",
                            placeholder="Action ID",
                            required=True,
                        ),
                    ),
                ],
            )
            await interaction.response.send_modal(self.modal)
            await self.modal.wait()
            await self.bot.actions.db.delete_one(
                {"ActionID": int(self.modal.id_value.value)}
            )
            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Deleted Action",
                    description="Action has been deleted successfully.",
                    color=GREEN_COLOR,
                )
            )

        else:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )


class CustomisePunishmentType(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        self.modal: typing.Union[CreatePunishmentType, DeletePunishmentType, None] = (
            None
        )

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            modal = CreatePunishmentType()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(view=self)
            self.value = "create"
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            modal = DeletePunishmentType()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(view=self)
            self.value = "delete"
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class CustomCommandModification(discord.ui.View):
    def __init__(self, user_id: int, command_data: dict):
        super().__init__(timeout=600)
        self.user_id = user_id
        self.value = None
        self.command_data = command_data

        if self.command_data.get("channel") is not None:
            for select in list(
                filter(lambda x: isinstance(x, discord.ui.ChannelSelect), self.children)
            ):
                select.default_values = [
                    discord.Object(id=self.command_data.get("channel"))
                ]

    async def check_ability(self, message):
        if self.command_data.get("message", None) and self.command_data.get(
            "name", None
        ):
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = False

            await message.edit(view=self)
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = True
            await message.edit(view=self)

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )
            return False

    async def refresh_ui(self, message: discord.Message):
        embed = discord.Embed(
            title="Custom Commands",
            description=(
                "**Command Information**\n"
                f"> **Command ID:** `{self.command_data['id']}`\n"
                f"> **Command Name:** {self.command_data['name']}\n"
                f"> **Creator:** <@{self.command_data['author']}>\n"
                f"> **Default Channel:** {'<#{}>'.format(self.command_data.get('channel')) if self.command_data.get('channel') is not None else 'None selected'}\n"
                f"\n**Message:**\n"
                f"View the message below by clicking 'View Message'."
            ),
            color=BLANK_COLOR,
        )
        await message.edit(embed=embed)

    @discord.ui.button(label="View Variables", row=0)
    async def view_variables(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        return await interaction.response.send_message(
            embed=discord.Embed(
                description=(
                    "With **ERM Custom Commands**, you can use custom variables to adapt to the current circumstances when the command is ran.\n"
                    "`{user}` - Mention of the person using the command.\n"
                    "`{username}` - Name of the person using the command.\n"
                    "`{display_name}` - Display name of the person using the command.\n"
                    "`{time}` - Timestamp format of the time of the command execution.\n"
                    "`{server}` - Name of the server this is being ran in.\n"
                    "`{channel}` - Mention of the channel the command is being ran in.\n"
                    "`{prefix}` - The custom prefix of the bot.\n"
                    "`{onduty}` - Number of staff which are on duty within your server.\n"
                    "\n**PRC Specific Variables**\n"
                    "`{join_code}` - Join Code of the ER:LC server\n"
                    "`{players}` - Current players in the ER:LC server\n"
                    "`{max_players}` - Maximum players of the ER:LC server\n"
                    "`{queue}` - Number of players in the queue\n"
                    "`{staff}` - Number of staff members in-game\n"
                    "`{mods}` - Number of mods in-game\n"
                    "`{admins}` - Number of admins in-game\n"
                ),
                color=BLANK_COLOR,
            ),
            ephemeral=True,
        )

    @discord.ui.button(label="Edit Name", row=0)
    async def edit_custom_command_name(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        modal = CustomModal(
            "Edit Custom Command Name",
            [
                (
                    "name",
                    discord.ui.TextInput(label="Custom Command Name", max_length=50),
                )
            ],
        )

        await interaction.response.send_modal(modal)
        await modal.wait()
        try:
            chosen_identifier = modal.name.value
        except ValueError:
            return

        if not chosen_identifier:
            return

        self.command_data["name"] = chosen_identifier
        await self.check_ability(interaction.message)
        await self.refresh_ui(interaction.message)

    @discord.ui.button(label="View Message", row=0)
    async def view_custom_command_message(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True)

        async def _return_failure():
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="No Message Found",
                    description="There is currently no message associated with this Custom Command.\nYou can add one using 'Edit Message'.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        view = discord.ui.View()
        for item in self.command_data.get("buttons") or []:
            view.add_item(
                discord.ui.Button(
                    label=item["label"],
                    url=item["url"],
                    row=item["row"],
                    style=discord.ButtonStyle.url,
                )
            )

        if not self.command_data.get("message", None):
            return await _return_failure()

        if (
            not self.command_data.get("message", {}).get("content", None)
            and not len(self.command_data.get("message", {}).get("embeds", [])) > 0
        ):
            return await _return_failure()

        converted = []
        for item in self.command_data.get("message").get("embeds", []):
            converted.append(discord.Embed.from_dict(item))

        await interaction.followup.send(
            embeds=converted,
            content=self.command_data["message"].get("content", None),
            ephemeral=True,
            view=view,
        )

    @discord.ui.button(label="Edit Message", row=0)
    async def edit_message(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = MessageCustomisation(
            interaction.user.id,
            self.command_data.get("message", None),
            external=False,
            persist=False,
        )
        view.sustained_interaction = interaction

        if not self.command_data.get("message", None):
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            converted = []
            for item in self.command_data.get("message", {}).get("embeds", []):
                converted.append(discord.Embed.from_dict(item))

            await interaction.response.send_message(
                content=self.command_data.get("message", {}).get("content", None),
                embeds=converted,
                view=view,
                ephemeral=True,
            )

        await view.wait()
        if view.newView:
            await view.newView.wait()
            chosen_message = view.newView.msg
        else:
            chosen_message = view.msg

        new_content = chosen_message.content
        new_embeds = []
        for item in chosen_message.embeds or []:
            new_embeds.append(item.to_dict())

        self.command_data["message"] = {"content": new_content, "embeds": new_embeds}
        await self.check_ability(interaction.message)
        await self.refresh_ui(interaction.message)
        await (await interaction.original_response()).delete()

    @discord.ui.button(label="Edit Buttons", row=0)
    async def edit_buttons(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        view = ButtonCustomisation(self.command_data, interaction.user.id)
        view.sustained_interaction = interaction

        if not self.command_data.get("message", None):
            await interaction.response.send_message(view=view, ephemeral=True)
        else:
            converted = []
            for item in self.command_data.get("message", {}).get("embeds", []):
                converted.append(discord.Embed.from_dict(item))

            await interaction.response.send_message(
                content=self.command_data.get("message", {}).get("content", None),
                embeds=converted,
                view=view,
                ephemeral=True,
            )

        timeout = await view.wait()
        if timeout or not view.value:
            return

        self.command_data["buttons"] = view.command_data.get("buttons", [])
        await self.check_ability(interaction.message)
        await self.refresh_ui(interaction.message)
        await (await interaction.original_response()).delete()

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Default Channel",
        row=1,
        min_values=0,
        max_values=1,
        channel_types=[discord.ChannelType.text],
    )
    async def channel_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        self.command_data["channel"] = (
            select.values[0].id if len(select.values) > 0 else None
        )
        await interaction.response.defer(thinking=False)
        await self.check_ability(interaction.message)
        await self.refresh_ui(interaction.message)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=2)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        self.value = False
        pass

    @discord.ui.button(
        label="Finish", style=discord.ButtonStyle.green, row=2, disabled=True
    )
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        self.value = True
        self.stop()


class CounterButton(discord.ui.Button):
    def __init__(self, row):
        super().__init__(label="0", style=discord.ButtonStyle.primary, row=row)
        self.voters = set()

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        if user.id in self.voters:
            self.voters.remove(user.id)
            self.label = str(int(self.label) - 1)
            await interaction.response.send_message(
                f"Your vote has been removed.", ephemeral=True
            )
        else:
            self.voters.add(user.id)
            self.label = str(int(self.label) + 1)
            await interaction.response.send_message(
                f"Your vote has been added.", ephemeral=True
            )
        await interaction.message.edit(view=self.view)


class ViewVotersButton(discord.ui.Button):
    def __init__(self, row, counter_button):
        super().__init__(
            label="🔍View Voters", style=discord.ButtonStyle.secondary, row=row
        )
        self.counter_button = counter_button

    async def callback(self, interaction: discord.Interaction):
        voters = [
            interaction.guild.get_member(user_id).mention
            for user_id in self.counter_button.voters
        ]
        voter_list = "\n".join(voters) if voters else "No votes yet."
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Voters", description=voter_list, color=BLANK_COLOR
            ),
            ephemeral=True,
        )


class ButtonCustomisation(discord.ui.View):
    def __init__(self, command_data: dict, user_id: int):
        super().__init__(timeout=600)
        for item in command_data.get("buttons") or []:
            self.add_item(
                discord.ui.Button(
                    label=item["label"],
                    url=item["url"],
                    row=item["row"],
                    style=discord.ButtonStyle.url,
                )
            )

        self.command_data = command_data
        self.sustained_interaction = None
        self.value = None
        self.user_id = user_id

    @discord.ui.button(label="Add Button", row=4)
    async def add_button(self, interaction: discord.Interaction, _):
        if len(self.children) >= 25:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Limitation",
                    description="You can only have a maximum of 25 buttons per custom command.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        modal = CustomModal(
            "Add a Button",
            [
                (
                    "label",
                    discord.ui.TextInput(
                        label="Label",
                        max_length=80,
                        placeholder="Label of the button",
                        required=True,
                    ),
                ),
                (
                    "url",
                    discord.ui.TextInput(
                        label="URL",
                        max_length=500,
                        placeholder="URL of the button",
                        required=True,
                    ),
                ),
                (
                    "row",
                    discord.ui.TextInput(
                        label="Row", placeholder="Row of the button (e.g. 0, 1, 2, 3)"
                    ),
                ),
            ],
            {"ephemeral": True},
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Input validations
        if not all([i.isdigit() for i in modal.row.value.strip()]):
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Row",
                    description="The row you provided is not a valid number.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        if int(modal.row.value.strip()) > 4:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Row",
                    description="The row you provided must be within the range 0-4.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        if int(modal.row.value.strip()) < 0:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Row",
                    description="The row you provided must be within the range 0-4.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        if not modal.label.value.strip():
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Label",
                    description="The label you provided is not valid.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        if not modal.url.value.strip():
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid URL",
                    description="The URL you provided is not valid.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        if not any(
            [
                modal.url.value.strip().startswith(prefix)
                for prefix in ["https://", "http://"]
            ]
        ):
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid URL",
                    description="The URL you provided is not valid.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        message = interaction.message
        if self.sustained_interaction:
            message = await self.sustained_interaction.original_response()

        relevant_item = discord.ui.Button(
            label=modal.label.value.strip(),
            url=modal.url.value.strip(),
            row=int(modal.row.value.strip()),
            style=discord.ButtonStyle.url,
        )
        self.add_item(relevant_item)

        try:
            await message.edit(view=self)
        except discord.HTTPException:
            self.remove_item(relevant_item)
            return

        if self.command_data.get("buttons") is not None:
            self.command_data["buttons"].append(
                {
                    "label": modal.label.value.strip(),
                    "url": modal.url.value.strip(),
                    "row": int(modal.row.value.strip()),
                }
            )
        else:
            self.command_data["buttons"] = [
                {
                    "label": modal.label.value.strip(),
                    "url": modal.url.value.strip(),
                    "row": int(modal.row.value.strip()),
                }
            ]

    @discord.ui.button(label="Remove Button", row=4)
    async def remove_button(self, interaction: discord.Interaction, _):
        modal = CustomModal(
            "Remove a Button",
            [
                (
                    "label",
                    discord.ui.TextInput(
                        label="Label",
                        max_length=80,
                        placeholder="Label of the button",
                        required=True,
                    ),
                ),
            ],
            {"ephemeral": True},
        )
        await interaction.response.send_modal(modal)
        await modal.wait()
        # Input validations

        message = interaction.message
        if self.sustained_interaction:
            message = await self.sustained_interaction.original_response()

        for item in self.command_data.get("buttons") or []:
            if item["label"].lower() == modal.label.value.strip().lower():
                self.command_data["buttons"].remove(item)

        for button in self.children:
            if isinstance(button, discord.ui.Button):
                if button.label.lower() == modal.label.value.strip().lower():
                    if button.label not in [
                        "Add Button",
                        "Remove Button",
                        "Counter Button",
                        "Cancel",
                        "Finish",
                    ]:
                        self.remove_item(button)
                        break

        await message.edit(view=self)

    @discord.ui.button(label="Counter Button", row=4)
    async def add_counter(self, interaction: discord.Interaction, _):
        if len(self.children) >= 25:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Limitation",
                    description="You can only have a maximum of 25 buttons per custom command.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        modal = CustomModal(
            "Add a Button",
            [
                (
                    "row",
                    discord.ui.TextInput(
                        label="Row", placeholder="Row of the button (e.g. 0, 1, 2, 3)"
                    ),
                )
            ],
            {"ephemeral": True},
        )
        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.children[0].value.isdigit():
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Row",
                    description="The row you provided is not a valid number.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        row = int(modal.children[0].value.strip())

        if row > 4 or row < 0:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Row",
                    description="The row you provided must be within the range 0-4.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        counter_button = CounterButton(row=row)
        view_voters_button = ViewVotersButton(row=row, counter_button=counter_button)

        self.add_item(counter_button)
        self.add_item(view_voters_button)

        message = interaction.message
        if self.sustained_interaction:
            message = await self.sustained_interaction.original_response()

        try:
            await message.edit(view=self)
        except discord.HTTPException:
            self.remove_item(counter_button)
            self.remove_item(view_voters_button)
            return

        if self.command_data.get("buttons") is not None:
            self.command_data["buttons"].append({"label": "0", "row": row})
        else:
            self.command_data["buttons"] = [{"label": "0", "row": row}]

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=4)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        self.value = False
        pass

    @discord.ui.button(
        label="Finish", style=discord.ButtonStyle.green, row=4, disabled=False
    )
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        self.value = True
        self.stop()


class MessageCustomisation(discord.ui.View):
    def __init__(self, user_id, data=None, persist=False, external=False):
        super().__init__(timeout=600.0)
        if data is None:
            data = {}
        self.persist = persist
        self.value: typing.Union[str, None] = None
        self.modal: typing.Union[discord.ui.Modal, None] = None
        self.newView: typing.Union[EmbedCustomisation, None] = None
        self.msg = None
        self.has_embeds = False
        self.sustained_interaction = None
        self.external = external
        if data != {}:
            msg = data.get("message", data)
            content = msg["content"]
            embeds = msg.get("embeds")
            if embeds != []:
                self.has_embeds = True
        self.user_id = user_id

    async def check_ability(self, message):
        if message.content or message.embeds is not None:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = False

            await message.edit(view=self)
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = True
            await message.edit(view=self)

    @discord.ui.button(
        label="Set Message",
        style=discord.ButtonStyle.secondary,
    )
    async def content(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = SetContent()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            if self.sustained_interaction:
                await self.check_ability(
                    await self.sustained_interaction.original_response()
                )
                return await (
                    await self.sustained_interaction.original_response()
                ).edit(content=modal.name.value)
            await interaction.message.edit(content=modal.name.value)
            await self.check_ability(interaction.message)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Add Embed",
        style=discord.ButtonStyle.secondary,
    )
    async def addembed(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            if len(interaction.message.embeds) > 0:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Limitation",
                        description="You can only have one embed per custom command message.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )

            newView = EmbedCustomisation(interaction.user.id, self)
            newView.sustained_interaction = self.sustained_interaction
            self.newView = newView

            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message

            await chosen_interaction_message.edit(
                view=newView,
                embed=discord.Embed(colour=BLANK_COLOR, description="\u200b"),
            )
            await interaction.response.defer(thinking=False)
            # await self.check_ability(chosen_interaction_message)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.success, disabled=True)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            self.msg = interaction.message
            self.newView = self
            self.value = "finish"
            if not self.external:
                await interaction.response.defer(thinking=False)
            else:
                await int_invis_embed(
                    interaction,
                    "your custom message has been saved. You can now continue with your configuration.",
                )
            if not self.persist and not self.sustained_interaction:
                await interaction.message.delete()
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class EmbedCustomisation(discord.ui.View):
    def __init__(self, user_id, view=None, external=False):
        super().__init__(timeout=600.0)
        self.value: typing.Union[str, None] = None
        self.modal: typing.Union[discord.ui.Modal, None] = None
        self.msg = None
        self.user_id = user_id
        self.external = external
        self.sustained_interaction = None
        if view is not None:
            self.parent_view = view
        else:
            self.parent_view = None

    async def check_ability(self, message):
        if message.content or message.embeds is not None:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = False

            await message.edit(view=self)
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = True
            await message.edit(view=self)

    @discord.ui.button(
        label="Set Message",
        style=discord.ButtonStyle.secondary,
    )
    async def content(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = SetContent()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            await chosen_interaction_message.edit(content=modal.name.value)
            await self.check_ability(chosen_interaction_message)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Remove Embed",
        style=discord.ButtonStyle.secondary,
    )
    async def remove_embed(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            if len(interaction.message.embeds) > 0:
                if self.parent_view is not None:
                    if self.sustained_interaction:
                        chosen_interaction_message = (
                            await self.sustained_interaction.original_response()
                        )
                    else:
                        chosen_interaction_message = interaction.message
                    await chosen_interaction_message.edit(
                        view=self.parent_view, embed=None
                    )
                    await int_invis_embed(interaction, "embed removed.", ephemeral=True)
                else:
                    newView = MessageCustomisation(interaction.user.id)
                    self.parent_view = newView
                    await interaction.message.edit(view=newView, embed=None)
                    return await int_invis_embed(
                        interaction, "embed removed.", ephemeral=True
                    )
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.success, disabled=True)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            for item in self.children:
                item.disabled = True
            self.msg = interaction.message
            self.value = "finish"
            if not self.external:
                await interaction.response.defer(thinking=False)
            else:
                await int_invis_embed(
                    interaction,
                    "your custom message has been created. You can now continue with your configuration.",
                )
            if not self.sustained_interaction:
                await interaction.message.edit(view=None)
            if self.parent_view is not None:
                self.parent_view.stop()
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Set Title",
        row=1,
        style=discord.ButtonStyle.secondary,
    )
    async def set_title(self, interaction: discord.Interaction, _: discord.ui.Button):
        if interaction.user.id == self.user_id:
            modal = SetTitle()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            embed = interaction.message.embeds[0]
            embed.title = modal.name.value
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            await chosen_interaction_message.edit(embed=embed)
            await self.check_ability(chosen_interaction_message)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Set Description",
        row=1,
        style=discord.ButtonStyle.secondary,
    )
    async def set_description(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = SetDescription()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            embed = interaction.message.embeds[0]
            embed.description = modal.name.value
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            await chosen_interaction_message.edit(embed=embed)
            await self.check_ability(chosen_interaction_message)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Set Embed Colour",
        row=1,
        style=discord.ButtonStyle.secondary,
    )
    async def set_color(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = SetColour()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            embed = interaction.message.embeds[0]
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            try:
                embed.colour = modal.name.value
            except TypeError:
                try:
                    embed.colour = int(modal.name.value.replace("#", ""), 16)
                except TypeError:
                    return await interaction.response.send_message(
                        embed=discord.Embed(
                            title="Invalid Colour",
                            description="This colour is invalid.",
                            color=BLANK_COLOR,
                        ),
                        ephemeral=True,
                    )
            await chosen_interaction_message.edit(embed=embed)
            await self.check_ability(chosen_interaction_message)

        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Set Thumbnail",
        row=2,
        style=discord.ButtonStyle.secondary,
    )
    async def set_thumbnail(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = SetThumbnail()
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            embed = interaction.message.embeds[0]
            embed.set_thumbnail(url=modal.thumbnail.value)

            try:
                await chosen_interaction_message.edit(embed=embed)
            except discord.HTTPException:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Unavailable URL",
                        description="This URL is invalid or unavailable.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
            await self.check_ability(chosen_interaction_message)

        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Set Image",
        row=2,
        style=discord.ButtonStyle.secondary,
    )
    async def set_image(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = SetImage()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            embed = interaction.message.embeds[0]
            embed.set_image(url=modal.image.value)
            try:
                await chosen_interaction_message.edit(embed=embed)
            except discord.HTTPException:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Unavailable URL",
                        description="This URL is invalid or unavailable.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
            await self.check_ability(chosen_interaction_message)

        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Add Field",
        row=3,
        style=discord.ButtonStyle.secondary,
    )
    async def add_field(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = AddField()
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message

            await interaction.response.send_modal(modal)
            timeout = await modal.wait()
            if timeout:
                return
            self.modal = modal
            if len(interaction.message.embeds) == 0:
                return
            embed = interaction.message.embeds[0]
            try:
                inline = modal.inline.value
                if inline.lower() in ["yes", "y", "true"]:
                    inline = True
                elif inline.lower() in ["no", "n", "false"]:
                    inline = False
                else:
                    inline = False
                embed.add_field(
                    name=modal.name.value, value=modal.value.value, inline=inline
                )
            except AttributeError:
                return
            await chosen_interaction_message.edit(embed=embed)
            await self.check_ability(chosen_interaction_message)
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Set Footer",
        row=3,
        style=discord.ButtonStyle.secondary,
    )
    async def set_footer(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            modal = SetFooter()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            embed = interaction.message.embeds[0]
            embed.set_footer(text=modal.name.value, icon_url=modal.icon.value)
            try:
                await chosen_interaction_message.edit(embed=embed)
            except discord.HTTPException:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Unavailable URL",
                        description="This URL is invalid or unavailable.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
            await self.check_ability(chosen_interaction_message)

        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

    @discord.ui.button(
        label="Set Author",
        row=3,
        style=discord.ButtonStyle.secondary,
    )
    async def set_author(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id == self.user_id:
            modal = SetAuthor()
            await interaction.response.send_modal(modal)
            await modal.wait()
            self.modal = modal
            if self.sustained_interaction:
                chosen_interaction_message = (
                    await self.sustained_interaction.original_response()
                )
            else:
                chosen_interaction_message = interaction.message
            embed = interaction.message.embeds[0]
            embed.set_author(
                name=modal.name.value,
                url=modal.url.value,
                icon_url=modal.icon.value,
            )
            try:
                await chosen_interaction_message.edit(embed=embed)
            except discord.HTTPException:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Unavailable URL",
                        description="This URL is invalid or unavailable.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
            await self.check_ability(chosen_interaction_message)

        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class RemoveReminder(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    @discord.ui.button(label="Delete a reminder", style=discord.ButtonStyle.danger)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.response.defer()
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(view=self)
            self.value = "delete"
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class RemoveCustomCommand(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    @discord.ui.button(
        label="Delete a custom command", style=discord.ButtonStyle.danger
    )
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id == self.user_id:
            await interaction.response.defer()
            for item in self.children:
                item.disabled = True
            await interaction.edit_original_response(view=self)
            self.value = "delete"
            self.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class RemoveWarning(discord.ui.View):
    def __init__(self, bot, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.bot = bot
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)
        await interaction.response.defer()
        for item in self.children:
            self.remove_item(item)
        self.value = True

        # success = discord.Embed(
        #     title="<:CheckIcon:1035018951043842088> Removed Punishment",
        #     description="<:ArrowRightW:1035023450592514048>I've successfully removed the punishment from the user.",
        #     color=0x71C15F,
        # )

        # await interaction.edit_original_response(embed=success, view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)
        await interaction.response.defer()
        for item in self.children:
            self.remove_item(item)
        self.value = False

        # success = discord.Embed(
        #     title="<:ErrorIcon:1035000018165321808> Cancelled",
        #     description="<:ArrowRightW:1035023450592514048>The punishment has not been removed from the user.",
        #     color=0xFF3C3C,
        # )
        #
        # await interaction.edit_original_response(embed=success, view=self)
        self.stop()


class RequestReason(discord.ui.Modal, title="Edit Reason"):
    name = discord.ui.TextInput(label="Reason")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class RequestData(discord.ui.Modal, title="Edit Reason"):
    data = discord.ui.TextInput(label="Reason")

    def __init__(self, title="PLACEHOLDER", label="PLACEHOLDER"):
        self.data.label = label
        super().__init__(title=title)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class CustomModal(discord.ui.Modal, title="Edit Reason"):
    def __init__(self, title, options, epher_args: dict = None):
        super().__init__(title=title)
        if epher_args is None:
            epher_args = {}
        self.saved_items = {}
        self.epher_args = epher_args
        self.interaction = None

        for name, option in options:
            self.add_item(option)
            self.saved_items[name] = option

    async def on_submit(self, interaction: discord.Interaction):
        for key, item in self.saved_items.items():
            setattr(self, key, item)
        self.interaction = interaction
        await interaction.response.defer(**self.epher_args)
        self.stop()


class SetContent(discord.ui.Modal, title="Set Message Content"):
    name = discord.ui.TextInput(
        label="Content",
        placeholder="Content of the message",
        max_length=2000,
        style=discord.TextStyle.long,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        self.stop()


class CreatePunishmentType(discord.ui.Modal, title="Create Punishment Type"):
    name = discord.ui.TextInput(
        label="Name",
        placeholder="e.g. Verbal Warning",
        max_length=20,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        self.stop()


class DeletePunishmentType(discord.ui.Modal, title="Delete Punishment Type"):
    name = discord.ui.TextInput(
        label="Name",
        placeholder="e.g. Verbal Warning",
        max_length=20,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class RobloxUsername(discord.ui.Modal, title="Verification"):
    name = discord.ui.TextInput(
        label="Roblox Username",
        placeholder="e.g. RoyalCrests",
        max_length=32,
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        self.stop()


class SetTitle(discord.ui.Modal, title="Set Embed Title"):
    name = discord.ui.TextInput(
        label="Title", placeholder="Title of the embed", style=discord.TextStyle.short
    )
    url = discord.ui.TextInput(
        label="Title URL",
        placeholder="URL of the title",
        style=discord.TextStyle.short,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class CustomCommandSettings(discord.ui.Modal, title="Custom Command Settings"):
    name = discord.ui.TextInput(
        label="Custom Command Name",
        placeholder="e.g. ssu",
        style=discord.TextStyle.short,
        max_length=20,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class SetDescription(discord.ui.Modal, title="Set Embed Description"):
    name = discord.ui.TextInput(
        label="Description",
        placeholder="Description of the embed",
        style=discord.TextStyle.long,
        max_length=2000,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class SetColour(discord.ui.Modal, title="Set Embed Colour"):
    name = discord.ui.TextInput(
        label="Colour", placeholder="#DB514F", style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class SetImage(discord.ui.Modal, title="Set Image"):
    image = discord.ui.TextInput(
        label="Image URL", placeholder="Image URL", style=discord.TextStyle.short
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class AddField(discord.ui.Modal, title="Add Field"):
    name = discord.ui.TextInput(
        label="Field Name", placeholder="Field Name", style=discord.TextStyle.short
    )
    value = discord.ui.TextInput(
        label="Field Value", placeholder="Field Value", style=discord.TextStyle.short
    )
    inline = discord.ui.TextInput(
        label="Inline?",
        placeholder="Yes/No",
        default="Yes",
        style=discord.TextStyle.short,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class SetFooter(discord.ui.Modal, title="Set Footer"):
    name = discord.ui.TextInput(
        label="Footer Text", placeholder="Footer Text", style=discord.TextStyle.short
    )
    icon = discord.ui.TextInput(
        label="Footer Icon URL",
        placeholder="Footer Icon URL",
        default="",
        style=discord.TextStyle.short,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class SetAuthor(discord.ui.Modal, title="Set Author"):
    name = discord.ui.TextInput(
        label="Author Name", placeholder="Author Name", style=discord.TextStyle.short
    )
    url = discord.ui.TextInput(
        label="Author URL",
        placeholder="Author URL",
        default="",
        style=discord.TextStyle.short,
        required=False,
    )
    icon = discord.ui.TextInput(
        label="Author Icon URL",
        placeholder="Author Icon URL",
        default="",
        style=discord.TextStyle.short,
        required=False,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class SetThumbnail(discord.ui.Modal, title="Set Thumbnail"):
    thumbnail = discord.ui.TextInput(
        label="Thumbnail URL",
        placeholder="Thumbnail URL",
        style=discord.TextStyle.short,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class TimeRequest(discord.ui.Modal, title="Temporary Ban"):
    time = discord.ui.TextInput(label="Time (s/m/h/d)")

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)

        self.stop()


class ChangeWarningType(discord.ui.Select):
    def __init__(self, user_id, options: list):
        self.user_id: int = user_id

        selected_options = []
        using_options = False
        for option in options:
            if isinstance(option, str | int):
                option = discord.SelectOption(
                    label=str(option),
                    value=str(option),
                )
                selected_options.append(option)
                using_options = True
            elif isinstance(option, discord.SelectOption):
                option.emoji = "<:MalletWhite:1035258530422341672>"
                selected_options.append(option)
                using_options = True

        if not using_options:
            selected_options = [
                discord.SelectOption(
                    label="Warning",
                    value="Warn",
                    description="A warning, the smallest form of logged punishment",
                ),
                discord.SelectOption(
                    label="Kick",
                    value="Kick",
                    description="Removing a user from the game, usually given after warnings",
                ),
                discord.SelectOption(
                    label="Ban",
                    value="Ban",
                    description="A permanent form of removing a user from the game, given after kicks",
                ),
                discord.SelectOption(
                    label="Temporary Ban",
                    value="Temporary Ban",
                    description="Given after kicks, not enough to warrant a permanent removal",
                ),
                discord.SelectOption(
                    label="BOLO",
                    value="BOLO",
                    description="Cannot be found in the game, be on the lookout",
                ),
            ]
        super().__init__(
            placeholder="Select a warning type",
            min_values=1,
            max_values=1,
            options=selected_options,
        )

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            if self.values[0] == "Temporary Ban":
                modal = TimeRequest()
                await interaction.response.send_modal(modal)
                seconds = 0
                if modal.time.value.endswith("s", "m", "h", "d"):
                    if modal.time.value.endswith("s"):
                        seconds = int(modal.time.value.removesuffix("s"))
                    elif modal.time.value.endswith("m"):
                        seconds = int(modal.time.value.removesuffix("m")) * 60
                    elif modal.time.value.endswith("h"):
                        seconds = int(modal.time.value.removesuffix("h")) * 60 * 60
                    else:
                        seconds = int(modal.time.value.removesuffix("d")) * 60 * 60 * 24
                else:
                    seconds = int(modal.time.value)
            await interaction.response.defer()
            try:
                self.view.value = [self.values[0], seconds]
            except UnboundLocalError:
                self.view.value = self.values[0]
            self.view.stop()
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class EditWarningSelect(discord.ui.Select):
    def __init__(self, user_id: int, inherited_options: list):
        self.user_id: int = user_id
        self.inherited_options = inherited_options

        options = [
            discord.SelectOption(
                label="Edit reason",
                value="edit",
                description="Edit the reason of the punishment",
            ),
            discord.SelectOption(
                label="Change punishment type",
                value="change",
                description="Change the punishment type to a higher or lower severity",
            ),
            discord.SelectOption(
                label="Delete punishment",
                value="delete",
                description="Delete the punishment from the database. This is irreversible.",
            ),
        ]

        super().__init__(
            placeholder="Select an option", min_values=1, max_values=1, options=options
        )

    # This one is similar to the confirmation button except sets the inner value to `False`
    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id == self.user_id:
            self.view.value = self.values[0]
            if self.view.value == "edit":
                if interaction.user.id != self.user_id:
                    return
                # await interaction.response.defer()
                for item in self.view.children:
                    item.disabled = True
                self.view.value = "edit"

                self.view.modal = RequestReason()
                await interaction.response.send_modal(self.view.modal)
                await self.view.modal.wait()
                self.view.further_value = self.view.modal.name.value
                self.view.stop()
            elif self.view.value == "change":
                if interaction.user.id != self.user_id:
                    return
                for item in self.view.children:
                    item.disabled = True
                self.value = "type"
                view = WarningDropdownMenu(interaction.user.id, self.inherited_options)
                await interaction.message.edit(
                    content="<:ERMPending:1111097561588183121> **{},** please select a new punishment type.".format(
                        interaction.user.name
                    ),
                    embed=None,
                    view=view,
                )
                await view.wait()
                self.view.further_value = view.value

                self.view.stop()
            elif self.view.value == "delete":
                if interaction.user.id != self.user_id:
                    return
                await interaction.response.defer()
                for item in self.view.children:
                    item.disabled = True
                self.value = "delete"
                await interaction.edit_original_response(view=self.view)
                self.view.stop()
            else:
                await int_failure_embed(interaction, "you have not picked an option.")
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)


class EditWarning(discord.ui.View):
    def __init__(self, bot, user_id, options):
        super().__init__(timeout=600.0)
        self.value: typing.Union[None, str] = None
        self.bot: typing.Union[
            discord.ext.commands.Bot, discord.ext.commands.AutoShardedBot
        ] = bot
        self.user_id: int = user_id
        self.modal: typing.Union[None, discord.ui.Modal] = None
        self.further_value: typing.Union[None, str] = None
        self.options = options
        self.add_item(EditWarningSelect(user_id, options))


class RemoveBOLO(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            return
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = True

        await interaction.edit_original_response(
            content=f"<:ERMCheck:1111089850720976906> **{interaction.user.name}**, I've removed the BOLO from that user.",
            view=self,
        )
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)
        await interaction.response.defer()
        for item in self.children:
            item.disabled = True
        self.value = False

        await interaction.edit_original_response(
            content=f"<:ERMCheck:1111089850720976906> **{interaction.user.name}**, sounds good! I won't remove that punishment.",
            view=self,
        )
        self.stop()


class EnterRobloxUsername(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        self.modal: typing.Union[None, RobloxUsername] = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)
        self.modal = RobloxUsername()
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        self.stop()


class RequestDataView(discord.ui.View):
    def __init__(self, user_id, title: str, label: str):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        self.modal: typing.Union[None, RequestData] = None
        self.title = title
        self.label = label
        for item in self.children:
            item.label = self.title

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Enter Strike Amount", style=discord.ButtonStyle.secondary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)
        self.modal = RequestData(self.title, self.label)
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        self.stop()


class CustomModalView(discord.ui.View):
    def __init__(
        self,
        user_id,
        title: str,
        label: str,
        options: typing.List[typing.Tuple[str, discord.ui.TextInput]],
        epher_args: typing.Optional[dict] = None,
    ):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        self.modal: typing.Union[None, CustomModal] = None
        self.title = title
        self.label = label
        self.options = options
        self.epher_args = epher_args or {}

        for item in self.children:
            item.label = self.title

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Enter Strike Amount", style=discord.ButtonStyle.secondary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

        self.modal = CustomModal(self.label, self.options, self.epher_args)

        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        self.stop()


class GoogleSpreadsheetModification(discord.ui.View):
    def __init__(self, bot, config: dict, scopes: list, label: str, url: str):
        super().__init__(timeout=600.0)
        self.add_item(discord.ui.Button(label=label, url=url))
        self.bot = bot
        self.config = config
        self.scopes = scopes
        self.url = url

    @discord.ui.button(label="Request Ownership", style=discord.ButtonStyle.secondary)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = CustomModal(
            "Request Ownership",
            [
                (
                    "email",
                    discord.ui.TextInput(
                        placeholder="Email",
                        min_length=1,
                        max_length=100,
                        label="Email",
                        custom_id="email",
                    ),
                )
            ],
        )

        await interaction.response.send_modal(modal)

        timeout = await modal.wait()
        if timeout:
            return

        email = modal.email.value

        client = gspread.service_account_from_dict(self.config)
        sheet = client.open_by_url(self.url)
        client.insert_permission(sheet.id, value=email, perm_type="user", role="writer")
        permission_id = (sheet.list_permissions())[0]["id"]
        sheet.transfer_ownership(permission_id)

        self.remove_item(button)

        await interaction.edit_original_response(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Ownership Transferred",
                description="An ownership transfer request has been sent to your email.",
                color=GREEN_COLOR,
            ),
            view=self,
        )


class ConditionCreationToolkit(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=600.0)
        self.hidden_items = []
        self.hidden_selects = []
        self.bot = bot

        self.execution_interval = 300
        self.conditions = []
        self.constant = 0

        self.select_data = {}

        self.hide_buttons()
        self.refresh_ui()

    def hide_buttons(self):
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                self.hidden_items.append(item)
                self.remove_item(item)
            if isinstance(item, discord.ui.Select):
                if item.placeholder == "Select a logic gate":
                    self.hidden_selects.append(item)
                    self.remove_item(item)

    def refresh_ui(self, set_defaults=True):
        if len(self.hidden_selects) != 0 and len(self.conditions) != 0:
            for item in self.hidden_selects:
                item.row = 3
                self.add_item(item)
                self.hidden_selects = []

        if set_defaults:
            for item in self.children:
                if isinstance(item, discord.ui.Select):
                    item.disabled = False
                    for idx, option in enumerate(item.options):
                        option.default = option.value in item.values
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Select):
                    item._values = []

        if all(
            [
                len(i.values) != 0
                for i in list(
                    filter(
                        lambda x: isinstance(x, discord.ui.Select)
                        and x.placeholder != "Select a logic gate",
                        self.children,
                    )
                )
            ]
        ):
            for item in self.hidden_items:
                if "Value: " in item.label:
                    item.label = item.label.replace(
                        item.label.split("Value: ")[1], str(self.constant)
                    )
                self.add_item(item)
            self.hidden_items = []
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button) and item.label not in [
                    "Finish",
                    "Delete Last Condition",
                ]:
                    self.hidden_items.append(item)
                    self.remove_item(item)

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if "Value: " in item.label:
                    item.label = item.label.replace(
                        item.label.split("Value: ")[1], str(self.constant)
                    )
            if isinstance(item, discord.ui.Select):
                if (
                    item.placeholder == "Select a logic gate"
                    and len(self.conditions) == 0
                ):
                    self.hidden_selects.append(item)
                    self.remove_item(item)

        return self

    async def update_embed(self, interaction: discord.Interaction, set_default=True):
        embed = discord.Embed(
            title="Change Conditions",
            description="Conditions are requirements that must be met for the action. When a condition is selected, the action will be activated when the condition is met. Otherwise, the action will only be executed when ran with `/actions execute`.\n\n**If ...**",
            color=BLANK_COLOR,
        )
        embed.add_field(
            name="Execution Interval",
            value=td_format(datetime.timedelta(seconds=self.execution_interval)),
            inline=False,
        )

        for item in self.conditions:
            embed.description += f"\n> **{(('`{}`'.format(item.get('LogicGate', '').upper())) + ' ') if item.get('LogicGate', '') != '' else ''}{item['Variable']}** `{item['Operation']}` {item['Value']}"

        if len(self.conditions) == 0:
            embed.description += f"\n> *No Conditions*"

        await interaction.edit_original_response(
            embed=embed, view=self.refresh_ui(set_default)
        )

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.green, row=4)
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        await interaction.delete_original_response()
        self.stop()

    @discord.ui.button(label="Add Condition", style=discord.ButtonStyle.green, row=4)
    async def add_condition(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        condition_data = {}
        if self.constant != 0:
            condition_data["Value"] = self.constant
            self.constant = 0

        for select in list(
            filter(lambda x: isinstance(x, discord.ui.Select), self.children)
        ):
            if len(select.values) == 0:
                return await interaction.response.send_message(
                    embed=discord.Embed(
                        title="Invalid Condition",
                        description="You must select all required values to populate a condition.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )  # this shouldnt be possible, but its good measure

            def set_default(option):
                option.default = False
                return True  # keep the option!

            select.options = list(filter(set_default, select.options))

            if select.values[0] in condition_options.values():
                print("op")
                condition_data["Operation"] = select.values[0]
                continue

            if select.values[0] in ["and", "or"]:
                print("logic")
                condition_data["LogicGate"] = select.values[0]
                continue

            if (
                select.values[0] in server_conditions.values()
                and condition_data.get("Variable") is None
            ):
                if "X" in select.values[0]:  # requires dynamic argument
                    condition_data["Variable"] = (
                        select.values[0] + f" {self.select_data.get(select)}"
                    )
                    continue
                print("var")
                condition_data["Variable"] = select.values[0]
                continue
            else:
                if (
                    condition_data.get("Value") is None
                ):  # check for preoccupied constant :)
                    if "X" in select.values[0]:  # requires dynamic argument
                        condition_data["Value"] = (
                            select.values[0] + f" {self.select_data.get(select)}"
                        )
                        continue
                    print("val")
                    condition_data["Value"] = select.values[0]
                    continue

        self.conditions.append(condition_data)
        await interaction.response.defer(thinking=False)

        await self.update_embed(interaction, False)

    @discord.ui.button(
        label="Delete Last Condition", style=discord.ButtonStyle.red, row=4
    )
    async def delete_condition(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if len(self.conditions) == 0:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Invalid Condition",
                    description="You must have at least one condition to delete.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )
        self.conditions.pop()
        await interaction.response.defer(thinking=False)
        await self.update_embed(interaction)

    @discord.ui.button(
        label="Change Interval",
        style=discord.ButtonStyle.secondary,
        row=4,
        disabled=False,
    )
    async def change_interval(
        self, interaction: discord.Interaction, button: discord.ui.button
    ):
        modal = CustomModal(
            "Change Execution Interval",
            [
                (
                    "interval",
                    discord.ui.TextInput(
                        placeholder="Interval (s/m/h/d)",
                        min_length=1,
                        max_length=5,
                        label="Interval",
                    ),
                )
            ],
            {"ephemeral": True},
        )
        await interaction.response.send_modal(modal)
        timeout = await modal.wait()
        if timeout:
            return
        try:
            seconds = time_converter(modal.interval.value)
        except ValueError as _:
            return await modal.interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Interval",
                    description="The interval you entered is not a valid time.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        self.execution_interval = seconds
        await self.update_embed(interaction)

    @discord.ui.button(
        label="Constant Value: 0",
        style=discord.ButtonStyle.secondary,
        row=4,
        disabled=True,
    )
    async def view_constant_value(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        pass

    @discord.ui.select(
        placeholder="Select a value",
        options=[
            discord.SelectOption(
                label=key, value=value, description=relevant_descriptions[index]
            )
            for index, (key, value) in enumerate(server_conditions.items())
        ],
        max_values=1,
        min_values=0,
    )
    async def condition_select(
        self, interaction: discord.Interaction, select: discord.ui.select
    ):
        if not select.values:
            return await interaction.response.defer(thinking=False)
        if select.values[0] == "ERLC_X_InGame":
            modal = CustomModal(
                "Roblox Username",
                [
                    (
                        "roblox_username",
                        discord.ui.TextInput(
                            placeholder="e.g. builderman",
                            min_length=1,
                            max_length=30,
                            label="Roblox Username",
                            custom_id="value",
                        ),
                    )
                ],
                {"ephemeral": True},
            )
            await interaction.response.send_modal(modal)
            timeout = await modal.wait()
            if timeout:
                select._values = []
                await self.update_embed(interaction)

            roblox_username = modal.roblox_username.value
            try:
                await self.bot.roblox.get_user_by_username(roblox_username)
            except Exception as e:
                select._values = []
                await self.update_embed(interaction)
                await modal.interaction.followup.send(
                    embed=discord.Embed(
                        title="Invalid Value",
                        description="The value you entered is not a valid Roblox username.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
                return

            self.select_data[select] = roblox_username
        else:
            await interaction.response.defer(thinking=False)
        await self.update_embed(interaction)

    @discord.ui.select(
        placeholder="Select an operation",
        min_values=0,
        max_values=1,
        options=[
            discord.SelectOption(
                label=key, value=value, description=option_descriptions[index]
            )
            for index, (key, value) in enumerate(condition_options.items())
        ],
    )
    async def operation_select(
        self, interaction: discord.Interaction, select: discord.ui.select
    ):
        await interaction.response.defer(thinking=False)
        await self.update_embed(interaction)

    @discord.ui.select(
        placeholder="Select a value",
        min_values=0,
        max_values=1,
        options=[
            discord.SelectOption(
                label=key, value=value, description=relevant_descriptions[index]
            )
            for index, (key, value) in enumerate(server_conditions.items())
        ]
        + [
            discord.SelectOption(
                label="Constant Value",
                value="constant",
                description="A constant value that will be used in the condition",
            )
        ],
    )
    async def value2_select(
        self, interaction: discord.Interaction, select: discord.ui.select
    ):
        if select.values[0] == "constant":
            modal = CustomModal(
                "Constant Value",
                [
                    (
                        "constant",
                        discord.ui.TextInput(
                            placeholder="Value (must be a number)",
                            min_length=1,
                            max_length=5,
                            label="Value",
                            custom_id="value",
                        ),
                    )
                ],
                {"ephemeral": True},
            )
            await interaction.response.send_modal(modal)
            timeout = await modal.wait()
            if timeout:
                select._values = []
                await self.update_embed(interaction)
            if not modal.constant.value.strip().isdigit():
                select._values = []
                await self.update_embed(interaction)
                await modal.interaction.followup.send(
                    embed=discord.Embed(
                        title="Invalid Value",
                        description="The value you entered is not a valid number.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
                return
            self.constant = int(modal.constant.value)
        elif select.values[0] == "ERLC_X_InGame":
            modal = CustomModal(
                "Roblox Username",
                [
                    (
                        "roblox_username",
                        discord.ui.TextInput(
                            placeholder="e.g. builderman",
                            min_length=1,
                            max_length=30,
                            label="Roblox Username",
                            custom_id="value",
                        ),
                    )
                ],
                {"ephemeral": True},
            )
            await interaction.response.send_modal(modal)
            timeout = await modal.wait()
            if timeout:
                select._values = []
                await self.update_embed(interaction)

            roblox_username = modal.roblox_username.value
            try:
                await self.bot.roblox.get_user_by_username(roblox_username)
            except Exception as e:
                select._values = []
                await self.update_embed(interaction)
                await modal.interaction.followup.send(
                    embed=discord.Embed(
                        title="Invalid Value",
                        description="The value you entered is not a valid Roblox username.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
                return

            self.select_data[select] = roblox_username
        else:
            await interaction.response.defer(thinking=False)

        await self.update_embed(interaction)

    @discord.ui.select(
        placeholder="Select a logic gate",
        min_values=0,
        max_values=1,
        options=[
            discord.SelectOption(
                label="AND",
                value="and",
                description="All of the previous conditions must be met for the action to execute.",
            ),
            discord.SelectOption(
                label="OR",
                value="or",
                description="Any of the previous conditions must be met for the action to execute.",
            ),
        ],
    )
    async def logic_gate_select(
        self, interaction: discord.Interaction, select: discord.ui.select
    ):
        await interaction.response.defer(thinking=False)
        await self.update_embed(interaction)


class ActionCreationToolkit(discord.ui.View):
    def __init__(self, bot, action_name, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.bot = bot
        self.user_id = user_id
        self.action_data = {
            "ActionName": action_name,
            "ActionID": next(generator),
            "Triggers": 0,
            "Integrations": [],
            "ConditionExecutionInterval": 300,
            "Conditions": [],
            "Guild": 0,
            "LastExecuted": 0,
        }

        def return_correspondent_callback(item):
            async def unnative_callback(interaction):
                await self.native_callback(interaction, item)

            return unnative_callback

        actions = [
            "Execute Custom Command",
            "Toggle Reminder",
            "Force All Staff Off Duty",
            "Send ER:LC Command",
            "Send ER:LC Message",
            "Send ER:LC Hint",
            "Delay",
            "Add Role",
            "Remove Role",
            "Execute ERM Command"
        ]

        extras = ["Remove Last Integration"]

        for item in actions:
            button = discord.ui.Button(style=discord.ButtonStyle.secondary, label=item)
            button.callback = return_correspondent_callback(item)
            self.add_item(button)

        button = discord.ui.Button( # 🎨 Create a new button
            style=discord.ButtonStyle.primary, label="Access Roles" # 🔘 Set style and label
        ) # 📦 Close button definition
        button.callback = self.set_access_roles # ⚙️ Assign callback function

        self.add_item(button) # ➕ Add button to the view

        for item in extras: # 🔄 Iterate through extra items
            button = discord.ui.Button(style=discord.ButtonStyle.danger, label=item) # 🔘 Create danger button
            button.callback = self.remove_last_integration # ⚙️ Assign removal callback

            self.add_item(button) # ➕ Add removal button to view

        button = discord.ui.Button(style=discord.ButtonStyle.success, label="Finish") # 🔘 Create finish button
        button.callback = self.finish # ⚙️ Assign finish callback

        self.add_item(button) # ➕ Add finish button to view

    async def finish(self, interaction: discord.Interaction): # 🏁 Define finish method
        if len(self.action_data["Integrations"]) == 0: # ❓ Check if no integrations exist
            return await interaction.response.send_message( # 💬 Send error message
                embed=discord.Embed( # 🖼️ Create embed for error
                    title="Not Enough Integrations", # 📝 Set title
                    description="You need at least one integration to finish this action.", # 📝 Set description
                    color=BLANK_COLOR, # 🎨 Set color
                ), # 📦 Close embed
                ephemeral=True, # 🔒 Make it private
            ) # 📦 Close send_message

        self.action_data["Guild"] = interaction.guild.id # 🆔 Store guild ID
        self.stop() # 🛑 Stop the view

    async def remove_last_integration(self, interaction: discord.Interaction): # 🗑️ Define removal method
        if len(self.action_data["Integrations"]) == 0: # ❓ Check if empty
            return await interaction.response.send_message( # 💬 Send error message
                embed=discord.Embed( # 🖼️ Create error embed
                    title="Unable To Remove", # 📝 Set title
                    description="I was unable to remove the last integration from this action. It may be that there are no integrations.", # 📝 Set description
                    color=BLANK_COLOR # 🎨 Set color
                ), # 📦 Close embed
                ephemeral=True # 🔒 Private message
            ) # 📦 Close send_message
        self.action_data["Integrations"].pop(-1) # 📉 Remove last item
        message = interaction.message # 📨 Get origin message
        embed = message.embeds[-1] # 🖼️ Get last embed
        lines = embed.description.splitlines() # 📑 Split description lines
        lines.pop(-2) # ✂️ Remove second to last line
        content = "\n".join(lines) # 🔗 Join lines back
        embed.description = content # 📝 Update description
        await interaction.message.edit(embed=embed) # 🔄 Edit the message
        await interaction.response.defer(thinking=False) # ⏳ Defer response

    async def set_access_roles(self, interaction: discord.Interaction): # 🎭 Define role setting method
        view = RoleSelect(interaction.user.id, limit=10) # 👀 Create role selection view
        view.children[0].default_values = [ # 📋 Set default values
            discord.utils.get(interaction.guild.roles, id=item) # 🔍 Find role by ID
            for item in (self.action_data.get("AccessRoles", []) or []) # 🔄 For each stored role
        ] # 📦 Close list comprehension
        await interaction.response.send_message( # 💬 Prompt for roles
            embed=discord.Embed( # 🖼️ Create prompt embed
                title="Access Roles", # 📝 Set title
                description="These roles will be able to execute this action. **Usually this would be your staff role.**", # 📝 Set description
                color=BLANK_COLOR, # 🎨 Set color
            ), # 📦 Close embed
            view=view, # 👀 Attach view
            ephemeral=True, # 🔒 Private message
        ) # 📦 Close send_message
        timeout = await view.wait() # ⏰ Wait for interaction
        if timeout: # ⌛ If timed out
            return # ↩️ Exit
        self.action_data["AccessRoles"] = [i.id for i in view.value] # 🆔 Save role IDs
        await (await interaction.original_response()).delete() # 🗑️ Cleanup message

    @discord.ui.button( # 🔘 Define UI button
        label="Change Conditions", # 📝 Set button label
        style=discord.ButtonStyle.primary, # 🎨 Primary blue style
        row=2, # 📍 Position on row 2
    ) # 📦 Close decorator
    async def add_condition( # 🛠️ Condition adder method
        self, interaction: discord.Interaction, button: discord.ui.Button # 📥 Input parameters
    ): # 📦 Method body
        embed = discord.Embed( # 🖼️ Create basic embed
            title="Change Conditions", # 📝 Set title
            description="Conditions are requirements that must be met for the action. When a condition is selected, the action will be activated when the condition is met. Otherwise, the action will only be executed when ran with `/actions execute`.\n\n**If ...**\n> *No Conditions*", # 📜 Set description
            color=BLANK_COLOR, # 🎨 Set color
        ) # 📦 Close embed
        if len(self.action_data["Conditions"]) > 0: # ❓ Are there existing conditions?
            embed.description = embed.description.replace("> *No Conditions*", "") # ✂️ Remove placeholder
            for item in self.action_data["Conditions"]: # 🔄 Loop through conditions
                embed.description += f"\n> **{(('`{}`'.format(item.get('LogicGate', '').upper())) + ' ') if item.get('LogicGate', '') != '' else ''}{item['Variable']}** `{item['Operation']}` {item['Value']}" # 📝 Append condition text

        embed.add_field( # ➕ Add info field
            name="Execution Interval", # 🏷️ Field name
            value=td_format( # ⏳ Format time delta
                datetime.timedelta( # ⏰ Create time object
                    seconds=self.action_data["ConditionExecutionInterval"] # ⏱️ Get stored seconds
                ) # 📦 Close timedelta
            ), # 📦 Close td_format
            inline=False, # ↔️ Multiline field
        ) # 📦 Close add_field

        view = ConditionCreationToolkit(self.bot) # 🛠️ Create toolkit view
        await interaction.response.send_message(embed=embed, ephemeral=True, view=view) # 💬 Send setup message
        timeout = await view.wait() # ⏰ Wait for input
        if timeout: # ⌛ Check for timeout
            return # ↩️ Exit early
        self.action_data["Conditions"] = view.conditions # 💾 Save new conditions
        self.action_data["ConditionExecutionInterval"] = view.execution_interval # ⌚ Save interval

        embed = interaction.message.embeds[-1] # 🖼️ Get current embed
        if len(view.conditions) != 0: # ❓ Are conditions present?
            embed.add_field( # ➕ Add field for summary
                name="Conditions", # 🏷️ Field label
                value="\n".join( # 🔗 Join with newlines
                    [ # 🏗️ List comprehension
                        f"> **{('`{}`'.format(item.get('LogicGate', '')) + ' ') if item.get('LogicGate') else ''}{item['Variable']}** `{item['Operation']}` {item['Value']}" # 📝 Format line
                        for item in view.conditions # 🔄 Iterate conditions
                    ] # 📦 Close list
                ), # 📦 Close join
                inline=False, # ↔️ Large field
            ) # 📦 Close add_field
            embed.add_field( # ➕ Add interval summary
                name="Execution Interval", # 🏷️ Label
                value=td_format(datetime.timedelta(seconds=view.execution_interval)), # ⏳ Formatted time
                inline=False, # ↔️ Full width
            ) # 📦 Close add_field
        await interaction.message.edit(embed=embed) # 🔄 Update original message

    async def native_callback(self, interaction: discord.Interaction, button_name):

        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )
        correspondents = {
            "Execute Custom Command": 1,
            "Toggle Reminder": 1,
            "Force All Staff Off Duty": 0,
            "Send ER:LC Command": 1,
            "Send ER:LC Message": 1,
            "Send ER:LC Hint": 1,
            "Delay": 1,
            "Add Role": 1,
            "Remove Role": 1,
            "Execute ERM Command": 1,
        }
        if not correspondents[button_name]:
            msg = interaction.message
            embed = msg.embeds[-1]

            msg.embeds[-1].description = msg.embeds[-1].description.replace("No Integrations", "").replace("*New Integration*", "")
            if (
                len(f" **{button_name}**\n> *New Integration*")
                + len(msg.embeds[-1].description)
            ) > 4000:
                embed = discord.Embed(
                    title="\u200b", color=BLANK_COLOR, description="> "
                )
                embed.description += f" **{button_name}**\n> *New Integration*"
                msg.embeds.append(embed)
            else:
                embed.description += f" **{button_name}**\n> *New Integration*"
                msg.embeds[len(msg.embeds) - 1] = embed

            await interaction.message.edit(embeds=msg.embeds)

            self.action_data["Integrations"].append(
                {
                    "IntegrationName": button_name,
                    "IntegrationID": {
                        "Execute Custom Command": 0,
                        "Toggle Reminder": 1,
                        "Force All Staff Off Duty": 2,
                        "Send ER:LC Command": 3,
                        "Send ER:LC Message": 4,
                        "Send ER:LC Hint": 5,
                        "Delay": 6,
                        "Add Role": 7,
                        "Remove Role": 8,
                        "Execute ERM Command": 9
                    }[button_name],
                    "ExtraInformation": None,
                }
            )

            await interaction.response.send_message(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Successfully Added",
                    description="I have successfully added the integration.",
                    color=GREEN_COLOR,
                ),
                ephemeral=True,
            )

        else:
            extra_information = {
                "Execute Custom Command": ["Custom Command Name", 0],
                "Toggle Reminder": ["Reminder Name", 0],
                "Send ER:LC Command": ["Command", 1],
                "Send ER:LC Message": ["Message", 1],
                "Send ER:LC Hint": ["Hint", 1],
                "Delay": ["Time (Seconds)", 1],
                "Add Role": ["Role ID", 0],
                "Remove Role": ["Role ID", 0],
                "Execute ERM Command": ["Command (without prefix)", 1],
            }

            view = CustomModalView(
                interaction.user.id,
                "Provide Information",
                "Provide Information",
                [
                    (
                        "info",
                        discord.ui.TextInput(label=extra_information[button_name][0]),
                    )
                ],
                {"ephemeral": True},
            )

            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Extra Information",
                    description=f"**{button_name}** requires extra information, provide it by pressing the button below.",
                    color=BLANK_COLOR,
                ),
                view=view,
                ephemeral=True,
            )
            timeout = await view.wait()
            if timeout:
                return
            provided_information = view.modal.info.value
            if not provided_information:
                return
            dynamic = extra_information[button_name][1]

            async def static_validation_failure():
                await view.modal.interaction.followup.send(
                    embed=discord.Embed(
                        title="Incorrect Medium",
                        description="This medium is invalid. Please try again by clicking the button on the initial embed.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )

            if not dynamic:
                if "Role" in button_name:
                    role = interaction.guild.get_role(int(provided_information))
                    if not role:
                        await static_validation_failure()
                    provided_information = int(provided_information)

                if "Reminder" in button_name:
                    # Fetch reminders

                    reminders = await self.bot.reminders.find_by_id(
                        interaction.guild.id
                    )
                    if not reminders:
                        return await static_validation_failure()

                    reminders = reminders.get("reminders", [])
                    if not reminders:
                        return await static_validation_failure()

                    for reminder in reminders:
                        if reminder["name"] == provided_information:
                            break
                    else:
                        return await static_validation_failure()

                if "Custom Command" in button_name:
                    # Fetch Custom Commands

                    custom_commands = await self.bot.custom_commands.find_by_id(
                        interaction.guild.id
                    )
                    custom_commands = (custom_commands or {}).get("commands", [])
                    if not custom_commands:
                        return await static_validation_failure()

                    for command in custom_commands:
                        if command["name"] == provided_information:
                            break
                    else:
                        return await static_validation_failure()

            if "Command (without prefix)" in button_name:
                # strip possible prefix
                provided_information = provided_information.strip()
                if provided_information[0] not in [*string.ascii_lowercase, *string.ascii_uppercase]:
                    provided_information = provided_information[1:]

            self.action_data["Integrations"].append(
                {
                    "IntegrationName": button_name,
                    "IntegrationID": {
                        "Execute Custom Command": 0,
                        "Toggle Reminder": 1,
                        "Force All Staff Off Duty": 2,
                        "Send ER:LC Command": 3,
                        "Send ER:LC Message": 4,
                        "Send ER:LC Hint": 5,
                        "Delay": 6,
                        "Add Role": 7,
                        "Remove Role": 8,
                        "Execute ERM Command": 9
                    }[button_name],
                    "ExtraInformation": provided_information,
                }
            )
            msg = interaction.message
            embed = msg.embeds[-1]
            msg.embeds[-1].description = msg.embeds[-1].description.replace("No Integrations", "").replace("*New Integration*", "")


            if (
                len(
                    f" **{button_name}:** {provided_information}\n> *New Integration*"
                )
                + len(msg.embeds[-1].description)
            ) > 4000:
                embed = discord.Embed(
                    title="\u200b", color=BLANK_COLOR, description="> "
                )
                embed.description += f" **{button_name}:** {provided_information}\n> *New Integration*"
                msg.embeds.append(embed)
            else:
                embed.description += f" **{button_name}:** {provided_information}\n> *New Integration*"
                msg.embeds[len(msg.embeds) - 1] = embed

            await interaction.message.edit(embeds=msg.embeds)



class LinkView(discord.ui.View):
    def __init__(self, label: str, url: str):
        super().__init__(timeout=600.0)
        self.add_item(discord.ui.Button(label=label, url=url))


class RequestGoogleSpreadsheet(discord.ui.View):
    def __init__(
        self,
        bot,
        user_id,
        config: dict,
        scopes: list,
        data: list,
        template: str,
        total_seconds: int,
        type="lb",
        additional_data=None,
        label="Google Spreadsheet",
    ):
        self.bot = bot
        if type:
            self.type = type
        else:
            self.type = "lb"
        if additional_data:
            self.additional_data = additional_data
        else:
            self.additional_data = []

        super().__init__(timeout=600.0)
        self.user_id = user_id
        self.config = config
        self.scopes = scopes
        self.data = data
        self.template = template
        self.total_seconds = total_seconds
        if label:
            for item in self.children:
                item.label = label

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Google Spreadsheet", style=discord.ButtonStyle.secondary)
    async def googlespreadsheet(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(ephemeral=True, thinking=True)

        if interaction.user.id != self.user_id:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )

        await interaction.followup.send(
            embed=discord.Embed(
                title="Generating...",
                description="We are currently generating your Google Spreadsheet.",
                color=BLANK_COLOR,
            )
        )

        client = gspread.service_account_from_dict(self.config)

        sheet: gspread.Spreadsheet = client.copy(
            self.template, interaction.guild.name, copy_permissions=True
        )
        new_sheet = sheet.get_worksheet(0)
        try:
            new_sheet.update_cell(4, 2, f'=IMAGE("{interaction.guild.icon.url}")')
        except AttributeError:
            pass

        if self.type == "lb":
            cell_list = new_sheet.range("D13:H999")
        elif self.type == "ar":
            cell_list = new_sheet.range("D13:I999")

        try:
            new_sheet.update_cell(
                12, 1, td_format(datetime.timedelta(seconds=self.total_seconds))
            )
        except OverflowError:
            pass

        for c, n_v in zip(cell_list, self.data):
            c.value = str(n_v)

        new_sheet.update_cells(cell_list, "USER_ENTERED")
        if self.type == "ar":
            LoAs = sheet.get_worksheet(1)
            LoAs.update_cell(4, 2, f'=IMAGE("{interaction.guild.icon.url}")')
            cell_list = LoAs.range("D13:H999")

            for cell, new_value in zip(cell_list, self.additional_data):
                if isinstance(new_value, int):
                    cell.value = f"=({new_value}/ 86400 + DATE(1970, 1, 1))"
                else:
                    cell.value = str(new_value)
            LoAs.update_cells(cell_list, "USER_ENTERED")

        client.insert_permission(
            sheet.id, value=None, perm_type="anyone", role="writer"
        )

        view = GoogleSpreadsheetModification(
            self.bot, self.config, self.scopes, "Open Google Spreadsheet", sheet.url
        )

        await interaction.edit_original_response(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Successfully generated",
                description="Your Google Spreadsheet has been successfully generated.",
                color=GREEN_COLOR,
            ),
            view=view,
        )

        self.stop()


#
# class LiveMenu(discord.ui.View):
#     def __init__(self, bot, ctx):
#         super().__init__(timeout=600.0)
#         self.bot = bot
#         self.context = ctx
#
#     async def execute_command(
#         self,
#         interaction: discord.Interaction,
#         arguments: str,
#         command: discord.ext.commands.HybridCommand = None,
#         extra_args: dict = None,
#         concatenate_to_last_argument: bool = False,
#         flag_class: discord.ext.commands.FlagConverter = DutyManageOptions,
#     ):
#         if command is None:
#             # assume default
#             command = self.bot.get_command("duty manage")
#         mockinteraction = copy(interaction)
#         mockinteraction._cs_command = command
#         mockinteraction.user = self.context.author
#
#         fakecontext = await discord.ext.commands.Context.from_interaction(
#             mockinteraction
#         )
#         mockcontext = copy(fakecontext)
#         can_run = await command.can_run(mockcontext)
#
#         if not can_run:
#             await interaction.response.send_message(
#                 content="<:ERMClose:1111101633389146223> You do not have permission to run this command!",
#                 ephemeral=True,
#             )
#             return
#
#         mockcontext.command = command
#         mockcontext.author = self.context.author
#
#         if not concatenate_to_last_argument:
#             await mockcontext.invoke(
#                 command,
#                 flags=await flag_class.convert(mockcontext, arguments),
#                 **extra_args,
#             )
#         else:
#             index = 0
#             for key, value in extra_args.copy().items():
#                 if index == len(extra_args) - 1:
#                     value += (" " + arguments)
#                     extra_args[key] = value
#                 index += 1
#
#
#             await mockcontext.invoke(
#                 command,
#                 **extra_args
#             )
#
#     @discord.ui.button(
#         label="On Duty", style=discord.ButtonStyle.green, custom_id="on_duty-execution"
#     )
#     async def on_duty(
#         self, interaction: discord.Interaction, button: discord.ui.Button
#     ):
#         await self.execute_command(
#             interaction, "/onduty=True /without_command_execution=True"
#         )
#
#     @discord.ui.button(
#         label="Toggle Break",
#         style=discord.ButtonStyle.secondary,
#         custom_id="toggle_break-execution",
#     )
#     async def toggle_break(
#         self, interaction: discord.Interaction, button: discord.ui.Button
#     ):
#         await self.execute_command(
#             interaction, "/togglebreak=True /without_command_execution=True"
#         )
#
#     @discord.ui.button(
#         label="Off Duty",
#         style=discord.ButtonStyle.danger,
#         custom_id="off_duty-execution",
#     )
#     async def off_duty(
#         self, interaction: discord.Interaction, button: discord.ui.Button
#     ):
#         await self.execute_command(
#             interaction, "/offduty=True /without_command_execution=True"
#         )
#
#     @discord.ui.button(
#         label="Log Punishment",
#         style=discord.ButtonStyle.secondary,
#         custom_id="punish-execution",
#         row=1,
#     )
#     async def _punish(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.user = None
#         self.punish_type = None
#         self.reason = None
#
#         class PunishModal(discord.ui.Modal):
#             def __init__(modal):
#                 super().__init__(title="Log Punishment", timeout=600.0)
#                 modal.add_item(
#                     discord.ui.TextInput(label="ROBLOX User", placeholder="ROBLOX User")
#                 )
#                 modal.add_item(
#                     discord.ui.TextInput(
#                         label="Punishment Type", placeholder="Punishment Type"
#                     )
#                 )
#                 modal.add_item(
#                     discord.ui.TextInput(label="Reason", placeholder="Reason")
#                 )
#
#             async def on_submit(modal, modal_interaction: discord.Interaction):
#                 for item in modal.children:
#                     if item.label == "ROBLOX User":
#                         self.user = item.value
#                     elif item.label == "Punishment Type":
#                         self.punish_type = item.value
#                     elif item.label == "Reason":
#                         self.reason = item.value
#                 await self.execute_command(
#                     modal_interaction,
#                     "\n/ephemeral=True /without_command_execution=True",
#                     command=self.bot.get_command("punish"),
#                     extra_args={
#                         "user": self.user,
#                         "type": self.punish_type,
#                         "reason": self.reason,
#                     },
#                     concatenate_to_last_argument=True,
#                     flag_class=PunishOptions,
#                 )
#
#         await interaction.response.send_modal(PunishModal())
#         self.user = None
#         self.punish_type = None
#         self.reason = None
#
#     @discord.ui.button(
#         label="Search",
#         style=discord.ButtonStyle.secondary,
#         custom_id="search-execution",
#         row=1,
#     )
#     async def _search(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.user = None
#
#         class SearchModal(discord.ui.Modal):
#             def __init__(modal):
#                 super().__init__(title="Search User", timeout=600.0)
#                 modal.add_item(
#                     discord.ui.TextInput(label="ROBLOX User", placeholder="ROBLOX User")
#                 )
#
#             async def on_submit(modal, modal_interaction: discord.Interaction):
#                 for item in modal.children:
#                     if item.label == "ROBLOX User":
#                         self.user = item.value
#                 await self.execute_command(
#                     modal_interaction,
#                     "/ephemeral=True /without_command_execution=True",
#                     command=self.bot.get_command("search"),
#                     extra_args={
#                         "query": self.user
#                     },
#                     flag_class=SearchOptions,
#                 )
#
#         await interaction.response.send_modal(SearchModal())
#         self.user = None
#
#     @discord.ui.button(
#         label="Active BOLOs",
#         style=discord.ButtonStyle.secondary,
#         custom_id="bolos-execution",
#         row=1,
#     )
#     async def _bolos(self, interaction: discord.Interaction, button: discord.ui.Button):
#         self.user = None
#
#         class SearchModal(discord.ui.Modal):
#             def __init__(modal):
#                 super().__init__(title="BOLO Search", timeout=600.0)
#                 modal.add_item(
#                     discord.ui.TextInput(label="ROBLOX User", placeholder="Optional, leave empty for all", required=False)
#                 )
#
#             async def on_submit(modal, modal_interaction: discord.Interaction):
#                 for item in modal.children:
#                     if item.label == "ROBLOX User":
#                         self.user = item.value
#                 args = {}
#                 if self.user.strip() != "":
#                     args['user'] = self.user
#
#                 await self.execute_command(
#                     modal_interaction,
#                     "/ephemeral=True /without_command_execution=True",
#                     command=self.bot.get_command("bolo active"),
#                     extra_args=args,
#                     flag_class=SearchOptions,
#                 )
#
#         await interaction.response.send_modal(SearchModal())
#         self.user = None


class Verification(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        self.modal: typing.Union[None, RobloxUsername] = None

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Done!", style=discord.ButtonStyle.green, emoji="✅")
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

        await interaction.response.defer()

        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

        self.value = "done"
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)
            return await generalised_interaction_check_failure(interaction.followup)

        await interaction.response.defer()

        for item in self.children:
            item.disabled = True
        await interaction.edit_original_response(view=self)

        self.value = "cancel"
        self.stop()


class CustomSelectMenu(discord.ui.View):
    def __init__(self, user_id, options: list, limit: typing.Optional[int] = 1):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

        self.add_item(CustomDropdown(self.user_id, options, limit))


class MultiPaginatorMenu(discord.ui.View):
    def __init__(self, user_id, options: list, pages: dict):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

        self.add_item(MultiPaginatorDropdown(self.user_id, options, pages))


class WarningDropdownMenu(discord.ui.View):
    def __init__(self, user_id, options: list):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id
        new_options = []

        for option in options:
            if isinstance(option, discord.SelectOption):
                new_options.append(option)
            else:
                if isinstance(option, dict):
                    new_options.append(
                        discord.SelectOption(label=option["name"], value=option["name"])
                    )
                else:
                    new_options.append(discord.SelectOption(label=option, value=option))

        self.add_item(ChangeWarningType(self.user_id, new_options))


class ActivityNoticeAdministration(discord.ui.View):
    def __init__(
        self,
        bot,
        user_id: int,
        victim: int,
        guild_id: int,
        request_type: str,
        current_notice=None,
    ):
        super().__init__(timeout=900.0)
        self.user_id = user_id
        self.value = None
        self.stored_interaction = None
        self.victim = victim
        self.bot = bot
        self.guild_id = guild_id
        self.request_type = request_type
        self.current_notice = current_notice

        if self.current_notice is not None:
            self.delete_button = discord.ui.Button(
                label="Delete", style=discord.ButtonStyle.danger
            )
            self.delete_button.callback = self.delete_notice
            self.add_item(self.delete_button)

            self.end_button = discord.ui.Button(
                label="End", style=discord.ButtonStyle.secondary
            )
            self.end_button.callback = self.end_notice
            self.add_item(self.end_button)

            self.extend_button = discord.ui.Button(
                label="Extend", style=discord.ButtonStyle.primary
            )
            self.extend_button.callback = self.extend_notice
            self.add_item(self.extend_button)

    async def visual_close(self, message: discord.Message):
        for item in self.children:
            self.remove_item(item)

        await message.edit(view=self)
        await message.delete()

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )
            return False

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def create_notice(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.modal = CustomModal(
            "Create Activity Notice",
            [
                ("reason", discord.ui.TextInput(label="Reason")),
                ("duration", discord.ui.TextInput(label="Duration")),
            ],
            {"ephemeral": True},
        )

        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        self.stored_interaction = self.modal.interaction
        self.value = "create"

        await self.visual_close(interaction.message)
        self.stop()

    @discord.ui.button(label="List", style=discord.ButtonStyle.secondary)
    async def list_notices(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.defer(thinking=False, ephemeral=True)
        self.stored_interaction = interaction
        self.value = "list"

        await self.visual_close(interaction.message)
        self.stop()

    async def delete_notice(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        self.stored_interaction = interaction
        self.value = "delete"
        await self.visual_close(interaction.message)
        self.stop()

    async def end_notice(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        self.stored_interaction = interaction
        self.value = "end"

        await self.visual_close(interaction.message)
        self.stop()

    async def extend_notice(self, interaction: discord.Interaction):
        self.modal = CustomModal(
            "Extend Activity Notice",
            [("duration", discord.ui.TextInput(label="Duration"))],
            {"ephemeral": True},
        )

        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        self.stored_interaction = self.modal.interaction
        self.value = "extend"
        await self.visual_close(interaction.message)
        self.stop()


class MultiSelectMenu(discord.ui.View):
    def __init__(self, user_id, options: list):
        super().__init__(timeout=600.0)
        self.value = None
        self.user_id = user_id

        self.add_item(MultiDropdown(self.user_id, options))


class NextView(discord.ui.View):
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600.0)

        button = self.children[0]
        button.emoji = discord.PartialEmoji.from_str(
            bot.emoji_controller.get_emoji("arrow")
        )

        self.user_id = user_id
        self.value = None

    @discord.ui.button(emoji="<:arrow:1169695690784518154>")
    async def _next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        self.value = True
        await interaction.response.defer()
        self.stop()


class ShiftTypeManagement(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=600.0)
        self.user_id = user_id
        self.value = None
        self.selected_for_deletion = None
        self.name_for_creation = None
        self.modal = None

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def _create(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        # await interaction.response.defer(thinking=False)
        self.modal = CustomModal(
            "Create Shift Type",
            [
                (
                    "shift_type_name",
                    discord.ui.TextInput(
                        label="Name", placeholder="Name of Shift Type"
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        if self.modal.shift_type_name.value:
            self.name_for_creation = self.modal.shift_type_name.value
        else:
            return
        self.value = "create"
        self.stop()

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.primary)
    async def _edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        # await interaction.response.defer(thinking=False)
        self.modal = CustomModal(
            "Edit Shift Type",
            [
                (
                    "shift_type_name",
                    discord.ui.TextInput(
                        label="Name", placeholder="Name of Shift Type"
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        if self.modal.shift_type_name.value:
            self.name_for_creation = self.modal.shift_type_name.value
        else:
            return
        self.value = "edit"
        self.stop()

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def _delete(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        self.modal = CustomModal(
            "Shift Type Deletion",
            [
                (
                    "shift_type",
                    discord.ui.TextInput(
                        label="Shift Type ID", placeholder="ID of the Shift Type"
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        if self.modal.shift_type.value:
            self.selected_for_deletion = self.modal.shift_type.value
        else:
            return
        self.value = "delete"
        self.stop()


class PermissionTypeManagement(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=600.0)
        self.user_id = user_id
        self.value = None
        self.selected_for_deletion = None
        self.name_for_creation = None
        self.modal = None

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)
    async def _create(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        # await interaction.response.defer(thinking=False)
        self.modal = CustomModal(
            "Create Permission Type",
            [
                (
                    "permission_type_name",
                    discord.ui.TextInput(
                        label="Name", placeholder="Name of Permission Type"
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        if self.modal.permission_type_name.value:
            self.name_for_creation = self.modal.permission_type_name.value
        else:
            return
        self.value = "create"
        self.stop()

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.primary)
    async def _edit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        # await interaction.response.defer(thinking=False)
        self.modal = CustomModal(
            "Edit Permission Type",
            [
                (
                    "permission_type_name",
                    discord.ui.TextInput(
                        label="Name", placeholder="Name of Permission Type"
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        if self.modal.permission_type_name.value:
            self.name_for_creation = self.modal.permission_type_name.value
        else:
            return

        self.value = "edit"
        self.stop()

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)
    async def _delete(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        self.modal = CustomModal(
            "Permission Type Deletion",
            [
                (
                    "permission_type",
                    discord.ui.TextInput(
                        label="Permission Type Name",
                        placeholder="Name of the Permission Type",
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        if self.modal.permission_type.value:
            self.selected_for_deletion = self.modal.permission_type.value
        else:
            return
        self.value = "delete"
        self.stop()


class RoleQuotaManagement(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=600.0)
        self.user_id = user_id
        self.value = None
        self.selected_for_deletion = None
        self.name_for_creation = None
        self.modal = None

    @discord.ui.button(label="Create Role Quota")
    async def _create(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        await interaction.response.defer(thinking=False)
        self.value = "create"
        self.stop()

    @discord.ui.button(label="Delete Role Quota")
    async def _delete(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        self.modal = CustomModal(
            "Role Quota Deletion",
            [
                (
                    "role_id",
                    discord.ui.TextInput(label="Role ID", placeholder="ID of the Role"),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        if self.modal.role_id.value:
            self.selected_for_deletion = self.modal.role_id.value
        else:
            return
        self.value = "delete"
        self.stop()


class AcknowledgeStaffRequest(discord.ui.View):
    def __init__(self, bot: commands.Bot, o_id: ObjectId):
        super().__init__(timeout=None)
        self.bot = bot
        self.o_id = o_id

    @discord.ui.button(label="Acknowledge", style=discord.ButtonStyle.secondary)
    async def acknowledge(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        document = await self.bot.staff_requests.db.find_one({"_id": self.o_id})
        if interaction.user.id in document["acked"]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Already Acknowledged",
                    description="You have already acknowledged this Staff Request.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )
        document["acked"].append(interaction.user.id)
        await self.bot.staff_requests.db.update_one(
            {"_id": document["_id"]}, {"$set": {"acked": document["acked"]}}
        )
        embed = interaction.message.embeds[0]
        if embed.fields[-1].name.startswith("Acknowledgements"):
            index = len(embed.fields) - 1
            embed.set_field_at(
                index,
                name="Acknowledgements [{}]".format(len(document["acked"])),
                value="\n".join(["> <@{}>".format(u) for u in document["acked"]]),
            )
        else:
            embed.add_field(
                name="Acknowledgements [1]",
                value="\n".join(["> <@{}>".format(u) for u in document["acked"]]),
                inline=False,
            )

        await interaction.response.defer(thinking=False)
        await interaction.message.edit(embed=embed, view=self)


class BackNextView(discord.ui.View):
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=600.0)

        emojis = ["l_arrow", "arrow"]
        for button in self.children:
            if isinstance(button, discord.ui.Button):
                array_idx = int(button.label) - 1
                button.emoji = discord.PartialEmoji.from_str(
                    bot.emoji_controller.get_emoji(emojis[array_idx])
                )
                button.label = ""

        self.user_id = user_id
        self.value = None

    @discord.ui.button(label="1", emoji="<:l_arrow:1169754353326903407>")
    async def _back(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        self.value = -1
        self.stop()

    @discord.ui.button(label="2", emoji="<:arrow:1169695690784518154>")
    async def _next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id not in [self.user_id]:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                )
            )
        self.value = 1
        self.stop()


class AssociationConfigurationView(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, associated_defaults: list):
        super().__init__(timeout=None)
        self.bot = bot
        self.user_id = user_id

        for label, defaults in associated_defaults:
            use_configuration = None
            if len(defaults) == 0:
                continue
            if isinstance(defaults[0], list):
                if defaults[0][0] == "CUSTOM_CONF":
                    configurator = defaults[0]
                    match_configurator = configurator[1]
                    if match_configurator.get("_FIND_BY_LABEL") is True:
                        items = defaults[1:]
                        use_configuration = {
                            "configuration": match_configurator,
                            "matchables": items,
                        }
            item = None
            for iterating_item in self.children:
                if getattr(iterating_item, "label", None) is None:
                    if iterating_item.placeholder == label:
                        item = iterating_item
                        break
                else:
                    if iterating_item.label == label:
                        item = iterating_item
                        break
            if use_configuration is None:
                for index, defa in enumerate(defaults):
                    if defa is None:
                        defaults[index] = 0
                item.default_values = [i for i in defaults if i != 0]
            else:
                found_values = []
                for val in use_configuration["matchables"]:
                    if isinstance(item, discord.ui.Select):
                        if (
                            use_configuration["configuration"].get(
                                "_FIND_BY_LABEL", False
                            )
                            is True
                        ):
                            found_value = [i for i in item.options if i.label == val][0]
                            if not found_value:
                                continue
                            found_values.append(found_value)

                if isinstance(item, discord.ui.Select):
                    for val in found_values:
                        find_index = 0
                        for index, option in enumerate(item.options):
                            if option == val:
                                find_index = index
                                break
                        new_opt = item.options[find_index]
                        new_opt.default = True
                        item.options[find_index] = new_opt
                        break

                    for index, option in enumerate(item.options):
                        if index != find_index:
                            option.default = False

    async def on_timeout(self) -> None:
        for i in self.children:
            i.disabled = True
        if not hasattr(self, "message") or not self.message:
            return
        await self.message.edit(view=self)

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )
            return False


class ERLCIntegrationToolkit(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=900)
        self.selected_option = None
        self.user_id = user_id
        self.content = None
        self.message = None

    @discord.ui.button(label="Message", style=discord.ButtonStyle.secondary)
    async def message(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            modal := CustomModal(
                "Edit Message Content",
                [
                    (
                        "msg_content",
                        discord.ui.TextInput(
                            label="Message Content", max_length=250, required=True
                        ),
                    )
                ],
                {"ephemeral": True},
            )
        )
        timeout = await modal.wait()
        if timeout:
            return

        self.content = modal.msg_content.value
        self.selected_option = "Message"
        await self.message.edit(
            embed=discord.Embed(
                title="<:success:1163149118366040106> Success!",
                description="Message integration has successfully been setup.",
                color=GREEN_COLOR,
            ),
            view=None,
        )
        self.stop()

    @discord.ui.button(label="Hint", style=discord.ButtonStyle.secondary)
    async def hint(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(
            modal := CustomModal(
                "Edit Hint Content",
                [
                    (
                        "hint_content",
                        discord.ui.TextInput(
                            label="Hint Content", max_length=250, required=True
                        ),
                    )
                ],
                {"thinking": False},
            )
        )
        timeout = await modal.wait()
        if timeout:
            return

        self.content = modal.hint_content.value
        self.selected_option = "Hint"

        await self.message.edit(
            embed=discord.Embed(
                title="<:success:1163149118366040106> Success!",
                description="Hint integration has successfully been setup.",
                color=GREEN_COLOR,
            ),
            view=None,
        )
        self.stop()


class ReminderCreationToolkit(discord.ui.View):
    def __init__(
        self,
        user_id: int,
        dataset: dict,
        option: typing.Literal["create", "edit"],
        preset_values: dict | None = None,
    ):
        super().__init__(timeout=900.0)
        self.user_id = user_id
        self.dataset = dataset
        self.cancelled = None
        self.option = option

        for key, value in (preset_values or {}).items():
            for item in self.children:
                if isinstance(item, discord.ui.RoleSelect) or isinstance(
                    item, discord.ui.ChannelSelect
                ):
                    if item.placeholder == key:
                        item.default_values = value
                if isinstance(item, discord.ui.Button):
                    if item.label == key:
                        item.label = value["label"]
                        item.style = value["style"]

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True
        else:
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )
            return False

    async def refresh_ui(self, message: discord.Message):
        embed = discord.Embed(
            title=f"{self.option.title()} a Reminder",
            description=(
                f"> **Name:** {self.dataset['name']}\n"
                f"> **ID:** {self.dataset['id']}\n"
                f"> **Channel:** {'<#{}>'.format(self.dataset.get('channel', None)) if self.dataset.get('channel', None) is not None else 'Not set'}\n"
                f"> **Completion Ability:** {self.dataset.get('completion_ability') or 'Not set'}\n"
                f"> **Mentioned Roles:** {', '.join(['<@&{}>'.format(r) for r in self.dataset.get('role', [])]) or 'Not set'}\n"
                f"> **Interval:** {td_format(datetime.timedelta(seconds=self.dataset.get('interval', 0))) or 'Not set'}"
                f"\n\n**Content:**\n{self.dataset['message']}"
            ),
            color=BLANK_COLOR,
        )

        if all(
            [
                self.dataset.get("channel") is not None,
                self.dataset.get("interval") is not None,
            ]
        ):
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = False
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = True

        await message.edit(embed=embed, view=self)

    @discord.ui.select(
        cls=discord.ui.RoleSelect, placeholder="Mentioned Roles", row=0, max_values=25
    )
    async def mentioned_roles_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        await interaction.response.defer()

        self.dataset["role"] = [i.id for i in select.values]
        await self.refresh_ui(interaction.message)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Reminder Channel",
        row=1,
        max_values=1,
        channel_types=[discord.ChannelType.text],
    )
    async def channel_select(
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect
    ):
        await interaction.response.defer()

        self.dataset["channel"] = [i.id for i in select.values][0]
        await self.refresh_ui(interaction.message)

    @discord.ui.button(label="Set Interval", style=discord.ButtonStyle.secondary, row=2)
    async def set_interval(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        self.modal = CustomModal(
            "Set Interval",
            [
                (
                    "interval",
                    discord.ui.TextInput(
                        label="Interval",
                        placeholder="The interval between each reminder. (hours/minutes/seconds/days)",
                        default=str(self.dataset.get("interval", 0)),
                        required=False,
                    ),
                )
            ],
            {"ephemeral": True},
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        try:
            new_time = time_converter(self.modal.interval.value)
        except ValueError:
            return await self.modal.interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Time",
                    description="You did not enter a valid time.",
                    color=BLANK_COLOR,
                )
            )

        self.dataset["interval"] = new_time
        await self.refresh_ui(interaction.message)

    @discord.ui.button(
        label="Edit ER:LC Integration", style=discord.ButtonStyle.secondary, row=2
    )
    async def edit_integration(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        msg = await interaction.response.send_message(
            embed=discord.Embed(
                title="Edit ER:LC Integration",
                description="Here you can edit your reminder's integrations with Emergency Response: Liberty County, such as sending an automatic message or hint on a reminder activation. **As of right now, you can only have one integration type per reminder.**",
                color=BLANK_COLOR,
            ),
            ephemeral=True,
            view=(view := ERLCIntegrationToolkit(interaction.user.id)),
        )
        view.message = await interaction.original_response()
        timeout = await view.wait()
        if timeout:
            return
        selected_integration = view.selected_option
        content = view.content

        self.dataset["integration"] = {
            "type": selected_integration,
            "content": view.content,
        }
        await self.refresh_ui(interaction.message)

    @discord.ui.button(label="Edit Content", style=discord.ButtonStyle.secondary, row=2)
    async def edit_content(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        self.modal = CustomModal(
            "Edit Content",
            [
                (
                    "content",
                    discord.ui.TextInput(
                        label="Content",
                        placeholder="The content of the reminder",
                        default=str(self.dataset.get("message", "")),
                        style=discord.TextStyle.long,
                        max_length=2000,
                        required=False,
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        content = self.modal.content.value

        self.dataset["message"] = content
        await self.refresh_ui(interaction.message)

    @discord.ui.button(
        label="Completion Ability: Disabled", style=discord.ButtonStyle.danger, row=2
    )
    async def edit_completion_ability(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        await interaction.response.defer(thinking=False)
        if button.label == "Completion Ability: Disabled":
            self.dataset["completion_ability"] = True
            button.label = "Completion Ability: Enabled"
            button.style = discord.ButtonStyle.green
        else:
            self.dataset["completion_ability"] = False
            button.label = "Completion Ability: Disabled"
            button.style = discord.ButtonStyle.danger

        await self.refresh_ui(interaction.message)

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=3)
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer(ephemeral=True)
        self.cancelled = True
        await interaction.followup.send(
            embed=discord.Embed(
                title="Successfully cancelled",
                description="This reminder has not been created.",
                color=BLANK_COLOR,
            )
        )
        await interaction.message.delete()
        self.stop()

    @discord.ui.button(
        label="Finish", style=discord.ButtonStyle.green, disabled=True, row=3
    )
    async def finish(self, interaction: discord.Interaction, _: discord.Button):
        await interaction.response.defer()
        self.cancelled = False
        self.stop()


class BasicConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        return await super().interaction_check(interaction)

    @discord.ui.select(
        cls=discord.ui.RoleSelect, placeholder="Staff Roles", row=0, max_values=25
    )
    async def staff_role_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["staff_management"]["role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Staff Roles have been set to {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        cls=discord.ui.RoleSelect, placeholder="Admin Role", row=1, max_values=25
    )
    async def admin_role_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["staff_management"]["admin_role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Admin Role has been set to {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Management Roles",
        row=2,
        max_values=25,
        min_values=0,
    )
    async def management_role_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["staff_management"]["management_role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Management Roles have been set to {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        placeholder="Prefix",
        row=3,
        options=[
            discord.SelectOption(
                label="!", description="Use '!' as your custom prefix."
            ),
            discord.SelectOption(
                label=">", description="Use '>' as your custom prefix."
            ),
            discord.SelectOption(
                label="?", description="Use '?' as your custom prefix."
            ),
            discord.SelectOption(
                label=":", description="Use ':' as your custom prefix."
            ),
            discord.SelectOption(
                label="-", description="Use '-' as your custom prefix."
            ),
        ],
        max_values=1,
    )
    async def prefix_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["customisation"]["prefix"] = select.values[0]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Prefix has been set to {select.values[0]}.",
        )
        for i in select.options:
            i.default = False


# class PunishmentTypesConfiguration(discord.ui.View):
#     def __init__(self, bot, user_id: int, given_data: list):
#             # Init vars
#             self.bot = bot
#             self.user_id = user_id
#             self.given_data = given_data
#
#             # TODO: match given data -> embed structure
#
#     async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
#         if interaction.user.id == self.user_id:
#             return True
#         else:
#             await interaction.response.send_message(embed=discord.Embed(
#                 title="Not Permitted",
#                 description="You are not permitted to interact with these buttons.",
#                 color=blank_color
#             ), ephemeral=True)
#             return False
#
#     @discord.ui.select(options=[
#         discord.SelectOption(
#             label="Add Type",
#             description="Add a Punishment Type",
#             value="add"
#         ),
#         discord.SelectOption(
#             label="Modify Type",
#             description="Change some settings about a punishment type",
#             value="modify"
#         ),
#         discord.SelectOption(
#             label="Delete Type",
#             description="Delete a punishment type",
#             value="delete"
#         )
#     ])


class LOAConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        cls=discord.ui.RoleSelect, placeholder="LOA Role", row=1, max_values=25
    )
    async def loa_role_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["staff_management"]["loa_role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"LOA Role has been set to {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="LOA Channel",
        row=2,
        max_values=1,
        channel_types=[discord.ChannelType.text],
    )
    async def loa_channel_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["staff_management"]["channel"] = select.values[0].id
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"LOA Channel has been set to <#{select.values[0].id}>.",
        )

    @discord.ui.select(
        placeholder="LOA Requests",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="LOA Requests are enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="LOA Requests are disabled.",
            ),
        ],
        max_values=1,
    )
    async def enabled_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["staff_management"]["enabled"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"LOA Requests have been {'enabled' if select.values[0] == 'enabled' else 'disabled'}.",
        )
        for i in select.options:
            i.default = False


class ExtendedShiftOptions(discord.ui.View):
    def __init__(self, bot, associated_defaults: list):
        super().__init__(timeout=None)
        self.modal = None
        self.bot = bot
        self.modal_default = 0
        self.nickname_default = None
        self.quota_default = None

        for label, defaults in associated_defaults:
            if label == "max_staff":
                self.modal_default = defaults
                continue
            if label == "nickname_prefix":
                self.nickname_default = defaults
                continue
            if label == "quota":
                self.quota_default = defaults
                continue
            if label == "Break Roles":
                for item in self.children:
                    if (
                        isinstance(item, discord.ui.Select)
                        and item.placeholder == "Break Roles"
                    ):
                        item.default_values = defaults
                continue
            use_configuration = None
            if isinstance(defaults[0], list):
                if defaults[0][0] == "CUSTOM_CONF":
                    configurator = defaults[0]
                    match_configurator = configurator[1]
                    if match_configurator.get("_FIND_BY_LABEL") is True:
                        items = defaults[1:]
                        use_configuration = {
                            "configuration": match_configurator,
                            "matchables": items,
                        }

            item = None
            for iterating_item in self.children:
                if getattr(iterating_item, "label", None) is None:
                    if iterating_item.placeholder == label:
                        item = iterating_item
                        break
                else:
                    if iterating_item.label == label:
                        item = iterating_item
                        break
            if use_configuration is None:
                for index, defa in enumerate(defaults):
                    if defa is None:
                        defaults[index] = 0
                item.default_values = [i for i in defaults if i != 0]
            else:
                found_values = []
                for val in use_configuration["matchables"]:
                    if isinstance(item, discord.ui.Select):
                        if (
                            use_configuration["configuration"].get(
                                "_FIND_BY_LABEL", False
                            )
                            is True
                        ):
                            found_value = [i for i in item.options if i.label == val][0]
                            if not found_value:
                                continue
                            found_values.append(found_value)

                if isinstance(item, discord.ui.Select):
                    for val in found_values:
                        find_index = 0
                        for index, option in enumerate(item.options):
                            if option == val:
                                find_index = index
                                break
                        new_opt = item.options[find_index]
                        new_opt.default = True
                        item.options[find_index] = new_opt

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Break Roles",
        max_values=25,
        min_values=0,
    )
    async def shift_role_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        # secvuln: prevention
        highest_role_pos = max([i.position for i in interaction.user.roles])
        compared_role_pos = max([role.position for role in select.values])
        if (
            interaction.user.id != interaction.guild.owner_id
            and highest_role_pos <= compared_role_pos
        ):
            # we're not allowing this ...
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Security Concern",
                    description="You cannot choose a Break Role that is higher than your maximum role.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )
            select.default_values = list(
                filter(lambda x: x.position < highest_role_pos, select.values)
            )
            await interaction.message.edit(view=self)
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["shift_management"]["break_roles"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Break Role has been set to {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.button(label="Set Maximum Staff Online", row=4)
    async def set_maximum_staff_online(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        self.modal = CustomModal(
            "Maximum Staff",
            [
                (
                    "max_staff",
                    discord.ui.TextInput(
                        label="Maximum Staff Online",
                        placeholder="This is the amount of staff members that can be online at one time.",
                        default=str(self.modal_default),
                        required=False,
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        max_staff = self.modal.max_staff.value
        max_staff = int(max_staff.strip())

        bot = self.bot
        sett = await bot.settings.find_by_id(interaction.guild.id)
        sett["shift_management"]["maximum_staff"] = max_staff
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Maximum Staff Online has been set to {max_staff}.",
        )
        self.modal_default = max_staff

    @discord.ui.button(label="Set Nickname Prefix", row=3)
    async def set_nickname_prefix(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        self.modal = CustomModal(
            "Nickname Prefix",
            [
                (
                    "nickname_prefix",
                    discord.ui.TextInput(
                        label="Nickname Prefix",
                        placeholder="The nickname prefix that will be used when someone goes On-Duty.",
                        default=str(self.nickname_default),
                        required=False,
                    ),
                )
            ],
        )
        await interaction.response.send_modal(self.modal)
        await self.modal.wait()
        nickname_prefix = self.modal.nickname_prefix.value

        bot = self.bot
        sett = await bot.settings.find_by_id(interaction.guild.id)
        sett["shift_management"]["nickname_prefix"] = nickname_prefix
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Nickname Prefix has been set to {nickname_prefix}.",
        )
        self.nickname_default = nickname_prefix

    @discord.ui.button(label="Set Quota", row=2)
    async def set_quota(self, interaction: discord.Interaction, button: discord.Button):
        quota_hours = self.quota_default
        self.modal = CustomModal(
            "Quota",
            [
                (
                    "quota",
                    discord.ui.TextInput(
                        label="Quota",
                        placeholder="This value will be used to judge whether a staff member has completed quota.",
                        default=td_format(datetime.timedelta(seconds=quota_hours)),
                        required=False,
                    ),
                )
            ],
            epher_args={"ephemeral": True},
        )

        await interaction.response.send_modal(self.modal)
        await self.modal.wait()

        try:
            seconds = time_converter(self.modal.quota.value)
        except ValueError:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="Invalid Time",
                    description="You provided an invalid time format.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

        bot = self.bot
        sett = await bot.settings.find_by_id(interaction.guild.id)
        sett["shift_management"]["quota"] = seconds
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Quota has been set to {td_format(datetime.timedelta(seconds=seconds))}.",
        )
        self.quota_default = seconds


class ShiftConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="On-Duty Role",
        row=2,
        max_values=25,
        min_values=0,
    )
    async def shift_role_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        # secvuln: prevention
        highest_role_pos = max([i.position for i in interaction.user.roles])
        compared_role_pos = max([role.position for role in select.values])
        if (
            interaction.user.id != interaction.guild.owner_id
            and highest_role_pos <= compared_role_pos
        ):
            # we're not allowing this ...
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Security Concern",
                    description="You cannot choose an On-Duty role that is higher than your maximum role.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )
            select.default_values = list(
                filter(lambda x: x.position < highest_role_pos, select.values)
            )
            await interaction.message.edit(view=self)
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["shift_management"]["role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"On-Duty Role has been set to {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Shift Channel",
        row=1,
        max_values=1,
        channel_types=[discord.ChannelType.text],
    )
    async def shift_channel_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["shift_management"]["channel"] = select.values[0].id
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Shift Channel has been set to <#{select.values[0].id}>.",
        )

    @discord.ui.select(
        placeholder="Shift Management",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="Shift Management is enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="Shift Management is disabled.",
            ),
        ],
        max_values=1,
    )
    async def enabled_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["shift_management"]["enabled"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            bot,
            interaction.guild,
            interaction.user,
            f"Shift Management has been {'enabled' if select.values[0] == 'enabled' else 'disabled'}.",
        )
        for i in select.options:
            i.default = False

    @discord.ui.button(label="More Options", row=3)
    async def more_options(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        new_view = ExtendedShiftOptions(
            self.bot,
            [
                ("max_staff", sett["shift_management"].get("maximum_staff", 0)),
                ("quota", sett["shift_management"].get("quota", 0)),
                (
                    "nickname_prefix",
                    sett["shift_management"].get("nickname_prefix", ""),
                ),
                (
                    "Break Roles",
                    [
                        discord.utils.get(interaction.guild.roles, id=i)
                        for i in sett["shift_management"].get("break_roles", [])
                    ],
                ),
            ],
        )
        await interaction.response.send_message(view=new_view, ephemeral=True)

    @discord.ui.button(label="Shift Types", row=3)
    async def shift_types(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        settings = await self.bot.settings.find_by_id(interaction.guild.id)
        shift_types = settings.get("shift_types", {}).get("types", [])

        embed = discord.Embed(title="Shift Types", color=BLANK_COLOR)
        for item in shift_types:
            embed.add_field(
                name=f"{item['name']}",
                value=(
                    f"> **Name:** {item['name']}\n"
                    f"> **ID:** {item['id']}\n"
                    f"> **Channel:** <#{item['channel']}>\n"
                    f"> **Nickname Prefix:** {item.get('nickname') or 'None'}\n"
                    f"> **Access Roles:** {','.join(['<@&{}>'.format(role) for role in item.get('access_roles') or []]) or 'None'}\n"
                    f"> **On-Duty Role:** {','.join(['<@&{}>'.format(role) for role in item.get('role', [])]) or 'None'}"
                ),
                inline=False,
            )

        if len(embed.fields) == 0:
            embed.add_field(
                name="No Shift Types",
                value="There are no shift types on this server.",
                inline=False,
            )
        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )

        view = ShiftTypeManagement(interaction.user.id)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        await view.wait()

        if view.value == "edit":
            selected_item = None
            for item in shift_types:
                if item["name"] == view.name_for_creation:
                    selected_item = item
                    break

            if not selected_item:
                return await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="Incorrect Shift Type",
                        description="This shift type is incorrect or invalid.",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            data = selected_item

            embed = discord.Embed(
                title="Edit a Shift Type",
                description=(
                    f"> **Name:** {data['name']}\n"
                    f"> **ID:** {data['id']}\n"
                    f"> **Shift Channel:** {'<#{}>'.format(data.get('channel', None)) if data.get('channel', None) is not None else 'Not set'}\n"
                    f"> **Nickname Prefix:** {data.get('nickname') or 'None'}\n"
                    f"> **On-Duty Roles:** {', '.join(['<@&{}>'.format(r) for r in data.get('role', [])]) or 'Not set'}\n"
                    f"> **Break Roles:** {', '.join(['<@&{}>'.format(r) for r in data.get('break_roles', [])]) or 'Not set'}\n"
                    f"> **Access Roles:** {', '.join(['<@&{}>'.format(r) for r in data.get('access_roles', [])]) or 'Not set'}\n\n\n"
                    f"Access Roles are roles that are able to freely use this Shift Type and are able to go on-duty as this Shift Type. If an access role is selected, an individual must have it to go on-duty with this Shift Type."
                ),
                color=BLANK_COLOR,
            )

            roles = list(
                filter(
                    lambda x: x is not None,
                    [
                        discord.utils.get(interaction.guild.roles, id=i)
                        for i in data.get("role", [])
                    ],
                )
            )
            break_roles = list(
                filter(
                    lambda x: x is not None,
                    [
                        discord.utils.get(interaction.guild.roles, id=i)
                        for i in data.get("break_roles", [])
                    ],
                )
            )

            access_roles = list(
                filter(
                    lambda x: x is not None,
                    [
                        discord.utils.get(interaction.guild.roles, id=i)
                        for i in data.get("access_roles", [])
                    ],
                )
            )
            shift_channel = list(
                filter(
                    lambda x: x is not None,
                    [
                        discord.utils.get(
                            interaction.guild.channels, id=data.get("channel", 0)
                        )
                    ],
                )
            )

            view = ShiftTypeCreator(
                interaction.user.id,
                data,
                "edit",
                {
                    "On-Duty Roles": roles,
                    "Break Roles": break_roles,
                    "Access Roles": access_roles,
                    "Shift Channel": shift_channel,
                },
            )
            view.restored_interaction = interaction
            msg = await interaction.original_response()
            await msg.edit(view=view, embed=embed)
            await view.wait()
            if view.cancelled is True:
                return

            dataset = settings.get("shift_types", {}).get("types", [])

            for index, item in enumerate(dataset):
                if item["id"] == view.dataset["id"]:
                    dataset[index] = view.dataset
                    break
            if not settings.get("shift_types"):
                settings["shift_types"] = {}
                settings["shift_types"]["types"] = dataset
            else:
                settings["shift_types"]["types"] = dataset

            await self.bot.settings.update_by_id(settings)
            await msg.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Shift Type Edited",
                    description="Your shift type has been edited!",
                    color=GREEN_COLOR,
                ),
                view=None,
            )
            return

        if view.value == "create":
            data = {
                "id": next(generator),
                "name": view.name_for_creation,
                "channel": None,
                "roles": [],
            }
            embed = discord.Embed(
                title="Shift Type Creation",
                description=(
                    f"> **Name:** {data['name']}\n"
                    f"> **ID:** {data['id']}\n"
                    f"> **Shift Channel:** {'<#{}>'.format(data.get('channel', None)) if data.get('channel', None) is not None else 'Not set'}\n"
                    f"> **Nickname Prefix:** {data.get('nickname') or 'None'}\n"
                    f"> **On-Duty Roles:** {', '.join(['<@&{}>'.format(r) for r in data.get('role', [])]) or 'Not set'}\n"
                    f"> **Access Roles:** {', '.join(['<@&{}>'.format(r) for r in data.get('access_roles', [])]) or 'Not set'}\n\n\n"
                    f"Access Roles are roles that are able to freely use this Shift Type and are able to go on-duty as this Shift Type. If an access role is selected, an individual must have it to go on-duty with this Shift Type."
                ),
                color=BLANK_COLOR,
            )

            view = ShiftTypeCreator(interaction.user.id, data, "create")
            view.restored_interaction = interaction
            msg = await interaction.original_response()
            await msg.edit(view=view, embed=embed)
            await view.wait()
            if view.cancelled is True:
                return

            dataset = settings.get("shift_types", {}).get("types", [])

            dataset.append(view.dataset)
            if not settings.get("shift_types"):
                settings["shift_types"] = {}
                settings["shift_types"]["types"] = dataset
            else:
                settings["shift_types"]["types"] = dataset

            await self.bot.settings.update_by_id(settings)
            await msg.edit(
                embed=discord.Embed(
                    title="<:success:1163149118366040106> Shift Type Created",
                    description="Your shift type has been created!",
                    color=GREEN_COLOR,
                ),
                view=None,
            )
            await config_change_log(
                self.bot,
                interaction.guild,
                interaction.user,
                f"Shift Type Created: {view.dataset['name']}",
            )
            return
        elif view.value == "delete":
            try:
                type_id = int(view.selected_for_deletion.strip())
            except ValueError:
                return await (await interaction.original_response()).edit(
                    embed=discord.Embed(
                        title="Invalid Shift Type",
                        description="The ID you have provided is not associated with a shift type.",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            shift_types = settings.get("shift_types", {}).get("types", [])
            if len(shift_types) == 0:
                return await (await interaction.original_response()).edit(
                    embed=discord.Embed(
                        title="Invalid Shift Type",
                        description="The ID you have provided is not associated with a shift type.",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            if type_id not in [t["id"] for t in shift_types]:
                return await (await interaction.original_response()).edit(
                    embed=discord.Embed(
                        title="Invalid Shift Type",
                        description="The ID you have provided is not associated with a shift type.",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            for item in shift_types:
                if item["id"] == type_id:
                    shift_types.remove(item)
                    break

            if not settings.get("shift_types"):
                settings["shift_types"] = {}

            settings["shift_types"]["types"] = shift_types
            await self.bot.settings.update_by_id(settings)
            await config_change_log(
                self.bot,
                interaction.guild,
                interaction.user,
                f"Shift Type Deleted: {item['name']}",
            )
            msg = await interaction.original_response()
            await msg.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Shift Type Deleted",
                    description="Your shift type has been deleted!",
                    color=GREEN_COLOR,
                ),
                view=None,
            )

    @discord.ui.button(label="Role Quotas", row=3)
    async def role_quotas(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        settings = await self.bot.settings.find_by_id(interaction.guild.id)
        role_quotas = settings.get("shift_management").get("role_quotas", [])

        embed = discord.Embed(title="Role Quotas", description="", color=BLANK_COLOR)
        for item in role_quotas:
            role_id, particular_quota = item["role"], item["quota"]
            # role = interaction.guild.get_role(role_id)
            try:
                roles = await interaction.guild.fetch_roles()
                role = discord.utils.get(roles, id=role_id)
            except discord.HTTPException:
                continue

            if not role:
                continue
            embed.description += f"{role.mention} `{role_id}` • {td_format(datetime.timedelta(seconds=particular_quota))}\n"

        if len(embed.description) == 0:
            embed.add_field(
                name="No Role Quotas",
                value="There are no role quotas in this server.",
                inline=False,
            )
        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )

        view = RoleQuotaManagement(interaction.user.id)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

        await view.wait()
        if view.value == "create":
            data = {"role": 0, "quota": 0}
            embed = discord.Embed(
                title="Role Quota Creation",
                description=(
                    f"> **Role:** {'<@&{}>'.format(data['role']) if data['role'] != 0 else 'Not set'}\n"
                    f"> **Quota:** {td_format(datetime.timedelta(seconds=data['quota']))}\n"
                ),
                color=BLANK_COLOR,
            )

            view = RoleQuotaCreator(self.bot, interaction.user.id, data)
            view.restored_interaction = interaction
            msg = await interaction.original_response()
            await msg.edit(view=view, embed=embed)
            await view.wait()
            if view.cancelled is True:
                return

            dataset = settings.get("shift_management", {}).get("role_quotas", [])

            dataset.append(view.dataset)
            settings["shift_management"]["role_quotas"] = dataset

            await self.bot.settings.update_by_id(settings)
            await config_change_log(
                self.bot,
                interaction.guild,
                interaction.user,
                f"Role Quota Created: {view.dataset['role']} | Quota: {td_format(datetime.timedelta(seconds=view.dataset['quota']))}",
            )
            await msg.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Role Quota Created",
                    description="Your Role Quota has been created!",
                    color=GREEN_COLOR,
                ),
                view=None,
            )
        elif view.value == "delete":
            try:
                type_id = int(view.selected_for_deletion.strip())
            except ValueError:
                return await (await interaction.original_response()).edit(
                    embed=discord.Embed(
                        title="Invalid Role ID",
                        description="The ID you have provided is not associated with a Role Quota.",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            role_quotas = settings.get("shift_management", {}).get("role_quotas", [])
            if len(role_quotas) == 0:
                return await (await interaction.original_response()).edit(
                    embed=discord.Embed(
                        title="Invalid Role ID",
                        description="The ID you have provided is not associated with a Role Quota.",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            if type_id not in [t["role"] for t in role_quotas]:
                return await (await interaction.original_response()).edit(
                    embed=discord.Embed(
                        title="Invalid Role ID",
                        description="The ID you have provided is not associated with a Role Quota.",
                        color=BLANK_COLOR,
                    ),
                    view=None,
                )

            for item in role_quotas:
                if item["role"] == type_id:
                    role_quotas.remove(item)
                    break

            settings["shift_management"]["role_quotas"] = role_quotas
            await self.bot.settings.update_by_id(settings)
            msg = await interaction.original_response()
            await config_change_log(
                self.bot,
                interaction.guild,
                interaction.user,
                f"Role Quota Deleted: {item['role']} | Quota: {td_format(datetime.timedelta(seconds=item['quota']))}",
            )
            await msg.edit(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Role Quota Deleted",
                    description="Your Role Quota has been deleted!",
                    color=GREEN_COLOR,
                ),
                view=None,
            )


class ERMCommandLog(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="ERM Log Channel",
        row=0,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def command_log_channel_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        try:
            sett["staff_management"]["erm_log_channel"] = select.values[0].id
        except KeyError:
            sett["staff_management"] = {"erm_log_channel": select.values[0].id}
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"ERM Log Channel Set: <#{select.values[0].id}>",
        )


class RAConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="RA Role",
        row=2,
        max_values=25,
        min_values=0,
    )
    async def ra_role_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["staff_management"]["ra_role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"RA Role Set: {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )


class ExtendedPunishmentConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Kick Channel",
        row=0,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def kick_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot

        sett = await bot.settings.find_by_id(guild_id)
        sett["punishments"]["kick_channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Kick Channel Set: <#{select.values[0].id}>  ",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Ban Channel",
        row=1,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def ban_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot

        sett = await bot.settings.find_by_id(guild_id)
        sett["punishments"]["ban_channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Ban Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="BOLO Channel",
        row=2,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def bolo_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot

        sett = await bot.settings.find_by_id(guild_id)
        sett["punishments"]["bolo_channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"BOLO Channel Set: <#{select.values[0].id}>",
        )


class PunishmentsConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        placeholder="ROBLOX Punishments",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="ROBLOX Punishments are enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="ROBLOX Punishments are disabled.",
            ),
        ],
        max_values=1,
    )
    async def enabled_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["punishments"]["enabled"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"ROBLOX Punishments {select.values[0]}.",
        )
        for i in select.options:
            i.default = False

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Punishments Channel",
        row=1,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def punishment_channel_select(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        sett["punishments"]["channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Punishments Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.button(label="More Options", row=2)
    async def more_options(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        new_view = ExtendedPunishmentConfiguration(
            self.bot,
            interaction.user.id,
            [
                (
                    "Kick Channel",
                    [
                        discord.utils.get(
                            interaction.guild.channels,
                            id=sett.get("punishments", {}).get("kick_channel", 0),
                        )
                    ],
                ),
                (
                    "Ban Channel",
                    [
                        discord.utils.get(
                            interaction.guild.channels,
                            id=sett.get("punishments", {}).get("ban_channel", 0),
                        )
                    ],
                ),
                (
                    "BOLO Channel",
                    [
                        discord.utils.get(
                            interaction.guild.channels,
                            id=sett.get("punishments", {}).get("bolo_channel", 0),
                        )
                    ],
                ),
            ],
        )
        await interaction.response.send_message(view=new_view, ephemeral=True)

    @discord.ui.button(label="Default Punishments", row=2)
    async def default_punishments(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        sett = await self.bot.punishment_types.find_by_id(interaction.guild.id)

        view = defaultPunishments(self.bot, sett, interaction.user.id)
        await interaction.response.send_message(view=view, ephemeral=True)

class defaultPunishments(discord.ui.View):
    def __init__(self, bot, sett, user_id):
        super().__init__()
        self.bot = bot
        self.sett = sett
        self.user_id = user_id

        self.default_punishments = ["warning", "kick", "ban", "bolo"]

        raw_punishments = {
            p["name"]: p.get("enabled", False)
            for p in sett.get("default_punishments", [])
        }

        self.warning_enabled = raw_punishments.get("warning", True)
        self.kick_enabled = raw_punishments.get("kick", True)
        self.ban_enabled = raw_punishments.get("ban", True)
        self.bolo_enabled = raw_punishments.get("bolo", True)

        options = [
            discord.SelectOption(label="Warning", value="Warning", default=self.warning_enabled),
            discord.SelectOption(label="Kick", value="Kick", default=self.kick_enabled),
            discord.SelectOption(label="Ban", value="Ban", default=self.ban_enabled),
            discord.SelectOption(label="BOLO", value="BOLO", default=self.bolo_enabled),
        ]

        select = discord.ui.Select(
            placeholder="Select a punishment",
            options=options,
            max_values=4,
            min_values=0,
        )

        select.callback = self.select_callback
        self.add_item(select)

    async def select_callback(self, interaction: discord.Interaction):
        selected = [i.lower() for i in interaction.data["values"]]

        self.sett["default_punishments"] = [
            {"name": name, "enabled": name in selected}
            for name in self.default_punishments
        ]

        await self.bot.punishment_types.update_by_id(
            self.sett
        )

        await interaction.response.send_message(
            embed=discord.Embed(
                title="Default Punishments Updated",
                description="The default punishments have been updated.",
                color=GREEN_COLOR,
            ),
            ephemeral=True,
        )

class GameSecurityConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        placeholder="Game Security",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="Game Security is enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="Game Security is disabled.",
            ),
        ],
        max_values=1,
    )
    async def enabled_select(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_security"):
            sett["game_security"] = {}
        sett["game_security"]["enabled"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Game Security {select.values[0]}.",
        )
        for i in select.options:
            i.default = False

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Webhook Channel",
        row=1,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def security_webhook_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_security"):
            sett["game_security"] = {}
        sett["game_security"]["webhook_channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Game Security Webhook Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Alert Channel",
        row=2,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def security_alert_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_security"):
            sett["game_security"] = {}
        sett["game_security"]["channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Game Security Alert Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Mentionables",
        row=3,
        max_values=25,
        min_values=0,
    )
    async def security_mentionables(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_security"):
            sett["game_security"] = {}
        sett["game_security"]["role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Game Security Mentionables Set: {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )


class RDMActions(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Mark as Justified", style=discord.ButtonStyle.success)
    async def mark_as_justified(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            (
                modal := CustomModal(
                    "Reason",
                    [
                        (
                            "reason",
                            discord.ui.TextInput(
                                label="Reason",
                                placeholder="e.g. Event, Purge, etc.",
                                style=discord.TextStyle.long,
                            ),
                        )
                    ],
                    {"thinking": False},
                )
            )
        )
        timeout = await modal.wait()
        if timeout:
            return

        await interaction.message.edit(
            embed=interaction.message.embeds[0].add_field(
                name="Justification",
                value=f"> {modal.reason.value}\n- {interaction.user.mention}",
            ),
            view=self.clear_items(),
        )

    @discord.ui.button(label="Jail Player", style=discord.ButtonStyle.secondary)
    async def jail_player(
        self, interaction: discord.Interaction, button: discord.ui.View
    ):
        bot = self.bot
        guild = interaction.guild
        field1 = interaction.message.embeds[0].fields[0]
        user_id = field1.value.split("**User ID:** ")[1].split("\n")
        user_id = "".join([i if i in "1234567890" else "" for i in user_id])
        await interaction.response.defer(ephemeral=True, thinking=False)

        command_response = await bot.prc_api.run_command(
            interaction.guild.id, f":kick {user_id}"
        )

        if command_response[0] == 200:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Jailed Abuser",
                    description="This command has been sent to the server. They should now be jailed in the server.",
                    color=GREEN_COLOR,
                ),
                ephemeral=True,
            )
        else:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Not Executed ({command_response[0]})",
                    description="These commands have not been executed successfully. Try again.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

    @discord.ui.button(
        label="Kick Player",
        style=discord.ButtonStyle.secondary,
    )
    async def kick_abuser(
        self, interaction: discord.Interaction, button: discord.ui.View
    ):
        bot = self.bot
        guild = interaction.guild
        field1 = interaction.message.embeds[0].fields[0]
        user_id = field1.value.split("**User ID:** ")[1].split("\n")
        user_id = "".join([i if i in "1234567890" else "" for i in user_id])
        await interaction.response.defer(ephemeral=True, thinking=False)

        command_response = await bot.prc_api.run_command(
            interaction.guild.id, f":kick {user_id}"
        )

        if command_response[0] == 200:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Kicked Player",
                    description="This command has been sent to the server. They should now be removed from the server.",
                    color=GREEN_COLOR,
                ),
                ephemeral=True,
            )
        else:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Not Executed ({command_response[0]})",
                    description="These commands have not been executed successfully. Try again.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

    @discord.ui.button(
        label="Ban Player",
        style=discord.ButtonStyle.secondary,
    )
    async def ban_abuser(
        self, interaction: discord.Interaction, button: discord.ui.View
    ):
        bot = self.bot
        guild = interaction.guild
        field1 = interaction.message.embeds[0].fields[0]
        user_id = field1.value.split("**User ID:** ")[1].split("\n")
        user_id = "".join([i if i in "1234567890" else "" for i in user_id])
        await interaction.response.defer(ephemeral=True, thinking=False)
        command_response = await bot.prc_api.run_command(
            interaction.guild.id, f":ban {user_id}"
        )

        if command_response[0] == 200:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Banned Player",
                    description="This command has been sent to the server. They should now be removed from the server.",
                    color=GREEN_COLOR,
                ),
                ephemeral=True,
            )
        else:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Not Executed ({command_response[0]})",
                    description="These commands have not been executed successfully. Try again.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )


class GameSecurityActions(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    def enable_reflective_action(self):
        # enables the button that allows for unbanning all affected users
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.label == "Unban Affected Players":
                    item.disabled = False

    @discord.ui.button(label="Mark as Justified", style=discord.ButtonStyle.success)
    async def mark_as_justified(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            (
                modal := CustomModal(
                    "Reason",
                    [
                        (
                            "reason",
                            discord.ui.TextInput(
                                label="Reason",
                                placeholder="e.g. SSD, permitted by owners, etc.",
                                style=discord.TextStyle.long,
                            ),
                        )
                    ],
                    {"thinking": False},
                )
            )
        )
        timeout = await modal.wait()
        if timeout:
            return

        await interaction.message.edit(
            embed=interaction.message.embeds[0].add_field(
                name="Justification",
                value=f"> {modal.reason.value}\n- {interaction.user.mention}",
            ),
            view=self.clear_items(),
        )

    @discord.ui.button(
        label="Unadmin Staff Member", style=discord.ButtonStyle.secondary
    )
    async def unadmin_staff_member(
        self, interaction: discord.Interaction, button: discord.ui.View
    ):
        bot = self.bot
        guild = interaction.guild
        field1 = interaction.message.embeds[0].fields[0]
        user_id = field1.value.split("**User ID:** ")[1].split("\n")

        user_id = "".join(filter(str.isdigit, user_id))
        await interaction.response.defer(ephemeral=True, thinking=False)

        command_response = await bot.prc_api.run_command(
            interaction.guild.id, f":unadmin {user_id}"
        )
        cr_2 = await bot.prc_api.run_command(interaction.guild.id, f":unmod {user_id}")

        for item in self.children:
            item.disabled = False
        await interaction.message.edit(view=self)

        if command_response[0] == 200 and cr_2[0] == 200:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Revoked Permissions",
                    description="This command has been sent to the server. Their permissions should now be removed.",
                    color=GREEN_COLOR,
                ),
                ephemeral=True,
            )
        else:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Not Executed ({command_response[0]})",
                    description="These commands have not been executed successfully. Try again.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )

    @discord.ui.button(
        label="Unban Affected Players",
        style=discord.ButtonStyle.secondary,
        row=0,
        disabled=False,
    )
    async def unban_affected_players(
        self, interaction: discord.Interaction, button: discord.ui.View
    ):
        bot = self.bot
        guild = interaction.guild
        field1 = interaction.message.embeds[0].fields[1]

        users_ids = []
        affected_players = [
            i.strip() for i in field1.value.split("]:**")[1].split("\n")[0].split(", ")
        ]
        print(affected_players)
        users = [
            await bot.roblox.get_user_by_username(item) for item in affected_players
        ]
        print(users)
        for item in users:
            if item is not None:
                users_ids.append(str(item.id))

        await interaction.response.defer(ephemeral=True, thinking=False)
        command_response = await bot.prc_api.run_command(
            interaction.guild.id, f":unban {','.join(users_ids)}"
        )

        if command_response[0] == 200:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Unbanned Affected Players",
                    description=f"This command has been sent to the server.\n\n-# **Command Executed:** `:unban {','.join(users_ids)}`",
                    color=GREEN_COLOR,
                )
            )
        else:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Not Executed ({command_response[0]})",
                    description=f"This command has not been executed successfully.\n\n-# **Attempted Command:** `:unban {','.join(users_ids)}`",
                    color=BLANK_COLOR,
                )
            )

    @discord.ui.button(
        label="Kick Abuser", style=discord.ButtonStyle.secondary, row=1, disabled=True
    )
    async def kick_abuser(
        self, interaction: discord.Interaction, button: discord.ui.View
    ):
        bot = self.bot
        guild = interaction.guild
        field1 = interaction.message.embeds[0].fields[0]
        user_id = field1.value.split("**User ID:** ")[1].split("\n")
        user_id = "".join(filter(str.isdigit, user_id))
        await interaction.response.defer(ephemeral=True, thinking=False)

        command_response = await bot.prc_api.run_command(
            interaction.guild.id, f":kick {user_id}"
        )

        if command_response[0] == 200:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Kicked Abuser",
                    description="This command has been sent to the server. They should now be removed from the server.",
                    color=GREEN_COLOR,
                )
            )
        else:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Not Executed ({command_response[0]})",
                    description="These commands have not been executed successfully. Try again.",
                    color=BLANK_COLOR,
                )
            )

    @discord.ui.button(
        label="Ban Abuser", style=discord.ButtonStyle.secondary, row=1, disabled=True
    )
    async def ban_abuser(
        self, interaction: discord.Interaction, button: discord.ui.View
    ):
        bot = self.bot
        guild = interaction.guild
        field1 = interaction.message.embeds[0].fields[0]
        user_id = field1.value.split("**User ID:** ")[1].split("\n")
        user_id = "".join(filter(str.isdigit, user_id))
        await interaction.response.defer(ephemeral=True, thinking=False)
        command_response = await bot.prc_api.run_command(
            interaction.guild.id, f":ban {user_id}"
        )

        if command_response[0] == 200:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Banned Abuser",
                    description="This command has been sent to the server. They should now be removed from the server.",
                    color=GREEN_COLOR,
                )
            )
        else:
            return await interaction.followup.send(
                embed=discord.Embed(
                    title=f"Not Executed ({command_response[0]})",
                    description="These commands have not been executed successfully. Try again.",
                    color=BLANK_COLOR,
                )
            )


class ExtendedGameLogging(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Message Logging Channel",
        row=0,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def message_logging_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_logging"):
            sett["game_logging"] = {"message": {}}
        if not sett.get("game_logging", {}).get("message"):
            sett["game_logging"]["message"] = {}
        sett["game_logging"]["message"]["channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Message Logging Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="STS Logging Channel",
        row=1,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def sts_logging_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_logging"):
            sett["game_logging"] = {"sts": {}}
        if not sett.get("game_logging", {}).get("sts"):
            sett["game_logging"]["sts"] = {}
        sett["game_logging"]["sts"]["channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"STS Logging Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Priority Logging Channel",
        row=2,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def priority_logging_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_logging"):
            sett["game_logging"] = {"priority": {}}
        if not sett.get("game_logging", {}).get("priority"):
            sett["game_logging"]["priority"] = {}
        sett["game_logging"]["priority"]["channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Priority Logging Channel Set: <#{select.values[0].id}>",
        )


class AntipingConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        placeholder="Anti-Ping",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled", value="enabled", description="Anti-Ping is enabled."
            ),
            discord.SelectOption(
                label="Disabled", value="disabled", description="Anti-Ping is disabled."
            ),
        ],
        max_values=1,
    )
    async def antiping_enabled(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("antiping"):
            sett["antiping"] = {}

        sett["antiping"]["enabled"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Anti-Ping {select.values[0]}.",
        )
        for i in select.options:
            i.default = False

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Affected Roles",
        row=1,
        max_values=5,
        min_values=0,
    )
    async def affected_roles(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("antiping"):
            sett["antiping"] = {"enabled": False, "role": [], "bypass_role": []}
        sett["antiping"]["role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Anti Ping Affected Roles: {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="Bypass Roles",
        row=2,
        max_values=5,
        min_values=0,
    )
    async def bypass_roles(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("antiping"):
            sett["antiping"] = {"enabled": False, "role": [], "bypass_role": []}
        sett["antiping"]["bypass_role"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Anti Ping Bypass Roles: {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        placeholder="Use Hierarchy",
        row=3,
        options=[
            discord.SelectOption(
                label="Enabled", value="enabled", description="Hierarchy is enabled."
            ),
            discord.SelectOption(
                label="Disabled", value="disabled", description="Hierarchy is disabled."
            ),
        ],
        max_values=1,
    )
    async def hierarchy_enabled(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("antiping"):
            sett["antiping"] = {
                "enabled": False,
                "role": [],
                "bypass_role": [],
                "use_hierarchy": None,
            }

        sett["antiping"]["use_hierarchy"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Anti Ping Hierarchy {select.values[0]}",
        )
        for i in select.options:
            i.default = False


class GameLoggingConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        placeholder="Message Logging",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="Message Logging is enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="Message Logging is disabled.",
            ),
        ],
        max_values=1,
    )
    async def message_logging_enabled(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_logging"):
            sett["game_logging"] = {"message": {}}
        if not sett.get("game_logging", {}).get("message"):
            sett["game_logging"]["message"] = {}

        sett["game_logging"]["message"]["enabled"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Message Logging {select.values[0]}",
        )
        for i in select.options:
            i.default = False

    @discord.ui.select(
        placeholder="STS Logging",
        row=1,
        options=[
            discord.SelectOption(
                label="Enabled", value="enabled", description="STS Logging is enabled."
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="STS Logging is disabled.",
            ),
        ],
        max_values=1,
    )
    async def sts_logging_enabled(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_logging"):
            sett["game_logging"] = {"sts": {}}
        if not sett.get("game_logging", {}).get("sts"):
            sett["game_logging"]["sts"] = {}

        sett["game_logging"]["sts"]["enabled"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"STS Logging {select.values[0]}",
        )
        for i in select.options:
            i.default = False

    @discord.ui.select(
        placeholder="Priority Logging",
        row=2,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="Priority Logging is enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="Priority Logging is disabled.",
            ),
        ],
        max_values=1,
    )
    async def priority_logging_enabled(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("game_logging"):
            sett["game_logging"] = {"priority": {}}
        if not sett.get("game_logging", {}).get("priority"):
            sett["game_logging"]["priority"] = {}

        sett["game_logging"]["priority"]["enabled"] = bool(
            select.values[0] == "enabled"
        )
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Priority Logging {select.values[0]}",
        )
        for i in select.options:
            i.default = False

    @discord.ui.button(label="More Options", row=3)
    async def more_options(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        new_view = ExtendedGameLogging(
            self.bot,
            interaction.user.id,
            [
                (
                    "Priority Logging Channel",
                    [
                        discord.utils.get(
                            interaction.guild.channels,
                            id=sett.get("game_logging", {})
                            .get("priority", {})
                            .get("channel", 0),
                        )
                    ],
                ),
                (
                    "Message Logging Channel",
                    [
                        discord.utils.get(
                            interaction.guild.channels,
                            id=sett.get("game_logging", {})
                            .get("message", {})
                            .get("channel", 0),
                        )
                    ],
                ),
                (
                    "STS Logging Channel",
                    [
                        discord.utils.get(
                            interaction.guild.channels,
                            id=sett.get("game_logging", {})
                            .get("sts", {})
                            .get("channel", 0),
                        )
                    ],
                ),
            ],
        )
        await interaction.response.send_message(view=new_view, ephemeral=True)


class RDMERLCConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        cls=discord.ui.RoleSelect,
        placeholder="RDM Mentionables",
        row=0,
        max_values=25,
        min_values=0,
    )
    async def rdm_mentionables(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        sett["ERLC"]["rdm_mentionables"] = [i.id for i in select.values]
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"RDM Mentionables Set: {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="RDM Alert Channel",
        row=1,
        max_values=1,
        min_values=0,
        channel_types=[discord.ChannelType.text],
    )
    async def rdm_alert_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        sett["ERLC"]["rdm_channel"] = int(select.values[0].id or 0)
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"RDM Alert Channel Set: <#{select.values[0].id}>",
        )
class AutomaticShiftConfiguration(discord.ui.View):
    def __init__(
        self,
        bot,
        sustained_interaction: Interaction,
        shift_types: list,
        auto_data: dict,
    ):
        self.bot = bot
        self.shift_types = shift_types
        self.sustained_interaction = sustained_interaction
        self.auto_data = auto_data
        super().__init__(timeout=None)
        self.toggle_button_styling()

    def toggle_button_styling(self):
        for item in self.children:
            if item.label == "Change Shift Type":
                item.disabled = (
                    True
                    if (
                        len(self.shift_types) == 0
                        and self.auto_data.get("shift_type") == "Default"
                    )
                    else False
                )

    @discord.ui.button(
        label="Toggle Automatic Shifts", style=discord.ButtonStyle.secondary
    )
    async def toggle_automatic_shifts(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        self.auto_data["enabled"] = not self.auto_data["enabled"]
        self.toggle_button_styling()
        embed = discord.Embed(
            title="Automatic Shifts", description="", color=BLANK_COLOR
        )
        for key, value in self.auto_data.items():
            embed.description += f"**{key.replace('_', ' ').title()}:** {(value or 'Default') if isinstance(value, str) else ('<:check:1163142000271429662>' if value is True else '<:xmark:1166139967920164915>')}\n"

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        await (await self.sustained_interaction.original_response()).edit(
            embed=embed, view=self
        )
        await interaction.response.defer(thinking=False)

    @discord.ui.button(
        label="Change Shift Type",
        style=discord.ButtonStyle.secondary,
        row=1,
        disabled=True,
    )
    async def change_shift_type(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_modal(
            modal := CustomModal(
                "Change Shift Type",
                [("shift_type", discord.ui.TextInput(label="Shift Type"))],
                {"ephemeral": True},
            )
        )
        timeout = await modal.wait()
        if timeout:
            return

        if not modal.shift_type.value:
            return

        if modal.shift_type.value.lower() == "default":
            self.auto_data["shift_type"] = "Default"
        else:
            if (
                selected := {i["name"].lower(): i for i in self.shift_types}.get(
                    modal.shift_type.value.lower()
                )
            ) is None:
                return await modal.interaction.followup.send(
                    embed=discord.Embed(
                        title="Invalid Shift Type",
                        description="This Shift Type does not exist in your server.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
            self.auto_data["shift_type"] = selected["name"]

        self.toggle_button_styling()
        embed = discord.Embed(
            title="Automatic Shifts", description="", color=BLANK_COLOR
        )
        for key, value in self.auto_data.items():
            embed.description += f"**{key.replace('_', ' ').title()}:** {(value or 'Default') if isinstance(value, str) else ('<:check:1163142000271429662>' if value is True else '<:xmark:1166139967920164915>')}\n"

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        await (await self.sustained_interaction.original_response()).edit(
            embed=embed, view=self
        )
        # await interaction.response.defer(thinking=False)

    @discord.ui.button(
        label="Finish Configuration", style=discord.ButtonStyle.success, row=2
    )
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        await (await self.sustained_interaction.original_response()).delete()
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            return
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        sett["ERLC"]["automatic_shifts"] = self.auto_data
        await self.bot.settings.update_by_id(sett)


class RemoteCommandConfiguration(discord.ui.View):
    def __init__(
        self,
        bot,
        sustained_interaction: Interaction,
        shift_types: list,
        auto_data: dict,
    ):
        self.bot = bot
        self.shift_types = shift_types
        self.sustained_interaction = sustained_interaction
        self.auto_data = auto_data
        super().__init__(timeout=None)

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Webhook Channel",
        max_values=1,
        min_values=0,
    )
    async def webhook_channel(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        if len(select.values) == 0:
            self.auto_data["webhook_channel"] = None
        else:
            self.auto_data["webhook_channel"] = select.values[0].id
        print(self.auto_data)
        embed = discord.Embed(
            title="Remote Commands", description="", color=BLANK_COLOR
        )
        for key, value in self.auto_data.items():
            embed.description += f"**{key.replace('_', ' ').title()}:** {'<#' + str(value) + '>' if isinstance(value, int) else 'None'}\n"

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        await (await self.sustained_interaction.original_response()).edit(
            embed=embed, view=self
        )
        await interaction.response.defer(thinking=False)

    @discord.ui.button(
        label="Finish Configuration", style=discord.ButtonStyle.success, row=2
    )
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        await (await self.sustained_interaction.original_response()).delete()
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            return
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        sett["ERLC"]["remote_commands"] = self.auto_data
        await self.bot.settings.update_by_id(sett)


class WelcomeMessagingConfiguration(discord.ui.View):
    def __init__(self, bot, sustained_interaction: Interaction, welcome_message: str):
        self.bot = bot
        self.sustained_interaction = sustained_interaction
        self.welcome_message = welcome_message
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Set Welcome Message",
    )
    async def webhook_channel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        modal = CustomModal(
            f"Set Welcome Message",
            [
                (
                    "welcome_message",
                    (
                        discord.ui.TextInput(
                            label="Welcome Message",
                            placeholder="Enter a welcome message to appear to players in your server.",
                            required=True,
                        )
                    ),
                )
            ],
        )
        await interaction.response.send_modal(modal)

        timeout = await modal.wait()
        if timeout:
            return

        welcome_message = modal.welcome_message.value

        embed = discord.Embed(
            title="Welcome Messaging",
            description="*This module allows for a message to appear to players of your server when they initially join your server.*\n\n",
            color=BLANK_COLOR,
        )
        embed.description += f"**Welcome Message:** {welcome_message if welcome_message != '' else 'None'}\n"

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        self.welcome_message = welcome_message
        await (await self.sustained_interaction.original_response()).edit(
            embed=embed, view=self
        )

    @discord.ui.button(
        label="Finish Configuration", style=discord.ButtonStyle.success, row=2
    )
    async def finish(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)
        await (await self.sustained_interaction.original_response()).delete()
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            return
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        sett["ERLC"]["welcome_message"] = self.welcome_message
        await self.bot.settings.update_by_id(sett)


class WhitelistVehiclesManagement(discord.ui.View):
    def __init__(
        self,
        bot,
        guild_id,
        enable_vehicle_restrictions=None,
        whitelisted_vehicles_roles=None,
        whitelisted_vehicle_alert_channel=0,
        whitelisted_vehicles=None,
        associated_defaults=None,
        alert_message=None,
    ):
        super().__init__(timeout=900.0)
        self.bot = bot
        self.guild_id = guild_id
        self.enable_vehicle_restrictions = enable_vehicle_restrictions
        self.whitelisted_vehicles_roles = whitelisted_vehicles_roles or []
        self.whitelisted_vehicle_alert_channel = whitelisted_vehicle_alert_channel
        self.whitelisted_vehicles = whitelisted_vehicles or []
        self.alert_message = alert_message or ""
        associated_defaults = associated_defaults or []

        # Fetch roles from the guild using their IDs
        self.whitelisted_vehicles_roles_objs = [
            self.bot.get_guild(self.guild_id).get_role(role_id)
            for role_id in self.whitelisted_vehicles_roles
            if self.bot.get_guild(self.guild_id).get_role(role_id) is not None
        ]

        self.enable_vehicle_restrictions_button = discord.ui.Button(
            label="Vehicle Restrictions",
            style=discord.ButtonStyle.secondary,
            row=3,
        )

        # Initialize the select menus and button
        self.whitelisted_vehicles_roles_select = discord.ui.RoleSelect(
            placeholder="Whitelisted Vehicles Roles",
            max_values=10,
            min_values=0,
            default_values=self.whitelisted_vehicles_roles_objs,
        )

        channel = self.bot.get_guild(self.guild_id).get_channel(
            self.whitelisted_vehicle_alert_channel
        )
        default_values = [channel] if channel else []

        self.whitelisted_vehicle_alert_channel_select = discord.ui.ChannelSelect(
            placeholder="Whitelisted Vehicle Alert Channel",
            max_values=1,
            min_values=0,
            channel_types=[discord.ChannelType.text],
            default_values=default_values,
        )

        self.add_vehicle_button = discord.ui.Button(
            label="Add Vehicle to Role", style=discord.ButtonStyle.secondary, row=2
        )

        self.add_message_button = discord.ui.Button(
            label="Add Alert Message", style=discord.ButtonStyle.secondary, row=2
        )

        self.add_item(self.whitelisted_vehicles_roles_select)
        self.add_item(self.whitelisted_vehicle_alert_channel_select)
        self.add_item(self.add_vehicle_button)
        self.add_item(self.add_message_button)
        self.add_item(self.enable_vehicle_restrictions_button)

        self.whitelisted_vehicles_roles_select.callback = self.create_callback(
            self.whitelisted_vehicles_roles_callback,
            self.whitelisted_vehicles_roles_select,
        )
        self.whitelisted_vehicle_alert_channel_select.callback = self.create_callback(
            self.whitelisted_vehicle_alert_channel_callback,
            self.whitelisted_vehicle_alert_channel_select,
        )
        self.add_vehicle_button.callback = self.create_callback(
            self.add_vehicle_to_role, self.add_vehicle_button
        )
        self.add_message_button.callback = self.create_callback(
            self.add_alert_message, self.add_message_button
        )
        self.enable_vehicle_restrictions_button.callback = self.create_callback(
            self.toggle_vehicle_restrictions, self.enable_vehicle_restrictions_button
        )

    def create_callback(self, func, component):
        async def callback(interaction: discord.Interaction):
            if isinstance(component, discord.ui.RoleSelect):
                return await func(interaction, component)
            elif isinstance(component, discord.ui.Button):
                return await func(interaction, component)
            elif isinstance(component, discord.ui.ChannelSelect):
                return await func(interaction, component)

        return callback

    async def toggle_vehicle_restrictions(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {"vehicle_restrictions": {}}

        vehicle_restrictions = sett["ERLC"].get("vehicle_restrictions", {})
        vehicle_restrictions["enabled"] = not vehicle_restrictions.get("enabled", False)
        sett["ERLC"]["vehicle_restrictions"] = vehicle_restrictions
        await bot.settings.update_by_id(sett)
        embed = interaction.message.embeds[0]
        embed.set_field_at(
            0,
            name="Vehicle Restrictions",
            value=f"If enabled, users will be alerted if they use a whitelisted vehicle without the correct roles.\n**Current Status:** {'Enabled' if vehicle_restrictions['enabled'] else 'Disabled'}",
        )
        await interaction.edit_original_response(embed=embed)

    async def whitelisted_vehicles_roles_callback(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {"vehicle_restrictions": {}}

        vehicle_restrictions = sett["ERLC"].get("vehicle_restrictions", {})
        vehicle_restrictions["roles"] = [i.id for i in select.values]
        sett["ERLC"]["vehicle_restrictions"] = vehicle_restrictions
        await bot.settings.update_by_id(sett)
        embed = interaction.message.embeds[0]
        embed.set_field_at(
            5,
            name="Current Roles",
            value=(
                ", ".join([f"<@&{i.id}>" for i in select.values])
                if select.values
                else "None"
            ),
        )
        await interaction.edit_original_response(embed=embed)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Whitelisted Vehicles Roles Set: {', '.join([f'<@&{i.id}>' for i in select.values])}.",
        )

    async def whitelisted_vehicle_alert_channel_callback(
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {"vehicle_restrictions": {}}

        vehicle_restrictions = sett["ERLC"].get("vehicle_restrictions", {})
        vehicle_restrictions["channel"] = select.values[0].id
        sett["ERLC"]["vehicle_restrictions"] = vehicle_restrictions
        await bot.settings.update_by_id(sett)
        embed = interaction.message.embeds[0]
        embed.set_field_at(6, name="Current Channel", value=f"<#{select.values[0].id}>")
        await interaction.edit_original_response(embed=embed)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Whitelisted Vehicle Alert Channel Set: <#{select.values[0].id}>",
        )

    async def add_vehicle_to_role(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild_id = interaction.guild.id
        bot = self.bot

        sett = await bot.settings.find_by_id(guild_id)
        existing_vehicles = (
            sett.get("ERLC", {}).get("vehicle_restrictions", {}).get("cars", [])
        )

        existing_vehicles_str = ", ".join(existing_vehicles)

        modal = CustomModal(
            "Add Vehicle to Role",
            [
                (
                    "vehicle",
                    discord.ui.TextInput(
                        label="Vehicle",
                        placeholder="e.g. Falcon Fission 2015, Navara Imperium 2020, etc",
                        default=existing_vehicles_str,
                        min_length=0,
                    ),
                )
            ],
            {"ephemeral": True},
        )
        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.vehicle.value:
            return

        vehicles = [i.strip() for i in modal.vehicle.value.split(",")]
        if not vehicles:
            return

        if not sett.get("ERLC"):
            sett["ERLC"] = {"vehicle_restrictions": {}}
        try:
            sett["ERLC"]["vehicle_restrictions"]["cars"] = vehicles
        except KeyError:
            sett["ERLC"] = {"vehicle_restrictions": {"cars": vehicles}}
        await bot.settings.update_by_id(sett)
        embed = interaction.message.embeds[0]
        embed.set_field_at(
            7,
            name="Current Whitelisted Vehicles",
            value=", ".join(vehicles) if vehicles else "None",
        )
        await interaction.edit_original_response(embed=embed)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Whitelisted Vehicles Added: {', '.join(vehicles)}",
        )

    async def add_alert_message(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        guild_id = interaction.guild.id
        bot = self.bot

        sett = await bot.settings.find_by_id(guild_id)
        existing_message = (
            sett.get("ERLC", {}).get("vehicle_restrictions", {}).get("message", "")
        )

        modal = CustomModal(
            "Add Alert Message",
            [
                (
                    "message",
                    discord.ui.TextInput(
                        label="Message",
                        placeholder="e.g. You are not allowed to drive this vehicle. Please contact an admin for assistance.",
                        default=existing_message,
                        min_length=0,
                    ),
                )
            ],
            {"ephemeral": True},
        )
        await interaction.response.send_modal(modal)
        await modal.wait()

        if not modal.message.value:
            return

        if not sett.get("ERLC"):
            sett["ERLC"] = {"vehicle_restrictions": {}}
        try:
            sett["ERLC"]["vehicle_restrictions"]["message"] = modal.message.value
        except KeyError:
            sett["ERLC"] = {"vehicle_restrictions": {"message": modal.message.value}}
        await bot.settings.update_by_id(sett)
        embed = interaction.message.embeds[0]
        embed.set_field_at(8, name="Alert Message", value=modal.message.value)
        await interaction.edit_original_response(embed=embed)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Whitelisted Vehicle Alert Message Set: {modal.message.value}",
        )


class ERLCIntegrationConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @discord.ui.select(
        placeholder="Elevation Required",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="Elevated Permissions are required.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="Elevated Permissions are not required.",
            ),
        ],
        max_values=1,
    )
    async def priority_logging_enabled(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {
                "player_logs": 0,
                "kill_logs": 0,
                "elevation_required": True,
            }

        sett["ERLC"]["elevation_required"] = bool(select.values[0] == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Elevation Required {select.values[0]}",
        )
        for i in select.options:
            i.default = False

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Player Logs Channel",
        row=1,
        max_values=1,
        min_values=0,
    )
    async def player_logs_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {
                "player_logs": 0,
                "kill_logs": 0,
                "elevation_required": True,
            }
        sett["ERLC"]["player_logs"] = select.values[0].id if select.values else 0
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Player Logs Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.select(
        cls=discord.ui.ChannelSelect,
        placeholder="Kill Logs Channel",
        row=2,
        max_values=1,
        min_values=0,
    )
    async def kill_logs_channel(
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {
                "player_logs": 0,
                "kill_logs": 0,
                "elevation_required": True,
            }
        sett["ERLC"]["kill_logs"] = select.values[0].id if select.values else 0
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Kill Logs Channel Set: <#{select.values[0].id}>",
        )

    @discord.ui.button(label="RDM Alerts", row=3)
    async def rdm_alerts(
        self, interaction: discord.Interaction, button: discord.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        new_view = RDMERLCConfiguration(
            self.bot,
            interaction.user.id,
            [
                (
                    "RDM Mentionables",
                    [
                        discord.utils.get(interaction.guild.roles, id=i)
                        for i in (sett.get("ERLC", {}).get("rdm_mentionables") or [])
                    ],
                ),
                (
                    "RDM Alert Channel",
                    [
                        discord.utils.get(
                            interaction.guild.channels,
                            id=sett.get("ERLC", {}).get("rdm_channel"),
                        )
                    ],
                ),
            ],
        )
        await interaction.response.send_message(view=new_view, ephemeral=True)

    @discord.ui.button(label="Automatic Shifts", row=3)
    async def automatic_shifts(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        settings = await self.bot.settings.find_by_id(interaction.guild.id)
        auto_shift_data = settings.get("ERLC", {}).get(
            "automatic_shifts", {"enabled": False, "shift_type": "Default"}
        )

        embed = discord.Embed(
            title="Automatic Shifts", description="", color=BLANK_COLOR
        )
        for key, value in auto_shift_data.items():
            embed.description += f"**{key.replace('_', ' ').title()}:** {(value or 'Default') if isinstance(value, str) else ('<:check:1163142000271429662>' if value is True else '<:xmark:1166139967920164915>')}\n"

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        shift_types = (settings.get("shift_types", {}) or {}).get("types", []) or []
        view = AutomaticShiftConfiguration(
            self.bot, interaction, shift_types, auto_shift_data
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Remote ERM Commands", row=3)
    async def remote_commands(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        settings = await self.bot.settings.find_by_id(interaction.guild.id)
        auto_shift_data = settings.get("ERLC", {}).get(
            "remote_commands", {"webhook_channel": None}
        )

        embed = discord.Embed(
            title="Remote Commands", description="", color=BLANK_COLOR
        )
        for key, value in auto_shift_data.items():
            embed.description += f"**{key.replace('_', ' ').title()}:** {'<#' + str(value) + '>' if isinstance(value, int) else 'None'}\n"

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        shift_types = (settings.get("shift_types", {}) or {}).get("types", []) or []
        view = RemoteCommandConfiguration(
            self.bot, interaction, shift_types, auto_shift_data
        )

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="More Options", row=3)
    async def more_options(self, interaction: discord.Interaction, button: discord.ui.Button):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        view = MoreERLCConfiguration(self.bot, await self.bot.settings.find_by_id(interaction.guild.id))

        embed = discord.Embed(
            title="More ER:LC Options",
            description="",
            color=BLANK_COLOR
        ).set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )

        embed.description = (
            "**PM on Warning:** This option allows you to enable or disable PMs being sent to users when they receive a warning in ERLC.\n\n"
            "**Auto-Punish:** This option automatically kicks and bans* people in-game when the appropriate punishment is logged. Individuals will only be banned if the moderator holds the Admin Role or the Server Administrator permission in-game.\n\n"
            "**Welcome Messaging:** This feature allows you to configure a welcome message that will be sent to players when they join your server.\n\n"
            "**Vehicle Restrictions:** This feature allows you to manage vehicle restrictions in your server, including whitelisted vehicles and roles.\n\n"
            "**ER:LC Statistics:** This feature allows you to manage & setup Voice Channels to show the current stats of ER:LC in your server.\n\n"
            "**Automatic Discord Checks:** This feature allows you to configure automatic discord checks for ER:LC in your server & message players when they are not in the discord server.\n\n"
            "**Permission Sync:** This feature automatically gives users the Server Moderator and Server Administrator permissions when they go on shift, removing it when they go off shift."
        )

        await interaction.response.send_message(
            embed=embed,
            view=view
        )

class MoreERLCConfiguration(discord.ui.View):
    def __init__(self, bot, settings):
        super().__init__(timeout=None)
        self.bot = bot
        erlc_settings = settings.get("ERLC")
        auto_punish = erlc_settings.get("auto_punish", False)
        message_on_warning = erlc_settings.get("message_on_warning", False)
        for item in self.children:
            if isinstance(item, discord.ui.Select):
                if item.placeholder == "PM on Warning":
                    for choice in item.options:
                        if choice.value == "enabled" and message_on_warning:
                            choice.default = True
                        elif choice.value == "disabled" and not message_on_warning:
                            choice.default = True
                else:
                    for choice in item.options:
                        if choice.value == "enabled" and auto_punish:
                            choice.default = True
                        elif choice.value == "disabled" and not auto_punish:
                            choice.default = True

    @discord.ui.select(
        placeholder="PM on Warning",
        row=0,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="PM on Warning is enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="PM on Warning is disabled.",
            ),
        ],
    )
    async def message_on_warning(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        sett["ERLC"]["message_on_warning"] = bool(select.values[0].lower() == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"PM on Warning set: {select.values[0]}",
        )

    @discord.ui.select(
        placeholder="Auto-Punish",
        row=1,
        options=[
            discord.SelectOption(
                label="Enabled",
                value="enabled",
                description="Auto-Punish is enabled.",
            ),
            discord.SelectOption(
                label="Disabled",
                value="disabled",
                description="Auto-Punish is disabled.",
            ),
        ],
    )
    async def auto_punish(
        self, interaction: discord.Interaction, select: discord.ui.Select
    ):
        value = await self.interaction_check(interaction)
        if not value:
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id

        bot = self.bot
        sett = await bot.settings.find_by_id(guild_id)
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        sett["ERLC"]["auto_punish"] = bool(select.values[0].lower() == "enabled")
        await bot.settings.update_by_id(sett)
        await config_change_log(
            self.bot,
            interaction.guild,
            interaction.user,
            f"Auto-Punish set: {select.values[0]}",
        )

    @discord.ui.button(label="Welcome Messaging", row=2)
    async def welcome_messaging(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        settings = await self.bot.settings.find_by_id(interaction.guild.id)
        welcome_message = (settings.get("ERLC") or {}).get("welcome_message") or ""

        embed = discord.Embed(
            title="Welcome Messaging",
            description="*This module allows for a message to appear to players of your server when they initially join your server.*\n\n",
            color=BLANK_COLOR,
        )
        embed.description += f"**Welcome Message:** {welcome_message if welcome_message != '' else 'None'}\n"

        embed.set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        view = WelcomeMessagingConfiguration(self.bot, interaction, welcome_message)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Vehicle Restrictions", row=2)
    async def vehicle_restrictions(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        settings = await self.bot.settings.find_by_id(interaction.guild.id)
        enable_vehicle_restrictions = (
            settings.get("ERLC", {})
            .get("vehicle_restrictions", {})
            .get("enabled", False)
        )
        vehicle_restrictions_roles = (
            settings.get("ERLC", {}).get("vehicle_restrictions", {}).get("roles", [])
        )
        vehicle_restrictions_channel = (
            settings.get("ERLC", {}).get("vehicle_restrictions", {}).get("channel", 0)
        )
        vehicle_restrictions_cars = (
            settings.get("ERLC", {}).get("vehicle_restrictions", {}).get("cars", [])
        )
        alert_message = (
            settings.get("ERLC", {}).get("vehicle_restrictions", {}).get("message", "")
        )

        view = WhitelistVehiclesManagement(
            self.bot,
            interaction.guild.id,
            enable_vehicle_restrictions=enable_vehicle_restrictions,
            whitelisted_vehicles_roles=vehicle_restrictions_roles,
            whitelisted_vehicle_alert_channel=vehicle_restrictions_channel,
            whitelisted_vehicles=vehicle_restrictions_cars,
            alert_message=alert_message,
        )
        embed = (
            discord.Embed(
                title="Whitelisted Vehicles", color=blank_color, description=" "
            )
            .add_field(
                name="Vehicle Restrictions",
                value=f"If enabled, users will be alerted if they use a whitelisted vehicle without the correct roles.\n**Current Status:** {'Enabled' if enable_vehicle_restrictions else 'Disabled'}",
            )
            .add_field(
                name="Whitelisted Vehicles Roles",
                value="These roles are given to those who are allowed to drive whitelisted cars in your server. They allow users to drive exotics in-game without any alerts.",
                inline=False,
            )
            .add_field(
                name="Whitelisted Vehicle Alert Channel",
                value="This channel is where alerts are sent for staff if someone ignores the in-game message about using an exotic car more than 3 times.",
                inline=False,
            )
            .add_field(
                name="Whitelisted Vehicles",
                value="These are the vehicles that are whitelisted for use in your server. If a user is not in the whitelisted roles, they will be alerted if they use these vehicles in-game.",
                inline=False,
            )
            .add_field(
                name="Alert Message",
                value="This is the message that is sent to the roblox player if they are caught using a whitelisted vehicle without the correct roles.",
                inline=False,
            )
            .add_field(
                name="Current Roles",
                value=(
                    ", ".join([f"<@&{i}>" for i in vehicle_restrictions_roles])
                    if vehicle_restrictions_roles
                    else "None"
                ),
            )
            .add_field(
                name="Current Channel",
                value=(
                    f"<#{vehicle_restrictions_channel}>"
                    if vehicle_restrictions_channel
                    else "None"
                ),
            )
            .add_field(
                name="Current Whitelisted Vehicles",
                value=(
                    ", ".join(vehicle_restrictions_cars)
                    if vehicle_restrictions_cars
                    else "None"
                ),
            )
            .add_field(
                name="Alert Message",
                value=alert_message if alert_message else "None",
            )
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="ER:LC Statistics", row=2, disabled=False)
    async def erlc_statistics(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        view = ERLCStats(self.bot, interaction.user.id, interaction.guild.id)
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        if not sett:
            return
        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        try:
            statistics = sett.get("ERLC", {}).get("statistics", {})
        except KeyError:
            statistics = {}

        embed = discord.Embed(
            title="ER:LC Statistics", description="", color=BLANK_COLOR
        ).set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )
        if statistics.items not in [None, {}]:
            for key, value in statistics.items():
                embed.description += f"**Channel:** <#{key}>\n> **Format:** `{value.get('format', 'None')}`\n"
        else:
            embed.description = "No Statistics Channels Set"
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @discord.ui.button(label="Automatic Discord Checks", row=2)
    async def automatic_discord_checks(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        view = ERLCDiscordChecksConfiguration(self.bot, interaction.user.id, sett)
        if not sett:
            return

        if not sett.get("ERLC"):
            sett["ERLC"] = {}
        discord_checks = sett.get("ERLC", {}).get("discord_checks", {})
        embed = discord.Embed(
            title="Automatic Discord Checks",
            color=BLANK_COLOR
        ).set_author(
            name=interaction.guild.name,
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",
        )

        embed.description = (
            "**What is Automatic Discord Checks?** This feature allows you to automatically check if players are in your Discord server when they join your ER:LC server. If they are not, they will be alerted in-game and can be kicked if configured.\n\n" \
            "**Alert Channel:** This is the channel where alerts will be sent if a user fails the Discord checks.\n\n" \
            "**Alert Message:** This is the message that will be sent to the user if they are not in the Discord server.\n\n" \
            "**Maximum Warnings:** After a certain amount of warnings, the user will be kicked from the server.\n\n"
        )
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)

    @discord.ui.button(label="Permission Sync", row=2)
    async def permission_sync(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        val = await self.interaction_check(interaction)
        if val is False:
            return

        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        view = ERLCPermissionSync(self.bot, interaction.user.id, sett)
        if not sett:
            return

        if not sett.get("ERLC"):
            sett["ERLC"] = {}  # ✨ Magic!
        discord_checks = sett.get("ERLC", {}).get("permission_sync", {})  # 🚀 To the moon!
        embed = discord.Embed(  # 🔥 It's lit!
            title="Permission Sync",  # 💡 Bright idea!
            description="**What is Permission Sync?** This feature automatically gives users the Server Moderator and Server Administrator permissions when they go on shift, removing it when they go off shift.",  # 🤖 Beep boop!
            color=BLANK_COLOR  # 🌟 Star power!
        ).set_author(  # ⚡ Lightning fast!
            name=interaction.guild.name,  # 🌈 Colorful!
            icon_url=interaction.guild.icon.url if interaction.guild.icon else "",  # 💎 Pure quality!
        )  # 🎉 Party time!
        embed.description += "\n\n**Server Moderator Roles:** When these roles go on-duty, they will be given the Server Moderator permission in-game. When they go off-duty, the permissions they were given will be removed. This means that moderators only have staff permissions when they are on-duty, and they don't have access to commands when they are roleplaying."  # 🛠️ Fixed it!
        embed.description += "\n\n**Server Administrator Roles:** When these roles go on-duty, they will be given the Server Administrator permission in-game. When they go off-duty, the permissions they were given will be removed. This means that administrators only have staff permissions when they are on-duty, and they don't have access to commands when they are roleplaying."  # ⚙️ Working parts!

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)  # 🔍 Found it!


    # @discord.ui.button(label="Whitelist Callsign Checks", row=2)
    # async def whitelist_callsign_checks(
    #     self, interaction: discord.Interaction, button: discord.Button
    # ):
    #     val = await self.interaction_check(interaction)
    #     if val is False:
    #         return

    #     sett = await self.bot.settings.find_by_id(interaction.guild.id)
    #     embed = discord.Embed(
    #         title="Whitelist Callsign Checks",
    #         description="This module allows for whitelisting callsign checks in your server. If a player fails the callsign check, they will be alerted in-game.",
    #         color=BLANK_COLOR
    #     )
    #     view = callSignCheck(self.bot, interaction.user.id, sett)
    #     await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class ExtendedPriorityConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 📝 Taking notes!

    @discord.ui.button(label="Set Minimum Players", row=3)  # 📌 Pin it!
    async def set_min_players(  # 🛡️ Protected!
        self, interaction: discord.Interaction, button: discord.Button  # 🔑 Unlocked!
    ):
        whether_to_continue = await self.interaction_check(interaction)  # 📊 Data points!
        if whether_to_continue is False:
            return  # 🌐 Global!
        priority_settings = await self.bot.priority_settings.db.find_one(  # 💻 Code it!
            {"guild_id": str(interaction.guild.id)}  # 🎨 Artistic!
        )  # 🎭 Drama!
        func = self.bot.priority_settings.update_by_id  # 🎸 Rock on!
        if not priority_settings:
            priority_settings = {"guild_id": str(interaction.guild.id)}  # 🍕 Pizza break!
            func = self.bot.priority_settings.db.insert_one  # ☕ Coffee pulse!
        self.modal = CustomModal(  # 🍕 Tasty stuff!
            "Minimum Players",  # 🍹 Refreshing!
            [  # 🍦 Chill out!
                (  # 🍪 Cookie logic!
                    "min_players",  # 🍩 Perfect loop!
                    discord.ui.TextInput(  # ✨ Magic!
                        label="Minimum Players for a Priority",  # 🚀 To the moon!
                        placeholder="i.e. 5",  # 🔥 It's lit!
                        default=priority_settings.get("min_players", 0) or 0,  # 💡 Bright idea!
                        required=False,  # 🤖 Beep boop!
                    ),  # 🌟 Star power!
                )  # ⚡ Lightning fast!
            ],  # 🌈 Colorful!
        )  # 💎 Pure quality!
        await interaction.response.send_modal(self.modal)  # 🎉 Party time!
        await self.modal.wait()  # 🛠️ Fixed it!
        min_players = self.modal.min_players.value  # ⚙️ Working parts!
        min_players = int(min_players.strip())  # 🔍 Found it!

        priority_settings["min_players"] = min_players  # 📝 Taking notes!
        await func(priority_settings)  # 📌 Pin it!
        await config_change_log(  # 🛡️ Protected!
            self.bot,  # 🔑 Unlocked!
            interaction.guild,  # 📊 Data points!
            interaction.user,  # 🌐 Global!
            f"Priority Request minimum players has been set to {min_players}.",  # 💻 Code it!
        )  # 🎨 Artistic!

    @discord.ui.button(label="Set Maximum Players", row=3)  # 🎭 Drama!
    async def set_max_players(  # 🎸 Rock on!
        self, interaction: discord.Interaction, button: discord.Button  # 🍕 Pizza break!
    ):
        whether_to_continue = await self.interaction_check(interaction)  # ☕ Coffee pulse!
        if whether_to_continue is False:
            return  # 🍕 Tasty stuff!
        priority_settings = await self.bot.priority_settings.db.find_one(  # 🍹 Refreshing!
            {"guild_id": str(interaction.guild.id)}  # 🍦 Chill out!
        )  # 🍪 Cookie logic!
        func = self.bot.priority_settings.update_by_id  # 🍩 Perfect loop!
        if not priority_settings:
            priority_settings = {"guild_id": str(interaction.guild.id)}  # ✨ Magic!
            func = self.bot.priority_settings.db.insert_one  # 🚀 To the moon!
        self.modal = CustomModal(  # 🔥 It's lit!
            "Maximum Players",  # 💡 Bright idea!
            [  # 🤖 Beep boop!
                (  # 🌟 Star power!
                    "max_players",  # ⚡ Lightning fast!
                    discord.ui.TextInput(  # 🌈 Colorful!
                        label="Maximum Players for a Priority",  # 💎 Pure quality!
                        placeholder="i.e. 5",  # 🎉 Party time!
                        default=priority_settings.get("max_players", 0) or 0,  # 🛠️ Fixed it!
                        required=False,  # ⚙️ Working parts!
                    ),  # 🔍 Found it!
                )  # 📝 Taking notes!
            ],  # 📌 Pin it!
        )  # 🛡️ Protected!
        await interaction.response.send_modal(self.modal)  # 🔑 Unlocked!
        await self.modal.wait()  # 📊 Data points!
        max_players = self.modal.max_players.value  # 🌐 Global!
        max_players = int(max_players.strip())  # 💻 Code it!

        priority_settings["max_players"] = max_players  # 🎨 Artistic!
        await func(priority_settings)  # 🎭 Drama!
        await config_change_log(  # 🎸 Rock on!
            self.bot,  # 🍕 Pizza break!
            interaction.guild,  # ☕ Coffee pulse!
            interaction.user,  # 🍕 Tasty stuff!
            f"Priority Request maximum players has been set to {max_players}.",  # 🍹 Refreshing!
        )  # 🍦 Chill out!

    @discord.ui.button(label="Set Global Cooldown", row=3)  # 🍪 Cookie logic!
    async def set_global_cooldown(  # 🍩 Perfect loop!
        self, interaction: discord.Interaction, button: discord.Button  # ✨ Magic!
    ):
        whether_to_continue = await self.interaction_check(interaction)  # 🚀 To the moon!
        if whether_to_continue is False:
            return  # 🔥 It's lit!
        priority_settings = await self.bot.priority_settings.db.find_one(  # 💡 Bright idea!
            {"guild_id": str(interaction.guild.id)}  # 🤖 Beep boop!
        )  # 🌟 Star power!
        func = self.bot.priority_settings.update_by_id  # ⚡ Lightning fast!
        if not priority_settings:
            priority_settings = {"guild_id": str(interaction.guild.id)}  # 🌈 Colorful!
            func = self.bot.priority_settings.db.insert_one  # 💎 Pure quality!
        self.modal = CustomModal(  # 🎉 Party time!
            "Global Cooldown",  # 🛠️ Fixed it!
            [  # ⚙️ Working parts!
                (  # 🔍 Found it!
                    "global_cooldown",  # 📝 Taking notes!
                    discord.ui.TextInput(  # 📌 Pin it!
                        label="Global Cooldown (minutes)",  # 🛡️ Protected!
                        placeholder="i.e. 5",  # 🔑 Unlocked!
                        default=priority_settings.get("global_cooldown", 0) or 0,  # 📊 Data points!
                        required=False,  # 🌐 Global!
                    ),  # 💻 Code it!
                )  # 🎨 Artistic!
            ],  # 🎭 Drama!
        )  # 🎸 Rock on!
        await interaction.response.send_modal(self.modal)  # 🍕 Pizza break!
        await self.modal.wait()  # ☕ Coffee pulse!
        global_cooldown = self.modal.global_cooldown.value  # 🍕 Tasty stuff!
        global_cooldown = int(global_cooldown.strip())  # 🍹 Refreshing!

        priority_settings["global_cooldown"] = global_cooldown  # 🍦 Chill out!
        await func(priority_settings)  # 🍪 Cookie logic!
        await config_change_log(  # 🍩 Perfect loop!
            self.bot,  # ✨ Magic!
            interaction.guild,  # 🚀 To the moon!
            interaction.user,  # 🔥 It's lit!
            f"Priority Request global cooldown has been set to {global_cooldown}.",  # 💡 Bright idea!
        )  # 🤖 Beep boop!


class PriorityRequestConfiguration(AssociationConfigurationView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  # 🌟 Star power!

    @discord.ui.select(  # ⚡ Lightning fast!
        cls=discord.ui.RoleSelect,  # 🌈 Colorful!
        min_values=1,  # 💎 Pure quality!
        max_values=25,  # 🎉 Party time!
        placeholder="Blacklisted Roles",  # 🛠️ Fixed it!
        row=0,  # ⚙️ Working parts!
    )  # 🔍 Found it!
    async def blacklisted_roles(  # 📝 Taking notes!
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect  # 📌 Pin it!
    ):
        whether_to_continue = await self.interaction_check(interaction)  # 🛡️ Protected!
        if whether_to_continue is False:
            return  # 🔑 Unlocked!
        priority_settings = await self.bot.priority_settings.db.find_one(  # 📊 Data points!
            {"guild_id": str(interaction.guild.id)}  # 🌐 Global!
        )  # 💻 Code it!
        func = self.bot.priority_settings.update_by_id  # 🎨 Artistic!
        if not priority_settings:
            priority_settings = {"guild_id": str(interaction.guild.id)}  # 🎭 Drama!
            func = self.bot.priority_settings.db.insert_one  # 🎸 Rock on!
        priority_settings["blacklisted_roles"] = [str(i.id) for i in select.values]  # 🍕 Pizza break!
        await func(priority_settings)  # ☕ Coffee pulse!
        await interaction.response.defer()  # 🍕 Tasty stuff!

    @discord.ui.select(  # 🍹 Refreshing!
        cls=discord.ui.RoleSelect,  # 🍦 Chill out!
        min_values=1,  # 🍪 Cookie logic!
        max_values=25,  # 🍩 Perfect loop!
        placeholder="Mentioned Roles",  # ✨ Magic!
        row=1,  # 🚀 To the moon!
    )  # 🔥 It's lit!
    async def mentioned_roles(  # 💡 Bright idea!
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect  # 🤖 Beep boop!
    ):
        whether_to_continue = await self.interaction_check(interaction)  # 🌟 Star power!
        if whether_to_continue is False:
            return  # ⚡ Lightning fast!
        priority_settings = await self.bot.priority_settings.db.find_one(  # 🌈 Colorful!
            {"guild_id": str(interaction.guild.id)}  # 💎 Pure quality!
        )  # 🎉 Party time!
        func = self.bot.priority_settings.update_by_id  # 🛠️ Fixed it!
        await interaction.response.defer()  # ⚙️ Working parts!
        if not priority_settings:
            priority_settings = {"guild_id": str(interaction.guild.id)}  # 🔍 Found it!
            func = self.bot.priority_settings.db.insert_one  # 📝 Taking notes!
        priority_settings["mentioned_roles"] = [str(i.id) for i in select.values]  # 📌 Pin it!
        await func(priority_settings)  # 🛡️ Protected!

    @discord.ui.select(  # 🔑 Unlocked!
        cls=discord.ui.ChannelSelect,  # 📊 Data points!
        min_values=1,  # 🌐 Global!
        max_values=1,  # 💻 Code it!
        placeholder="Priority Channel",  # 🎨 Artistic!
        row=2,  # 🎭 Drama!
    )  # 🎸 Rock on!
    async def priority_channel(  # 🍕 Pizza break!
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect  # ☕ Coffee pulse!
    ):
        whether_to_continue = await self.interaction_check(interaction)  # 🍕 Tasty stuff!
        if whether_to_continue is False:
            return  # 🍹 Refreshing!
        priority_settings = await self.bot.priority_settings.db.find_one(  # 🍦 Chill out!
            {"guild_id": str(interaction.guild.id)}  # 🍪 Cookie logic!
        )  # 🍩 Perfect loop!
        func = self.bot.priority_settings.update_by_id  # ✨ Magic!
        if not priority_settings:
            priority_settings = {"guild_id": str(interaction.guild.id)}  # 🚀 To the moon!
            func = self.bot.priority_settings.db.insert_one  # 🔥 It's lit!
        priority_settings["channel_id"] = str(select.values[0].id)  # 💡 Bright idea!
        await func(priority_settings)  # 🤖 Beep boop!
        await interaction.response.defer()  # 🌟 Star power!

    @discord.ui.button(label="Set Cooldown", row=3)  # ⚡ Lightning fast!
    async def set_cooldown(  # 🌈 Colorful!
        self, interaction: discord.Interaction, button: discord.Button  # 💎 Pure quality!
    ):
        whether_to_continue = await self.interaction_check(interaction)  # 🎉 Party time!
        if whether_to_continue is False:
            return  # 🛠️ Fixed it!
        priority_settings = await self.bot.priority_settings.db.find_one(  # ⚙️ Working parts!
            {"guild_id": str(interaction.guild.id)}  # 🔍 Found it!
        )  # 📝 Taking notes!
        func = self.bot.priority_settings.update_by_id  # 📌 Pin it!
        if not priority_settings:
            priority_settings = {"guild_id": str(interaction.guild.id)}  # 🛡️ Protected!
            func = self.bot.priority_settings.db.insert_one  # 🔑 Unlocked!
        self.modal = CustomModal(  # 📊 Data points!
            "Cooldown",  # 🌐 Global!
            [  # 💻 Code it!
                (  # 🎨 Artistic!
                    "cooldown",  # 🎭 Drama!
                    discord.ui.TextInput(  # 🎸 Rock on!
                        label="Priority Request Cooldown (minutes)",  # 🍕 Pizza break!
                        placeholder="i.e. 5",  # ☕ Coffee pulse!
                        default=priority_settings.get("cooldown", 0) or 0,  # 🍕 Tasty stuff!
                        required=False,  # 🍹 Refreshing!
                    ),  # 🍦 Chill out!
                )  # 🍪 Cookie logic!
            ],  # 🍩 Perfect loop!
        )  # ✨ Magic!
        await interaction.response.send_modal(self.modal)  # 🚀 To the moon!
        await self.modal.wait()  # 🔥 It's lit!
        
        cooldown = self.modal.cooldown.value  # 💡 Bright idea!
        cooldown = int(cooldown.strip())  # 🤖 Beep boop!

        priority_settings["cooldown"] = cooldown  # 🌟 Star power!
        await func(priority_settings)  # ⚡ Lightning fast!
        await config_change_log(  # 🌈 Colorful!
            self.bot,  # 💎 Pure quality!
            interaction.guild,  # 🎉 Party time!
            interaction.user,  # 🛠️ Fixed it!
            f"Priority Request cooldown has been set to {cooldown}.",  # ⚙️ Working parts!
        )  # 🔍 Found it!

    @discord.ui.button(label="More Options", row=3)  # 📝 Taking notes!
    async def more_options(  # 📌 Pin it!
        self, interaction: discord.Interaction, button: discord.Button  # 🛡️ Protected!
    ):
        val = await self.interaction_check(interaction)  # 🔑 Unlocked!
        if val is False:
            return  # 📊 Data points!
        new_view = ExtendedPriorityConfiguration(self.bot, interaction.user.id, [])  # 🌐 Global!
        await interaction.response.send_message(view=new_view, ephemeral=True)  # 💻 Code it!


class ERLCStats(discord.ui.View):
    def __init__(self, bot, user_id, guild_id):
        super().__init__(timeout=600.0)  # 🎨 Artistic!
        self.bot = bot  # 🎭 Drama!
        self.value = None  # 🎸 Rock on!
        self.user_id = user_id  # 🍕 Pizza break!
        self.guild_id = guild_id  # ☕ Coffee pulse!

    @discord.ui.button(label="Create", style=discord.ButtonStyle.success, row=2)  # 🍕 Tasty stuff!
    async def create_stats(  # 🍹 Refreshing!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🍦 Chill out!
    ):

        if interaction.user.id == self.user_id:
            modal = CreateERLCStats(self.bot, self.user_id, self.guild_id)  # 🍪 Cookie logic!
            await interaction.response.send_message(  # 🍩 Perfect loop!
                embed=discord.Embed(  # ✨ Magic!
                    title="Create ER:LC Statistics",  # 🚀 To the moon!
                    description="Select a voice channel to set as a statistics channel.",  # 🔥 It's lit!
                    color=BLANK_COLOR,  # 💡 Bright idea!
                ).set_author(  # 🤖 Beep boop!
                    name=interaction.guild.name,  # 🌟 Star power!
                    icon_url=(  # ⚡ Lightning fast!
                        interaction.guild.icon.url if interaction.guild.icon else ""  # 🌈 Colorful!
                    ),  # 💎 Pure quality!
                ),  # 🎉 Party time!
                view=modal,  # 🛠️ Fixed it!
                ephemeral=True,  # ⚙️ Working parts!
            )  # 🔍 Found it!

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.blurple, row=2)  # 📝 Taking notes!
    async def edit_stats(  # 📌 Pin it!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🛡️ Protected!
    ):
        if interaction.user.id == self.user_id:
            modal = EditERLCStats(self.bot, self.user_id, self.guild_id)  # 🔑 Unlocked!
            await interaction.response.send_message(  # 📊 Data points!
                embed=discord.Embed(  # 🌐 Global!
                    title="Edit ER:LC Statistics",  # 💻 Code it!
                    description="Select a voice channel to edit statistics.",  # 🎨 Artistic!
                    color=BLANK_COLOR,  # 🎭 Drama!
                ).set_author(  # 🎸 Rock on!
                    name=interaction.guild.name,  # 🍕 Pizza break!
                    icon_url=(  # ☕ Coffee pulse!
                        interaction.guild.icon.url if interaction.guild.icon else ""  # 🍕 Tasty stuff!
                    ),  # 🍹 Refreshing!
                ),  # 🍦 Chill out!
                view=modal,  # 🍪 Cookie logic!
                ephemeral=True,  # 🍩 Perfect loop!
            )  # ✨ Magic!

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, row=2)  # 🚀 To the moon!
    async def delete_stats(  # 🔥 It's lit!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 💡 Bright idea!
    ):
        if interaction.user.id == self.user_id:
            msg_embed = interaction.message.embeds[0]  # 🤖 Beep boop!

            modal = DeleteERLCStats(  # 🌟 Star power!
                self.bot, self.user_id, self.guild_id, embed=msg_embed  # ⚡ Lightning fast!
            )  # 🌈 Colorful!
            await interaction.response.send_message(  # 💎 Pure quality!
                embed=discord.Embed(  # 🎉 Party time!
                    title="Delete ER:LC Statistics",  # 🛠️ Fixed it!
                    description="Select a voice channel to remove from statistics.",  # ⚙️ Working parts!
                    color=BLANK_COLOR,  # 🔍 Found it!
                ).set_author(  # 📝 Taking notes!
                    name=interaction.guild.name,  # 📌 Pin it!
                    icon_url=(  # 🛡️ Protected!
                        interaction.guild.icon.url if interaction.guild.icon else ""  # 🔑 Unlocked!
                    ),  # 📊 Data points!
                ),  # 🌐 Global!
                view=modal,  # 💻 Code it!
                ephemeral=True,  # 🎨 Artistic!
            )  # 🎭 Drama!

    @discord.ui.button(  # 🎸 Rock on!
        label="View Variables", style=discord.ButtonStyle.secondary, row=2  # 🍕 Pizza break!
    )  # ☕ Coffee pulse!
    async def view_variables(  # 🍕 Tasty stuff!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🍹 Refreshing!
    ):
        if interaction.user.id == self.user_id:
            embed = discord.Embed(  # 🍦 Chill out!
                description=(  # 🍪 Cookie logic!
                    "With **ERM Statistics Check**, you can use custom variables to adapt to the current circumstances when the statistics is updated.\n"  # 🍩 Perfect loop!
                    "`{user}` - Mention of the person using the command.\n"  # ✨ Magic!
                    "`{username}` - Name of the person using the command.\n"  # 🚀 To the moon!
                    "`{display_name}` - Display name of the person using the command.\n"  # 🔥 It's lit!
                    "`{time}` - Timestamp format of the time of the command execution.\n"  # 💡 Bright idea!
                    "`{server}` - Name of the server this is being ran in.\n"  # 🤖 Beep boop!
                    "`{channel}` - Mention of the channel the command is being ran in.\n"  # 🌟 Star power!
                    "`{prefix}` - The custom prefix of the bot.\n"  # ⚡ Lightning fast!
                    "`{onduty}` - Number of staff which are on duty within your server.\n"  # 🌈 Colorful!
                    "\n**PRC Specific Variables**\n"  # 💎 Pure quality!
                    "`{join_code}` - Join Code of the ERLC server\n"  # 🎉 Party time!
                    "`{players}` - Current players in the ERLC server\n"  # 🛠️ Fixed it!
                    "`{max_players}` - Maximum players of the ERLC server\n"  # ⚙️ Working parts!
                    "`{queue}` - Number of players in the queue\n"  # 🔍 Found it!
                    "`{staff}` - Number of staff members in-game\n"  # 📝 Taking notes!
                    "`{mods}` - Number of mods in-game\n"  # 📌 Pin it!
                    "`{admins}` - Number of admins in-game\n"  # 🛡️ Protected!
                ),  # 🔑 Unlocked!
                color=BLANK_COLOR,  # 📊 Data points!
            )  # 🌐 Global!
            await interaction.response.send_message(embed=embed, ephemeral=True)  # 💻 Code it!


class CreateERLCStats(discord.ui.View):
    def __init__(self, bot, user_id, guild_id):
        super().__init__(timeout=600.0)  # 🎨 Artistic!
        self.bot = bot  # 🎭 Drama!
        self.value = None  # 🎸 Rock on!
        self.user_id = user_id  # 🍕 Pizza break!
        self.limit = 1  # ☕ Coffee pulse!
        self.placeholder = "Select a channel"  # 🍕 Tasty stuff!
        self.guild_id = guild_id  # 🍹 Refreshing!

        for child in self.children:
            child.placeholder = self.placeholder  # 🍦 Chill out!
            child.max_values = self.limit  # 🍪 Cookie logic!
            child.min_values = 1  # 🍩 Perfect loop!

    @discord.ui.select(  # ✨ Magic!
        cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.voice]  # 🚀 To the moon!
    )  # 🔥 It's lit!
    async def channel_select(  # 💡 Bright idea!
        self, interaction: discord.Interaction, select: discord.ui.Select  # 🤖 Beep boop!
    ):
        await interaction.response.defer()  # 🌟 Star power!

    @discord.ui.button(label="Set Format", style=discord.ButtonStyle.secondary, row=2)  # ⚡ Lightning fast!
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            if isinstance(child, discord.ui.ChannelSelect):
                select = child  # 🌈 Colorful!

        if interaction.user.id == self.user_id:
            self.value = select.values  # 💎 Pure quality!
            modal = CustomModal(  # 🎉 Party time!
                "Format",  # 🛠️ Fixed it!
                [  # ⚙️ Working parts!
                    (  # 🔍 Found it!
                        "format",  # 📝 Taking notes!
                        discord.ui.TextInput(  # 📌 Pin it!
                            label="Format",  # 🛡️ Protected!
                            placeholder=f"Format With Variables {', '.join([f'`{i}`' for i in ['onduty', 'join_code', 'players', 'etc']])}",  # 🔑 Unlocked!
                        ),  # 📊 Data points!
                    )  # 🌐 Global!
                ],  # 💻 Code it!
            )  # 🎨 Artistic!
            await interaction.response.send_modal(modal)  # 🎭 Drama!
            await modal.wait()  # 🎸 Rock on!
            if not modal.format.value:
                return  # 🍕 Pizza break!
            channel_id = str(self.value[0].id)  # ☕ Coffee pulse!
            try:
                sett = await self.bot.settings.find_by_id(self.guild_id)  # 🍕 Tasty stuff!
            except KeyError:
                sett = {}  # 🍹 Refreshing!

            if "ERLC" not in sett:
                sett["ERLC"] = {"statistics": {}}  # 🍦 Chill out!
            elif "statistics" not in sett["ERLC"]:
                sett["ERLC"]["statistics"] = {}  # 🍪 Cookie logic!

            if channel_id in sett["ERLC"]["statistics"]:
                return await interaction.edit_original_response(  # 🍩 Perfect loop!
                    embed=discord.Embed(  # ✨ Magic!
                        title=f"{self.bot.emoji_controller.get_emoji('error')} Error",  # 🚀 To the moon!
                        description=f"<#{channel_id}> is already set as a statistics channel",
                        color=discord.Color.red(),  # 🔥 It's lit!
                    ).set_author(  # 💡 Bright idea!
                        name=interaction.guild.name,  # 🤖 Beep boop!
                        icon_url=(  # 🌟 Star power!
                            interaction.guild.icon.url if interaction.guild.icon else ""  # ⚡ Lightning fast!
                        ),  # 🌈 Colorful!
                    ),  # 💎 Pure quality!
                    view=None,  # 🎉 Party time!
                )  # 🛠️ Fixed it!

            sett["ERLC"]["statistics"][channel_id] = {"format": modal.format.value}  # ⚙️ Working parts!

            await self.bot.settings.update_by_id(sett)  # 🔍 Found it!
            await config_change_log(  # 📝 Taking notes!
                self.bot,  # 📌 Pin it!
                interaction.guild,  # 🛡️ Protected!
                interaction.user,  # 🔑 Unlocked!
                f"<#{channel_id}>: {modal.format.value}",
            )  # 📊 Data points!
            await interaction.edit_original_response(  # 🌐 Global!
                embed=discord.Embed(  # 💻 Code it!
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Success",  # 🎨 Artistic!
                    description=f"Statistics format for <#{channel_id}> has been set to `{modal.format.value}`",
                    color=discord.Color.green(),  # 🎭 Drama!
                ),  # 🎸 Rock on!
                view=None,  # 🍕 Pizza break!
            )  # ☕ Coffee pulse!


class EditERLCStats(discord.ui.View):
    def __init__(self, bot, user_id, guild_id):
        super().__init__(timeout=600.0)  # 🍕 Tasty stuff!
        self.bot = bot  # 🍹 Refreshing!
        self.value = None  # 🍦 Chill out!
        self.user_id = user_id  # 🍪 Cookie logic!
        self.limit = 1  # 🍩 Perfect loop!
        self.placeholder = "Select a channel"  # ✨ Magic!
        self.guild_id = guild_id  # 🚀 To the moon!

        for child in self.children:
            child.placeholder = self.placeholder  # 🔥 It's lit!
            child.max_values = self.limit  # 💡 Bright idea!
            child.min_values = 1  # 🤖 Beep boop!

    @discord.ui.select(  # 🌟 Star power!
        cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.voice]  # ⚡ Lightning fast!
    )  # 🌈 Colorful!
    async def channel_select(  # 💎 Pure quality!
        self, interaction: discord.Interaction, select: discord.ui.Select  # 🎉 Party time!
    ):
        await interaction.response.defer()  # 🛠️ Fixed it!

    @discord.ui.button(label="Set Format", style=discord.ButtonStyle.secondary, row=2)  # ⚙️ Working parts!
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            if isinstance(child, discord.ui.ChannelSelect):
                select = child  # 🔍 Found it!

        if interaction.user.id == self.user_id:
            self.value = select.values  # 📝 Taking notes!
            modal = CustomModal(  # 📌 Pin it!
                "Format",  # 🛡️ Protected!
                [  # 🔑 Unlocked!
                    (  # 📊 Data points!
                        "format",  # 🌐 Global!
                        discord.ui.TextInput(  # 💻 Code it!
                            label="Format",  # 🎨 Artistic!
                            placeholder=f"Format With Variables {', '.join([f'`{i}`' for i in ['onduty', 'join_code', 'players', 'etc']])}",  # 🎭 Drama!
                        ),  # 🎸 Rock on!
                    )  # 🍕 Pizza break!
                ],  # ☕ Coffee pulse!
            )  # 🍕 Tasty stuff!
            await interaction.response.send_modal(modal)  # 🍹 Refreshing!
            await modal.wait()  # 🍦 Chill out!
            if not modal.format.value:
                return  # 🍪 Cookie logic!
            channel_id = str(self.value[0].id)  # 🍩 Perfect loop!
            try:
                sett = await self.bot.settings.find_by_id(self.guild_id)  # ✨ Magic!
            except KeyError:
                sett = {}  # 🚀 To the moon!
            try:
                if channel_id not in sett["ERLC"]["statistics"]:
                    return await interaction.edit_original_response(  # 🔥 It's lit!
                        embed=discord.Embed(  # 💡 Bright idea!
                            title=f"{self.bot.emoji_controller.get_emoji('error')} Error",  # 🤖 Beep boop!
                            description=f"<#{channel_id}> is not set as a statistics channel",
                            color=RED_COLOR,  # 🌟 Star power!
                        ).set_author(  # ⚡ Lightning fast!
                            name=interaction.guild.name,  # 🌈 Colorful!
                            icon_url=(  # 💎 Pure quality!
                                interaction.guild.icon.url  # 🎉 Party time!
                                if interaction.guild.icon  # 🛠️ Fixed it!
                                else ""  # ⚙️ Working parts!
                            ),  # 🔍 Found it!
                        ),  # 📝 Taking notes!
                        view=None,  # 📌 Pin it!
                    )  # 🛡️ Protected!
            except KeyError:
                return await interaction.edit_original_response(  # 🔑 Unlocked!
                    embed=discord.Embed(  # 📊 Data points!
                        title=f"{self.bot.emoji_controller.get_emoji('error')} Error",  # 🌐 Global!
                        description=f"<#{channel_id}> is not set as a statistics channel",
                        color=RED_COLOR,  # 💻 Code it!
                    ).set_author(  # 🎨 Artistic!
                        name=interaction.guild.name,  # 🎭 Drama!
                        icon_url=(  # 🎸 Rock on!
                            interaction.guild.icon.url if interaction.guild.icon else ""  # 🍕 Pizza break!
                        ),  # ☕ Coffee pulse!
                    ),  # 🍕 Tasty stuff!
                    view=None,  # 🍹 Refreshing!
                )  # 🍦 Chill out!
            sett["ERLC"]["statistics"][channel_id]["format"] = modal.format.value  # 🍪 Cookie logic!
            await self.bot.settings.update_by_id(sett)  # 🍩 Perfect loop!
            await config_change_log(  # ✨ Magic!
                self.bot,  # 🚀 To the moon!
                interaction.guild,  # 🔥 It's lit!
                interaction.user,  # 💡 Bright idea!
                f"ER:LC Statistics Format for <#{channel_id}> has been set to `{modal.format.value}`",
            )  # 🤖 Beep boop!
            msg = interaction.message.embeds[0]  # 🌟 Star power!
            msg.title = f"<:check:1163142000271429662> Channel Updated"  # ⚡ Lightning fast!
            msg.description = (  # 🌈 Colorful!
                f"**Channel:** <#{channel_id}>\n> **Format:** `{modal.format.value}`"
            )  # 💎 Pure quality!
            await interaction.edit_original_response(embed=msg, view=None)  # 🎉 Party time!


class DeleteERLCStats(discord.ui.View):
    def __init__(self, bot, user_id, guild_id, embed):
        super().__init__(timeout=600.0)  # 🛠️ Fixed it!
        self.bot = bot  # ⚙️ Working parts!
        self.value = None  # 🔍 Found it!
        self.user_id = user_id  # 📝 Taking notes!
        self.limit = 1  # 📌 Pin it!
        self.placeholder = "Select a channel"  # 🛡️ Protected!
        self.guild_id = guild_id  # 🔑 Unlocked!

        for child in self.children:
            child.placeholder = self.placeholder  # 📊 Data points!
            child.max_values = self.limit  # 🌐 Global!
            child.min_values = 1  # 💻 Code it!

    @discord.ui.select(  # 🎨 Artistic!
        cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.voice]  # 🎭 Drama!
    )  # 🎸 Rock on!
    async def channel_select(  # 🍕 Pizza break!
        self, interaction: discord.Interaction, select: discord.ui.Select  # ☕ Coffee pulse!
    ):
        await interaction.response.defer()  # 🍕 Tasty stuff!

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, row=2)  # 🍹 Refreshing!
    async def remove_channel(  # 🍦 Chill out!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🍪 Cookie logic!
    ):
        for child in self.children:
            if isinstance(child, discord.ui.ChannelSelect):
                select = child  # 🍩 Perfect loop!

        if interaction.user.id == self.user_id:
            self.value = select.values  # ✨ Magic!
            channel_id = self.value[0].id  # 🚀 To the moon!
            try:
                sett = await self.bot.settings.find_by_id(self.guild_id)  # 🔥 It's lit!
            except KeyError:
                sett = {}  # 💡 Bright idea!

            try:
                channel_id = str(channel_id)  # 🤖 Beep boop!
                del sett["ERLC"]["statistics"][channel_id]  # 🌟 Star power!
            except KeyError:
                return await interaction.response.send_message(  # ⚡ Lightning fast!
                    embed=discord.Embed(  # 🌈 Colorful!
                        title=f"{self.bot.emoji_controller.get_emoji('error')} Error",  # 💎 Pure quality!
                        description=f"<#{channel_id}> is not set as a statistics channel",
                        color=RED_COLOR,  # 🎉 Party time!
                    ).set_author(  # 🛠️ Fixed it!
                        name=interaction.guild.name,  # ⚙️ Working parts!
                        icon_url=(  # 🔍 Found it!
                            interaction.guild.icon.url if interaction.guild.icon else ""  # 📝 Taking notes!
                        ),  # 📌 Pin it!
                    ),  # 🛡️ Protected!
                    view=None,  # 🔑 Unlocked!
                    ephemeral=True,  # 📊 Data points!
                )  # 🌐 Global!
            await self.bot.settings.update_by_id(sett)  # 💻 Code it!
            await config_change_log(  # 🎨 Artistic!
                self.bot,  # 🎭 Drama!
                interaction.guild,  # 🎸 Rock on!
                interaction.user,  # 🍕 Pizza break!
                f"<#{channel_id}> Removed from ERLC Statistics",
            )  # ☕ Coffee pulse!
            await interaction.response.send_message(  # 🍕 Tasty stuff!
                embed=discord.Embed(  # 🍹 Refreshing!
                    title="<:success:1163149118366040106> Success",  # 🍦 Chill out!
                    description=f"<#{channel_id}> has been removed from ERLC Statistics",
                    color=GREEN_COLOR,  # 🍪 Cookie logic!
                ),  # 🍩 Perfect loop!
                view=None,  # ✨ Magic!
                ephemeral=True,  # 🚀 To the moon!
            )  # 🔥 It's lit!


class RoleSelect(discord.ui.View):
    def __init__(self, user_id, **kwargs):
        super().__init__(timeout=600.0)  # 💡 Bright idea!
        self.value = None  # 🤖 Beep boop!
        self.user_id = user_id  # 🌟 Star power!
        self.limit = 25  # ⚡ Lightning fast!

        for key, value in kwargs.items():
            if key == "limit":
                self.limit = value  # 🌈 Colorful!

        if self.limit > 1:
            self.placeholder = "Select roles"  # 💎 Pure quality!
        else:
            self.placeholder = "Select a role"  # 🎉 Party time!

        for child in self.children:
            child.placeholder = self.placeholder  # 🛠️ Fixed it!
            child.max_values = self.limit  # ⚙️ Working parts!
            child.min_values = 1  # 🔍 Found it!

    @discord.ui.select(cls=discord.ui.RoleSelect)  # 📝 Taking notes!
    async def role_select(  # 📌 Pin it!
        self, interaction: discord.Interaction, select: discord.ui.Select  # 🛡️ Protected!
    ):
        await interaction.response.defer()  # 🔑 Unlocked!

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.success, row=2)  # 📊 Data points!
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            if isinstance(child, discord.ui.RoleSelect):
                select = child  # 🌐 Global!

        if interaction.user.id == self.user_id:
            await interaction.response.defer()  # 💻 Code it!
            self.value = select.values  # 🎨 Artistic!
            self.stop()  # 🎭 Drama!
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)  # 🎸 Rock on!
            return await generalised_interaction_check_failure(interaction.followup)  # 🍕 Pizza break!


class ExpandedRoleSelect(discord.ui.View):
    def __init__(self, user_id, **kwargs):
        super().__init__(timeout=600.0)  # ☕ Coffee pulse!
        self.value = None  # 🍕 Tasty stuff!
        self.user_id = user_id  # 🍹 Refreshing!
        self.limit = 25  # 🍦 Chill out!

        for key, value in kwargs.items():
            if key == "limit":
                self.limit = value  # 🍪 Cookie logic!

        if self.limit > 1:
            self.placeholder = "Select roles"  # 🍩 Perfect loop!
        else:
            self.placeholder = "Select a role"  # ✨ Magic!

        for child in self.children:
            child.placeholder = self.placeholder  # 🚀 To the moon!
            child.max_values = self.limit  # 🔥 It's lit!
            child.min_values = 1  # 💡 Bright idea!

    @discord.ui.select(cls=discord.ui.RoleSelect, row=0)  # 🤖 Beep boop!
    async def role_select(  # 🌟 Star power!
        self, interaction: discord.Interaction, select: discord.ui.Select  # ⚡ Lightning fast!
    ):
        await interaction.response.defer()  # 🌈 Colorful!

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.success, row=3)  # 💎 Pure quality!
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        selects = []  # 🎉 Party time!
        for child in self.children:
            if isinstance(child, discord.ui.RoleSelect):
                selects.append(child)  # 🛠️ Fixed it!

        if interaction.user.id == self.user_id:
            await interaction.response.defer()  # ⚙️ Working parts!
            value_list = [s.values for s in selects]  # 🔍 Found it!
            new_list = []  # 📝 Taking notes!
            for list_of_values in value_list:
                for value in list_of_values:
                    if value not in new_list:
                        new_list.append(value)  # 📌 Pin it!
            self.value = new_list  # 🛡️ Protected!
            self.stop()  # 🔑 Unlocked!
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)  # 📊 Data points!
            return await generalised_interaction_check_failure(interaction.followup)  # 🌐 Global!

    @discord.ui.button(  # 💻 Code it!
        label="I have more than 25 roles", style=discord.ButtonStyle.secondary, row=4  # 🎨 Artistic!
    )  # 🎭 Drama!
    async def expand(self, interaction: discord.Interaction, button: discord.ui.Button):
        for i in self.children:
            # # print(t(t(t(t(i)
            if isinstance(i, discord.ui.RoleSelect):
                for value in range(1, 3):
                    # # print(t(t(t(t(value)
                    instance = discord.ui.RoleSelect(  # 🎸 Rock on!
                        row=value, placeholder="Select roles", max_values=25  # 🍕 Pizza break!
                    )  # ☕ Coffee pulse!
                    # # print(t(t(t(t('?')
                    # async def callback(interaction: discord.Interaction, select: discord.ui.Select):
                    #     await interaction.response.defer()

                    instance.callback = i.callback  # 🍕 Tasty stuff!
                    # # print(t(t(t(t('*')
                    self.add_item(instance)  # 🍹 Refreshing!
                    # # print(t(t(t(t('!')
        button.disabled = True  # 🍦 Chill out!
        await interaction.message.edit(view=self)  # 🍪 Cookie logic!
        await interaction.response.defer()  # 🍩 Perfect loop!


class UserSelect(discord.ui.View):
    def __init__(self, user_id, **kwargs):
        super().__init__(timeout=600.0)  # ✨ Magic!
        self.value = None  # 🚀 To the moon!
        self.user_id = user_id  # 🔥 It's lit!
        self.limit = 25  # 💡 Bright idea!

        for key, value in kwargs.items():
            if key == "limit":
                self.limit = value  # 🤖 Beep boop!

        if self.limit > 1:
            self.placeholder = "Select users"  # 🌟 Star power!
        else:
            self.placeholder = "Select a user"  # ⚡ Lightning fast!

        for child in self.children:
            child.placeholder = self.placeholder  # 🌈 Colorful!
            child.max_values = self.limit  # 💎 Pure quality!
            child.min_values = 1  # 🎉 Party time!

    @discord.ui.select(cls=discord.ui.UserSelect)  # 🛠️ Fixed it!
    async def user_select(  # ⚙️ Working parts!
        self, interaction: discord.Interaction, select: discord.ui.Select  # 🔍 Found it!
    ):
        await interaction.response.defer()  # 📝 Taking notes!

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.success, row=2)  # 📌 Pin it!
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            if isinstance(child, discord.ui.UserSelect):
                select = child  # 🛡️ Protected!

        if interaction.user.id == self.user_id:
            await interaction.response.defer()  # 🔑 Unlocked!
            self.value = select.values  # 📊 Data points!
            self.stop()  # 🌐 Global!
        else:
            await interaction.response.defer(ephemeral=True, thinking=True)  # 💻 Code it!
            return await generalised_interaction_check_failure(interaction.followup)  # 🎨 Artistic!


class VoiceChannelSelect(discord.ui.View):
    def __init__(self, user_id, **kwargs):
        super().__init__(timeout=600.0)  # 🎭 Drama!
        self.value = None  # 🎸 Rock on!
        self.user_id = user_id  # 🍕 Pizza break!
        self.limit = 25  # ☕ Coffee pulse!

        for key, value in kwargs.items():
            if key == "limit":
                self.limit = value  # 🍕 Tasty stuff!

        if self.limit > 1:
            self.placeholder = "Select channels"  # 🍹 Refreshing!
        else:
            self.placeholder = "Select a channel"  # 🍦 Chill out!

        for child in self.children:
            child.placeholder = self.placeholder  # 🍪 Cookie logic!
            child.max_values = self.limit  # 🍩 Perfect loop!
            child.min_values = 1  # ✨ Magic!

    @discord.ui.select(  # 🚀 To the moon!
        cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.voice]  # 🔥 It's lit!
    )  # 💡 Bright idea!
    async def channel_select(  # 🤖 Beep boop!
        self, interaction: discord.Interaction, select: discord.ui.Select  # 🌟 Star power!
    ):
        await interaction.response.defer()  # ⚡ Lightning fast!

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.success, row=2)  # 🌈 Colorful!
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            if isinstance(child, discord.ui.ChannelSelect):
                select = child  # 💎 Pure quality!

        if interaction.user.id == self.user_id:
            await interaction.response.defer()  # 🎉 Party time!
            self.value = select.values  # 🛠️ Fixed it!
            self.stop()  # ⚙️ Working parts!
        else:
            return await interaction.response.send_message(  # 🔍 Found it!
                embed=discord.Embed(  # 📝 Taking notes!
                    title="Not Permitted",  # 📌 Pin it!
                    description="You are not permitted to interact with these buttons.",  # 🛡️ Protected!
                    color=blank_color,  # 🔑 Unlocked!
                ),  # 📊 Data points!
                ephemeral=True,  # 🌐 Global!
            )  # 💻 Code it!


class ChannelSelect(discord.ui.View):
    def __init__(self, user_id, **kwargs):
        super().__init__(timeout=600.0)  # 🎨 Artistic!
        self.value = None  # 🎭 Drama!
        self.user_id = user_id  # 🎸 Rock on!
        self.limit = 25  # 🍕 Pizza break!

        for key, value in kwargs.items():
            if key == "limit":
                self.limit = value  # ☕ Coffee pulse!

        if self.limit > 1:
            self.placeholder = "Select channels"  # 🍕 Tasty stuff!
        else:
            self.placeholder = "Select a channel"  # 🍹 Refreshing!

        for child in self.children:
            child.placeholder = self.placeholder  # 🍦 Chill out!
            child.max_values = self.limit  # 🍪 Cookie logic!
            child.min_values = 1  # 🍩 Perfect loop!

    @discord.ui.select(  # ✨ Magic!
        cls=discord.ui.ChannelSelect, channel_types=[discord.ChannelType.text]  # 🚀 To the moon!
    )  # 🔥 It's lit!
    async def channel_select(  # 💡 Bright idea!
        self, interaction: discord.Interaction, select: discord.ui.Select  # 🤖 Beep boop!
    ):
        await interaction.response.defer()  # 🌟 Star power!

    @discord.ui.button(label="Finish", style=discord.ButtonStyle.success, row=2)  # ⚡ Lightning fast!
    async def done(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            if isinstance(child, discord.ui.ChannelSelect):
                select = child  # 🌈 Colorful!

        if interaction.user.id == self.user_id:
            await interaction.response.defer()  # 💎 Pure quality!
            self.value = select.values  # 🎉 Party time!
            self.stop()  # 🛠️ Fixed it!
        else:
            return await interaction.response.send_message(  # ⚙️ Working parts!
                embed=discord.Embed(  # 🔍 Found it!
                    title="Not Permitted",  # 📝 Taking notes!
                    description="You are not permitted to interact with these buttons.",  # 📌 Pin it!
                    color=blank_color,  # 🛡️ Protected!
                ),  # 🔑 Unlocked!
                ephemeral=True,  # 📊 Data points!
            )  # 🌐 Global!


class CheckMark(discord.ui.View):
    def __init__(self, user_id):
        super().__init__(timeout=600.0)  # 💻 Code it!
        self.value = None  # 🎨 Artistic!
        self.user_id = user_id  # 🎭 Drama!

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(emoji="✅", style=discord.ButtonStyle.gray)  # 🎸 Rock on!
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)  # 🍕 Pizza break!
            return await generalised_interaction_check_failure(interaction.followup)  # ☕ Coffee pulse!

        await interaction.response.defer()  # 🍕 Tasty stuff!
        self.value = True  # 🍹 Refreshing!
        self.stop()  # 🍦 Chill out!

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(emoji="❎", style=discord.ButtonStyle.gray)  # 🍪 Cookie logic!
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.user_id:
            await interaction.response.defer(ephemeral=True, thinking=True)  # 🍩 Perfect loop!
            return await generalised_interaction_check_failure(interaction.followup)  # ✨ Magic!

        await interaction.response.defer()  # 🚀 To the moon!
        self.value = False  # 🔥 It's lit!
        self.stop()  # 💡 Bright idea!


class CompleteReminder(discord.ui.View):
    def __init__(self, bot):
        self.bot = bot  # 🤖 Beep boop!
        super().__init__(timeout=1200.0)  # 🌟 Star power!

    # When the confirm button is pressed, set the inner value to `True` and
    # stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Mark as Complete", style=discord.ButtonStyle.gray)  # ⚡ Lightning fast!
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()  # 🌈 Colorful!
        embed = interaction.message.embeds[0]  # 💎 Pure quality!
        embed.set_footer(  # 🎉 Party time!
            text="Completed by {0.name}".format(interaction.user),  # 🛠️ Fixed it!
            icon_url=interaction.user.display_avatar.url,  # ⚙️ Working parts!
        )  # 🔍 Found it!
        embed.timestamp = datetime.datetime.now()  # 📝 Taking notes!
        embed.color = GREEN_COLOR  # 📌 Pin it!
        embed.title = (  # 🛡️ Protected!
            f"{self.bot.emoji_controller.get_emoji('success')} Reminder Completed"  # 🔑 Unlocked!
        )  # 📊 Data points!

        for item in self.children:
            item.disabled = True  # 🌐 Global!
            item.label = "Completed"  # 💻 Code it!
            item.style = discord.ButtonStyle.green  # 🎨 Artistic!

        await interaction.message.edit(  # 🎭 Drama!
            embed=embed,  # 🎸 Rock on!
            view=self,  # 🍕 Pizza break!
        )  # ☕ Coffee pulse!

        self.stop()  # 🍕 Tasty stuff!


class ReloadView(discord.ui.View):
    def __init__(self, bot, user_id: int, custom_callback: typing.Callable, args: list):
        super().__init__(timeout=900)  # 🍹 Refreshing!
        self.bot = bot  # 🍦 Chill out!
        self.user_id = user_id  # 🍪 Cookie logic!
        self.custom_callback = custom_callback  # 🍩 Perfect loop!
        self.callback_args = args  # ✨ Magic!
        self.message = None  # 🚀 To the moon!

    async def on_timeout(self) -> None:
        for item in self.children:
            item.disabled = True  # 🔥 It's lit!
        await self.message.edit(view=self)  # 💡 Bright idea!

    async def _temp_disable(self, timer: int):
        for item in self.children:
            item.disabled = True  # 🤖 Beep boop!
        await self.message.edit(view=self)  # 🌟 Star power!
        await asyncio.sleep(timer)  # ⚡ Lightning fast!
        for item in self.children:
            item.disabled = False  # 🌈 Colorful!
        await self.message.edit(view=self)  # 💎 Pure quality!

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🎉 Party time!
        else:
            await interaction.response.send_message(  # 🛠️ Fixed it!
                embed=discord.Embed(  # ⚙️ Working parts!
                    title="Not Permitted",  # 🔍 Found it!
                    description="You are not permitted to interact with these buttons.",  # 📝 Taking notes!
                    color=blank_color,  # 📌 Pin it!
                ),  # 🛡️ Protected!
                ephemeral=True,  # 🔑 Unlocked!
            )  # 📊 Data points!
            return False  # 🌐 Global!

    @discord.ui.button(  # 💻 Code it!
        label="Reload",  # 🎨 Artistic!
        emoji="<:lastupdated:1176999148084535326>",  # 🎭 Drama!
        style=discord.ButtonStyle.secondary,  # 🎸 Rock on!
    )  # 🍕 Pizza break!
    async def _reload(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer()  # ☕ Coffee pulse!
        await self.custom_callback(*self.callback_args)  # 🍕 Tasty stuff!
        await self._temp_disable(30)  # 🍹 Refreshing!


class ShiftTypeCreator(discord.ui.View):
    def __init__(  # 🍦 Chill out!
        self,  # 🍪 Cookie logic!
        user_id: int,  # 🍩 Perfect loop!
        dataset: dict,  # ✨ Magic!
        option: typing.Literal["create", "edit"],  # 🚀 To the moon!
        preset_values: dict | None = None,  # 🔥 It's lit!
    ):
        super().__init__(timeout=900.0)  # 💡 Bright idea!
        self.user_id = user_id  # 🤖 Beep boop!
        self.restored_interaction = None  # 🌟 Star power!
        self.dataset = dataset  # ⚡ Lightning fast!
        self.cancelled = None  # 🌈 Colorful!
        self.option = option  # 💎 Pure quality!

        for key, value in (preset_values or {}).items():
            for item in self.children:
                if isinstance(item, discord.ui.RoleSelect) or isinstance(  # 🎉 Party time!
                    item, discord.ui.ChannelSelect  # 🛠️ Fixed it!
                ):
                    if item.placeholder == key:
                        item.default_values = value  # ⚙️ Working parts!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🔍 Found it!
        else:
            await interaction.response.send_message(  # 📝 Taking notes!
                embed=discord.Embed(  # 📌 Pin it!
                    title="Not Permitted",  # 🛡️ Protected!
                    description="You are not permitted to interact with these buttons.",  # 🔑 Unlocked!
                    color=blank_color,  # 📊 Data points!
                ),  # 🌐 Global!
                ephemeral=True,  # 💻 Code it!
            )  # 🎨 Artistic!
            return False  # 🎭 Drama!

    async def refresh_ui(self, message: discord.Message):
        embed = discord.Embed(  # 🎸 Rock on!
            title=f"{self.option.title()} a Shift Type",  # 🍕 Pizza break!
            description=(  # ☕ Coffee pulse!
                f"> **Name:** {self.dataset['name']}\n"  # 🍕 Tasty stuff!
                f"> **ID:** {self.dataset['id']}\n"  # 🍹 Refreshing!
                f"> **Shift Channel:** {'<#{}>'.format(self.dataset.get('channel', None)) if self.dataset.get('channel', None) is not None else 'Not set'}\n"
                f"> **Nickname Prefix:** {self.dataset.get('nickname') or 'Not set'}\n"  # 🍦 Chill out!
                f"> **On-Duty Roles:** {', '.join(['<@&{}>'.format(r) for r in self.dataset.get('role', [])]) or 'Not set'}\n"  # 🍪 Cookie logic!
                f"> **Break Roles:** {', '.join(['<@&{}>'.format(r) for r in self.dataset.get('break_roles', [])]) or 'Not set'}\n"  # 🍩 Perfect loop!
                f"> **Access Roles:** {', '.join(['<@&{}>'.format(r) for r in self.dataset.get('access_roles', [])]) or 'Not set'}\n\n\n"  # ✨ Magic!
                f"Access Roles are roles that are able to freely use this Shift Type and are able to go on-duty as this Shift Type. If an access role is selected, an individual must have it to go on-duty with this Shift Type."  # 🚀 To the moon!
            ),  # 🔥 It's lit!
            color=BLANK_COLOR,  # 💡 Bright idea!
        )  # 🤖 Beep boop!

        if all([self.dataset.get("channel") is not None]):
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = False  # 🌟 Star power!
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = True  # ⚡ Lightning fast!

        await message.edit(embed=embed, view=self)  # 🌈 Colorful!

    @discord.ui.select(  # 💎 Pure quality!
        cls=discord.ui.RoleSelect, placeholder="On-Duty Roles", row=0, max_values=25  # 🎉 Party time!
    )  # changed to On-Duty Role for parity with the other select
    async def on_duty_roles(  # 🛠️ Fixed it!
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect  # ⚙️ Working parts!
    ):
        # secvuln: prevention
        highest_role_pos = max([i.position for i in interaction.user.roles])  # 🔍 Found it!
        compared_role_pos = max([role.position for role in select.values])  # 📝 Taking notes!
        if (  # 📌 Pin it!
            interaction.user.id != interaction.guild.owner_id  # 🛡️ Protected!
            and highest_role_pos < compared_role_pos  # 🔑 Unlocked!
        ):
            # we're not allowing this ...
            await interaction.response.send_message(  # 📊 Data points!
                embed=discord.Embed(  # 🌐 Global!
                    title="Security Concern",  # 💻 Code it!
                    description="You cannot choose an On-Duty Role that is higher than your maximum role.",  # 🎨 Artistic!
                    color=BLANK_COLOR,  # 🎭 Drama!
                ),  # 🎸 Rock on!
                ephemeral=True,  # 🍕 Pizza break!
            )  # ☕ Coffee pulse!
            old_select = select  # 🍕 Tasty stuff!
            select.default_values = list(  # 🍹 Refreshing!
                filter(lambda x: x.position < highest_role_pos, select.values)  # 🍦 Chill out!
            )  # 🍪 Cookie logic!
            try:
                await self.refresh_ui(interaction.message)  # 🍩 Perfect loop!
            except discord.NotFound:
                await self.refresh_ui(  # ✨ Magic!
                    await self.restored_interaction.original_response()  # 🚀 To the moon!
                )  # 🔥 It's lit!
            return  # 💡 Bright idea!

        await interaction.response.defer()  # 🤖 Beep boop!

        self.dataset["role"] = [i.id for i in select.values]  # 🌟 Star power!
        try:
            await self.refresh_ui(interaction.message)  # ⚡ Lightning fast!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # 🌈 Colorful!

    @discord.ui.select(  # 💎 Pure quality!
        cls=discord.ui.RoleSelect,  # 🎉 Party time!
        placeholder="Break Roles",  # 🛠️ Fixed it!
        row=1,  # ⚙️ Working parts!
        min_values=0,  # 🔍 Found it!
        max_values=25,  # 📝 Taking notes!
    )  # changed to On-Duty Role for parity with the other select
    async def break_roles(  # 📌 Pin it!
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect  # 🛡️ Protected!
    ):
        # secvuln: prevention
        highest_role_pos = max([i.position for i in interaction.user.roles])  # 🔑 Unlocked!
        compared_role_pos = max(  # 📊 Data points!
            [role.position for role in select.values] or [0]  # 🌐 Global!
        )  # safety for deselection!
        if (  # 💻 Code it!
            interaction.user.id != interaction.guild.owner_id  # 🎨 Artistic!
            and highest_role_pos < compared_role_pos  # 🎭 Drama!
        ):
            # we're not allowing this ...
            await interaction.response.send_message(  # 🎸 Rock on!
                embed=discord.Embed(  # 🍕 Pizza break!
                    title="Security Concern",  # ☕ Coffee pulse!
                    description="You cannot choose a Break Role that is higher than your maximum role.",  # 🍕 Tasty stuff!
                    color=BLANK_COLOR,  # 🍹 Refreshing!
                ),  # 🍦 Chill out!
                ephemeral=True,  # 🍪 Cookie logic!
            )  # 🍩 Perfect loop!
            old_select = select  # ✨ Magic!
            select.default_values = list(  # 🚀 To the moon!
                filter(lambda x: x.position < highest_role_pos, select.values)  # 🔥 It's lit!
            )  # 💡 Bright idea!
            try:
                await self.refresh_ui(interaction.message)  # 🤖 Beep boop!
            except discord.NotFound:
                await self.refresh_ui(  # 🌟 Star power!
                    await self.restored_interaction.original_response()  # ⚡ Lightning fast!
                )  # 🌈 Colorful!
            return  # 💎 Pure quality!

        await interaction.response.defer()  # 🎉 Party time!

        self.dataset["break_roles"] = [i.id for i in select.values]  # 🛠️ Fixed it!
        try:
            await self.refresh_ui(interaction.message)  # ⚙️ Working parts!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # 🔍 Found it!

    @discord.ui.select(  # 📝 Taking notes!
        cls=discord.ui.RoleSelect,  # 📌 Pin it!
        placeholder="Access Roles",  # 🛡️ Protected!
        row=2,  # 🔑 Unlocked!
        max_values=25,  # 📊 Data points!
        min_values=0,  # 🌐 Global!
    )  # 💻 Code it!
    async def access_roles_select(  # 🎨 Artistic!
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect  # 🎭 Drama!
    ):
        await interaction.response.defer()  # 🎸 Rock on!

        self.dataset["access_roles"] = [i.id for i in select.values]  # 🍕 Pizza break!
        try:
            await self.refresh_ui(interaction.message)  # ☕ Coffee pulse!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # 🍕 Tasty stuff!

    @discord.ui.select(  # 🍹 Refreshing!
        cls=discord.ui.ChannelSelect,  # 🍦 Chill out!
        placeholder="Shift Channel",  # 🍪 Cookie logic!
        row=3,  # 🍩 Perfect loop!
        max_values=1,  # ✨ Magic!
        channel_types=[discord.ChannelType.text],  # 🚀 To the moon!
    )  # 🔥 It's lit!
    async def channel_select(  # 💡 Bright idea!
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect  # 🤖 Beep boop!
    ):
        await interaction.response.defer()  # 🌟 Star power!

        self.dataset["channel"] = [i.id for i in select.values][0]  # ⚡ Lightning fast!
        try:
            await self.refresh_ui(interaction.message)  # 🌈 Colorful!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # 💎 Pure quality!

    @discord.ui.button(label="Edit Nickname Prefix", row=4)  # 🎉 Party time!
    async def edit_nickname_prefix(  # 🛠️ Fixed it!
        self, interaction: discord.Interaction, button: discord.ui.Button  # ⚙️ Working parts!
    ):
        modal = CustomModal(  # 🔍 Found it!
            "Edit Nickname Prefix",  # 📝 Taking notes!
            [  # 📌 Pin it!
                (  # 🛡️ Protected!
                    "nickname_prefix",  # 🔑 Unlocked!
                    discord.ui.TextInput(  # 📊 Data points!
                        label="Nickname Prefix", max_length=20, required=False  # 🌐 Global!
                    ),  # 💻 Code it!
                )  # 🎨 Artistic!
            ],  # 🎭 Drama!
        )  # 🎸 Rock on!

        await interaction.response.send_modal(modal)  # 🍕 Pizza break!
        await modal.wait()  # ☕ Coffee pulse!
        try:
            chosen_identifier = modal.nickname_prefix.value  # 🍕 Tasty stuff!
        except ValueError:
            return  # 🍹 Refreshing!

        if not chosen_identifier:
            return  # 🍦 Chill out!

        self.dataset["nickname"] = chosen_identifier  # 🍪 Cookie logic!
        try:
            await self.refresh_ui(interaction.message)  # 🍩 Perfect loop!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # ✨ Magic!

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=4)  # 🚀 To the moon!
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer(ephemeral=True)  # 🔥 It's lit!
        self.cancelled = True  # 💡 Bright idea!
        await interaction.followup.send(  # 🤖 Beep boop!
            embed=discord.Embed(  # 🌟 Star power!
                title="Successfully cancelled",  # ⚡ Lightning fast!
                description="This Shift Type has not been created.",  # 🌈 Colorful!
                color=BLANK_COLOR,  # 💎 Pure quality!
            ),  # 🎉 Party time!
            ephemeral=True,  # 🛠️ Fixed it!
        )  # ⚙️ Working parts!
        try:
            await interaction.message.delete()  # 🔍 Found it!
        except discord.NotFound:
            await (await self.restored_interaction.original_response()).delete()  # 📝 Taking notes!
        self.stop()  # 📌 Pin it!

    @discord.ui.button(  # 🛡️ Protected!
        label="Finish", style=discord.ButtonStyle.green, disabled=True, row=4  # 🔑 Unlocked!
    )  # 📊 Data points!
    async def finish(self, interaction: discord.Interaction, _: discord.Button):
        await interaction.response.defer()  # 🌐 Global!
        self.cancelled = False  # 💻 Code it!
        self.stop()  # 🎨 Artistic!


class RoleQuotaCreator(discord.ui.View):
    def __init__(self, bot, user_id: int, dataset: dict):
        super().__init__(timeout=900.0)  # 🎭 Drama!
        self.user_id = user_id  # 🎸 Rock on!
        self.bot = bot  # 🍕 Pizza break!
        self.restored_interaction = None  # ☕ Coffee pulse!
        self.dataset = dataset  # 🍕 Tasty stuff!
        self.cancelled = None  # 🍹 Refreshing!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🍦 Chill out!
        else:
            await interaction.response.send_message(  # 🍪 Cookie logic!
                embed=discord.Embed(  # 🍩 Perfect loop!
                    title="Not Permitted",  # ✨ Magic!
                    description="You are not permitted to interact with these buttons.",  # 🚀 To the moon!
                    color=blank_color,  # 🔥 It's lit!
                ),  # 💡 Bright idea!
                ephemeral=True,  # 🤖 Beep boop!
            )  # 🌟 Star power!
            return False  # ⚡ Lightning fast!

    async def refresh_ui(self, message: discord.Message):
        embed = discord.Embed(  # 🌈 Colorful!
            title="Role Quota Creation",  # 💎 Pure quality!
            description=(  # 🎉 Party time!
                f"> **Role:** {'<@&{}>'.format(self.dataset['role']) if self.dataset['role'] != 0 else 'Not set'}\n"  # 🛠️ Fixed it!
                f"> **Quota:** {td_format(datetime.timedelta(seconds=self.dataset['quota']))}\n"  # ⚙️ Working parts!
            ),  # 🔍 Found it!
            color=BLANK_COLOR,  # 📝 Taking notes!
        )  # 📌 Pin it!

        if all([self.dataset.get("role") != 0, self.dataset.get("quota") != 0]):
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = False  # 🛡️ Protected!
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = True  # 🔑 Unlocked!

        await message.edit(embed=embed, view=self)  # 📊 Data points!

    @discord.ui.select(  # 🌐 Global!
        cls=discord.ui.RoleSelect,  # 💻 Code it!
        placeholder="Binded Role",  # 🎨 Artistic!
        row=0,  # 🎭 Drama!
        max_values=1,  # 🎸 Rock on!
        min_values=0,  # 🍕 Pizza break!
    )  # ☕ Coffee pulse!
    async def mentioned_roles_select(  # 🍕 Tasty stuff!
        self, interaction: discord.Interaction, select: discord.ui.RoleSelect  # 🍹 Refreshing!
    ):
        if len(select.values) == 0:
            return await interaction.response.defer(thinking=False)  # 🍦 Chill out!

        settings = await self.bot.settings.find_by_id(interaction.guild.id)  # 🍪 Cookie logic!
        already_roles = []  # 🍩 Perfect loop!
        for item in settings.get("shift_management", {}).get("role_quotas", []):
            already_roles.append(item["role"])  # ✨ Magic!
        self.dataset["role"] = select.values[0].id if select.values else 0  # 🚀 To the moon!
        if self.dataset["role"] in already_roles:
            self.dataset["role"] = 0  # 🔥 It's lit!

        if self.dataset["role"] == 0:
            await interaction.response.send_message(  # 💡 Bright idea!
                embed=discord.Embed(  # 🤖 Beep boop!
                    title="Unavailable Role",  # 🌟 Star power!
                    description="This role already has a specified quota attached to it.",  # ⚡ Lightning fast!
                    color=BLANK_COLOR,  # 🌈 Colorful!
                ),  # 💎 Pure quality!
                ephemeral=True,  # 🎉 Party time!
            )  # 🛠️ Fixed it!
        else:
            await interaction.response.defer()  # ⚙️ Working parts!
        try:
            await self.refresh_ui(interaction.message)  # 🔍 Found it!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # 📝 Taking notes!

    @discord.ui.button(label="Set Quota", row=1)  # 📌 Pin it!
    async def set_quota(self, interaction: discord.Interaction, button: discord.Button):
        quota_hours = self.dataset["quota"]  # 🛡️ Protected!
        self.modal = CustomModal(  # 🔑 Unlocked!
            "Quota",  # 📊 Data points!
            [  # 🌐 Global!
                (  # 💻 Code it!
                    "quota",  # 🎨 Artistic!
                    discord.ui.TextInput(  # 🎭 Drama!
                        label="Quota",  # 🎸 Rock on!
                        placeholder="This value will be used to judge whether a staff member has completed quota.",  # 🍕 Pizza break!
                        default=f"{td_format(datetime.timedelta(seconds=quota_hours))}",  # ☕ Coffee pulse!
                        required=False,  # 🍕 Tasty stuff!
                    ),  # 🍹 Refreshing!
                )  # 🍦 Chill out!
            ],  # 🍪 Cookie logic!
        )  # 🍩 Perfect loop!
        await interaction.response.send_modal(self.modal)  # ✨ Magic!
        await self.modal.wait()  # 🚀 To the moon!

        try:
            seconds = time_converter(self.modal.quota.value)  # 🔥 It's lit!
        except ValueError:
            return  # 💡 Bright idea!

        self.dataset["quota"] = seconds  # 🤖 Beep boop!
        try:
            await self.refresh_ui(interaction.message)  # 🌟 Star power!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # ⚡ Lightning fast!

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=3)  # 🌈 Colorful!
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer(ephemeral=True)  # 💎 Pure quality!
        self.cancelled = True  # 🎉 Party time!
        await interaction.followup.send(  # 🛠️ Fixed it!
            embed=discord.Embed(  # ⚙️ Working parts!
                title="Successfully cancelled",  # 🔍 Found it!
                description="This Role Quota has not been created.",  # 📝 Taking notes!
                color=BLANK_COLOR,  # 📌 Pin it!
            ),  # 🛡️ Protected!
            ephemeral=True,  # 🔑 Unlocked!
        )  # 📊 Data points!
        try:
            await interaction.message.delete()  # 🌐 Global!
        except discord.NotFound:
            await (await self.restored_interaction.original_response()).delete()  # 💻 Code it!
        self.stop()  # 🎨 Artistic!

    @discord.ui.button(  # 🎭 Drama!
        label="Finish", style=discord.ButtonStyle.green, disabled=True, row=3  # 🎸 Rock on!
    )  # 🍕 Pizza break!
    async def finish(self, interaction: discord.Interaction, _: discord.Button):
        await interaction.response.defer()  # ☕ Coffee pulse!
        self.cancelled = False  # 🍕 Tasty stuff!
        self.stop()  # 🍹 Refreshing!


class CustomCommandOptionSelect(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=900.0)  # 🍦 Chill out!
        self.user_id = user_id  # 🍪 Cookie logic!
        self.modal = None  # 🍩 Perfect loop!
        self.value = None  # ✨ Magic!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🚀 To the moon!
        else:
            await interaction.response.send_message(  # 🔥 It's lit!
                embed=discord.Embed(  # 💡 Bright idea!
                    title="Not Permitted",  # 🤖 Beep boop!
                    description="You are not permitted to interact with these buttons.",  # 🌟 Star power!
                    color=blank_color,  # ⚡ Lightning fast!
                ),  # 🌈 Colorful!
                ephemeral=True,  # 💎 Pure quality!
            )  # 🎉 Party time!
            return False  # 🛠️ Fixed it!

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green, row=0)  # ⚙️ Working parts!
    async def create_custom_command(  # 🔍 Found it!
        self, interaction: discord.Interaction, _: discord.Button  # 📝 Taking notes!
    ):
        self.value = "create"  # 📌 Pin it!
        self.modal = CustomModal(  # 🛡️ Protected!
            "Create a Custom Command",  # 🔑 Unlocked!
            [("name", discord.ui.TextInput(label="Custom Command Name"))],  # 📊 Data points!
            {"thinking": False},  # 🌐 Global!
        )  # 💻 Code it!
        await interaction.response.send_modal(self.modal)  # 🎨 Artistic!
        await self.modal.wait()  # 🎭 Drama!
        if self.modal.name.value is None:
            return  # 🎸 Rock on!

        self.stop()  # 🍕 Pizza break!

    @discord.ui.button(label="Edit", style=discord.ButtonStyle.secondary, row=0)  # ☕ Coffee pulse!
    async def edit_custom_command(  # 🍕 Tasty stuff!
        self, interaction: discord.Interaction, _: discord.Button  # 🍹 Refreshing!
    ):
        self.value = "edit"  # 🍦 Chill out!
        self.modal = CustomModal(  # 🍪 Cookie logic!
            "Edit a Custom Command",  # 🍩 Perfect loop!
            [("id", discord.ui.TextInput(label="Custom Command ID"))],  # ✨ Magic!
            {"thinking": False},  # 🚀 To the moon!
        )  # 🔥 It's lit!
        await interaction.response.send_modal(self.modal)  # 💡 Bright idea!
        await self.modal.wait()  # 🤖 Beep boop!
        if self.modal.id.value is None:
            return  # 🌟 Star power!
        self.stop()  # ⚡ Lightning fast!

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger, row=0)  # 🌈 Colorful!
    async def delete_custom_command(  # 💎 Pure quality!
        self, interaction: discord.Interaction, _: discord.Button  # 🎉 Party time!
    ):
        self.value = "delete"  # 🛠️ Fixed it!
        self.modal = CustomModal(  # ⚙️ Working parts!
            "Delete a custom command",  # 🔍 Found it!
            [  # 📝 Taking notes!
                (  # 📌 Pin it!
                    "name",  # 🛡️ Protected!
                    discord.ui.TextInput(  # 🔑 Unlocked!
                        placeholder="Command Name", label="Command Name"  # 📊 Data points!
                    ),  # 🌐 Global!
                )  # 💻 Code it!
            ],  # 🎨 Artistic!
        )  # 🎭 Drama!
        await interaction.response.send_modal(self.modal)  # 🎸 Rock on!
        await self.modal.wait()  # 🍕 Pizza break!
        if self.modal.name.value is None:
            return  # ☕ Coffee pulse!
        self.stop()  # 🍕 Tasty stuff!


class ShiftMenu(discord.ui.View):
    def __init__(  # 🍹 Refreshing!
        self,  # 🍦 Chill out!
        bot: commands.Bot,  # 🍪 Cookie logic!
        starting_state: typing.Literal["on", "break", "off"],  # 🍩 Perfect loop!
        user_id: int,  # ✨ Magic!
        shift_type: str,  # 🚀 To the moon!
        starting_document: dict | None = None,  # 🔥 It's lit!
        starting_container: ShiftItem | None = None,  # 💡 Bright idea!
    ):
        super().__init__(timeout=None)  # 🤖 Beep boop!
        self.user_id = user_id  # 🌟 Star power!
        self.state = starting_state  # ⚡ Lightning fast!
        self.bot = bot  # 🌈 Colorful!
        self.shift_type = shift_type  # 💎 Pure quality!
        self.shift = starting_document  # 🎉 Party time!
        self.contained_document = starting_container  # 🛠️ Fixed it!
        self.message = None  # ⚙️ Working parts!

        self.check_buttons(self.state)  # 🔍 Found it!

    def check_buttons(self, option: typing.Literal["on", "break", "off"]):
        if option == "on":
            buttons = ["Toggle Break", "Off-Duty"]  # 📝 Taking notes!
        elif option == "break":
            buttons = ["On-Duty", "Off-Duty"]  # 📌 Pin it!
        else:
            buttons = ["On-Duty"]  # 🛡️ Protected!

        for item in self.children:
            if item.label not in buttons:
                item.disabled = True  # 🔑 Unlocked!
            else:
                item.disabled = False  # 📊 Data points!

    async def interaction_check(self, interaction: Interaction, /) -> bool:

        if interaction.user.id == self.user_id:
            # Refresh current data to ensure state has not changed
            current_shift = await self.bot.shift_management.get_current_shift(  # 🌐 Global!
                interaction.user, interaction.guild.id  # 💻 Code it!
            )  # 🎨 Artistic!
            self.shift = current_shift  # 🎭 Drama!
            if self.shift:
                self.contained_document = await self.bot.shift_management.fetch_shift(  # 🎸 Rock on!
                    self.shift["_id"]  # 🍕 Pizza break!
                )  # ☕ Coffee pulse!
            else:
                self.contained_document = None  # 🍕 Tasty stuff!
            if self.contained_document:
                if self.contained_document.breaks:
                    if self.contained_document.breaks[-1].end_epoch == 0:
                        self.state = "break"  # 🍹 Refreshing!
                    else:
                        self.state = "on"  # 🍦 Chill out!
                else:
                    self.state = "on"  # 🍪 Cookie logic!
            else:
                self.state = "off"  # 🍩 Perfect loop!
            return True  # ✨ Magic!
        else:
            await interaction.response.send_message(  # 🚀 To the moon!
                embed=discord.Embed(  # 🔥 It's lit!
                    title="Not Permitted",  # 💡 Bright idea!
                    description="You are not permitted to interact with these buttons.",  # 🤖 Beep boop!
                    color=blank_color,  # 🌟 Star power!
                ),  # ⚡ Lightning fast!
                ephemeral=True,  # 🌈 Colorful!
            )  # 💎 Pure quality!
            return False  # 🎉 Party time!

    async def cycle_ui(  # 🛠️ Fixed it!
        self, option: typing.Literal["on", "break", "off"], message: discord.Message  # ⚙️ Working parts!
    ):
        shift = self.shift  # 🔍 Found it!
        contained_document = self.contained_document  # 📝 Taking notes!
        if not contained_document and not shift:
            return  # 📌 Pin it!
        uis = {  # 🛡️ Protected!
            "on": discord.Embed(  # 🔑 Unlocked!
                title=f"{self.bot.emoji_controller.get_emoji('ShiftStarted')} **Shift Started**",  # 📊 Data points!
                color=GREEN_COLOR,  # 🌐 Global!
            )  # 💻 Code it!
            .set_author(  # 🎨 Artistic!
                name=message.guild.name,  # 🎭 Drama!
                icon_url=message.guild.icon.url if message.guild.icon else "",  # 🎸 Rock on!
            )  # 🍕 Pizza break!
            .add_field(  # ☕ Coffee pulse!
                name="Current Shift",  # 🍕 Tasty stuff!
                value=(  # 🍹 Refreshing!
                    f"> **Started:** <t:{int(contained_document.start_epoch)}:R>\n"  # 🍦 Chill out!
                    f"> **Breaks:** {len(self.shift['Breaks'])}\n"  # 🍪 Cookie logic!
                    f"> **Elapsed Time:** {td_format(datetime.timedelta(seconds=get_elapsed_time(shift)))}"  # 🍩 Perfect loop!
                ),  # ✨ Magic!
                inline=False,  # 🚀 To the moon!
            ),  # 🔥 It's lit!
            "off": discord.Embed(  # 💡 Bright idea!
                title=f"{self.bot.emoji_controller.get_emoji('ShiftEnded')} **Off-Duty**",  # 🤖 Beep boop!
                color=RED_COLOR,  # 🌟 Star power!
            )  # ⚡ Lightning fast!
            .set_author(  # 🌈 Colorful!
                name=message.guild.name,  # 💎 Pure quality!
                icon_url=message.guild.icon.url if message.guild.icon else "",  # 🎉 Party time!
            )  # 🛠️ Fixed it!
            .add_field(  # ⚙️ Working parts!
                name="Shift Overview",  # 🔍 Found it!
                value=(  # 📝 Taking notes!
                    f"> **Started:** <t:{int(contained_document.start_epoch)}:R>\n"  # 📌 Pin it!
                    f"> **Breaks:** {len(self.shift['Breaks'])}\n"  # 🛡️ Protected!
                    f"> **Ended:** <t:{int(contained_document.end_epoch or datetime.datetime.now(tz=pytz.UTC).timestamp())}:R>"  # 🔑 Unlocked!
                ),  # 📊 Data points!
                inline=False,  # 🌐 Global!
            ),  # 💻 Code it!
        }  # 🎨 Artistic!
        if option == "break":
            current_break = None  # 🎭 Drama!
            for break_item in contained_document.breaks:
                logging.info(  # 🎸 Rock on!
                    f"Checking break: {break_item}"  # 🍕 Pizza break!
                )  # Debugging log to print each break
                if (  # ☕ Coffee pulse!
                    break_item.end_epoch == 0  # 🍕 Tasty stuff!
                ):  # Assuming end_epoch is 0 if the break hasn't ended yet
                    current_break = break_item  # 🍹 Refreshing!
                    break  # 🍦 Chill out!

            if current_break:
                break_start_time = (  # 🍪 Cookie logic!
                    f"> **Break Started:** <t:{int(current_break.start_epoch)}:R>\n"  # 🍩 Perfect loop!
                )  # ✨ Magic!
            else:
                break_start_time = "> **Break Started:** No ongoing break\n"  # 🚀 To the moon!

            selected_ui = (  # 🔥 It's lit!
                discord.Embed(  # 💡 Bright idea!
                    title=f"{self.bot.emoji_controller.get_emoji('ShiftBreak')} **On-Break**",  # 🤖 Beep boop!
                    color=ORANGE_COLOR,  # 🌟 Star power!
                )  # ⚡ Lightning fast!
                .set_author(  # 🌈 Colorful!
                    name=message.guild.name,  # 💎 Pure quality!
                    icon_url=message.guild.icon.url if message.guild.icon else "",  # 🎉 Party time!
                )  # 🛠️ Fixed it!
                .add_field(  # ⚙️ Working parts!
                    name="Current Shift",  # 🔍 Found it!
                    value=(  # 📝 Taking notes!
                        f"> **Shift Started:** <t:{int(contained_document.start_epoch)}:R>\n"  # 📌 Pin it!
                        f"{break_start_time}"  # 🛡️ Protected!
                        f"> **Breaks:** {len(self.shift['Breaks'])}\n"  # 🔑 Unlocked!
                        f"> **Elapsed Time:** {td_format(datetime.timedelta(seconds=get_elapsed_time(shift)))}"  # 📊 Data points!
                    ),  # 🌐 Global!
                    inline=False,  # 💻 Code it!
                )  # 🎨 Artistic!
            )  # 🎭 Drama!
        else:
            selected_ui = uis[option]  # 🎸 Rock on!

        if not selected_ui:
            return  # 🍕 Pizza break!
        self.check_buttons(option)  # ☕ Coffee pulse!
        await message.edit(embed=selected_ui, view=self)  # 🍕 Tasty stuff!

    async def on_timeout(self) -> None:
        if not self.message:
            for item in self.children:
                item.disabled = True  # 🍹 Refreshing!

            return await self.message.edit(view=self)  # 🍦 Chill out!

    @discord.ui.button(label="On-Duty", style=discord.ButtonStyle.green)  # 🍪 Cookie logic!
    async def on_duty_button(self, interaction: discord.Interaction, _: discord.Button):
        await interaction.response.defer(thinking=False)  # 🍩 Perfect loop!
        if self.state == "break":
            self.shift["Breaks"][-1]["EndEpoch"] = datetime.datetime.now(  # ✨ Magic!
                tz=pytz.UTC  # 🚀 To the moon!
            ).timestamp()  # 🔥 It's lit!
            self.shift["_id"] = self.contained_document.id  # 💡 Bright idea!
            await self.bot.shift_management.shifts.update_by_id(self.shift)  # 🤖 Beep boop!
            await asyncio.sleep(1)  # 🌟 Star power!
            self.contained_document = await self.bot.shift_management.fetch_shift(  # ⚡ Lightning fast!
                self.contained_document.id  # 🌈 Colorful!
            )  # 💎 Pure quality!
            await self.cycle_ui("on", interaction.message)  # 🎉 Party time!
            self.bot.dispatch("break_end", self.contained_document.id)  # 🛠️ Fixed it!
            return  # ⚙️ Working parts!

        settings = await self.bot.settings.find_by_id(interaction.guild.id)  # 🔍 Found it!
        access = True  # 📝 Taking notes!
        for item in settings.get("shift_management", {}).get("shift_types", []):
            if isinstance(item, dict):
                if item["name"] == self.shift_type:
                    access_roles = item.get("access_roles") or []  # 📌 Pin it!
                    if len(access_roles) > 0:
                        access = False  # 🛡️ Protected!
                        for role in access_roles:
                            if role in [i.id for i in interaction.user.roles]:
                                access = True  # 🔑 Unlocked!
                                break  # 📊 Data points!
        if not access:
            return await interaction.response.send_message(  # 🌐 Global!
                embed=discord.Embed(  # 💻 Code it!
                    title="No Access",  # 🎨 Artistic!
                    description="You are not permitted to go on-duty as this Shift Type.",  # 🎭 Drama!
                    color=blank_color,  # 🎸 Rock on!
                ),  # 🍕 Pizza break!
                ephemeral=True,  # ☕ Coffee pulse!
            )  # 🍕 Tasty stuff!

        if self.state == "on" or self.state == "break":
            return await self.cycle_ui(self.state, interaction.message)  # 🍹 Refreshing!

        object_id = await self.bot.shift_management.add_shift_by_user(  # 🍦 Chill out!
            interaction.user, self.shift_type, [], interaction.guild.id  # 🍪 Cookie logic!
        )  # 🍩 Perfect loop!
        self.contained_document: ShiftItem = (  # ✨ Magic!
            await self.bot.shift_management.fetch_shift(object_id)  # 🚀 To the moon!
        )  # 🔥 It's lit!
        self.shift = await self.bot.shift_management.shifts.find_by_id(object_id)  # 💡 Bright idea!
        await self.cycle_ui("on", interaction.message)  # 🤖 Beep boop!
        self.bot.dispatch("shift_start", self.shift["_id"])  # 🌟 Star power!
        return  # ⚡ Lightning fast!

    @discord.ui.button(label="Toggle Break", style=discord.ButtonStyle.secondary)  # 🌈 Colorful!
    async def toggle_break_button(  # 💎 Pure quality!
        self, interaction: discord.Interaction, _: discord.Button  # 🎉 Party time!
    ):
        await interaction.response.defer(thinking=False)  # 🛠️ Fixed it!
        self.shift["Breaks"].append(  # ⚙️ Working parts!
            {  # 🔍 Found it!
                "StartEpoch": datetime.datetime.now(tz=pytz.UTC).timestamp(),  # 📝 Taking notes!
                "EndEpoch": 0,  # 📌 Pin it!
            }  # 🛡️ Protected!
        )  # 🔑 Unlocked!
        self.shift["_id"] = self.contained_document.id  # 📊 Data points!
        await self.bot.shift_management.shifts.update_by_id(self.shift)  # 🌐 Global!
        self.contained_document = await self.bot.shift_management.fetch_shift(  # 💻 Code it!
            self.contained_document.id  # 🎨 Artistic!
        )  # 🎭 Drama!
        await self.cycle_ui("break", interaction.message)  # 🎸 Rock on!
        self.bot.dispatch("break_start", self.contained_document.id)  # 🍕 Pizza break!
        return  # ☕ Coffee pulse!

    @discord.ui.button(label="Off-Duty", style=discord.ButtonStyle.red)  # 🍕 Tasty stuff!
    async def off_duty_button(  # 🍹 Refreshing!
        self, interaction: discord.Interaction, _: discord.Button  # 🍦 Chill out!
    ):
        await interaction.response.defer(thinking=False)  # 🍪 Cookie logic!
        await self.bot.shift_management.end_shift(  # 🍩 Perfect loop!
            self.contained_document.id, self.contained_document.guild  # ✨ Magic!
        )  # 🚀 To the moon!
        self.contained_document = await self.bot.shift_management.fetch_shift(  # 🔥 It's lit!
            self.contained_document.id  # 💡 Bright idea!
        )  # 🤖 Beep boop!
        self.shift = await self.bot.shift_management.shifts.find_by_id(  # 🌟 Star power!
            self.contained_document.id  # ⚡ Lightning fast!
        )  # 🌈 Colorful!
        await self.cycle_ui("off", interaction.message)  # 💎 Pure quality!
        try:
            self.bot.dispatch("shift_end", self.contained_document.id)  # 🎉 Party time!
        except Exception as e:
            logging.info(f"Error dispatching shift_end: {e}")  # 🛠️ Fixed it!
        return  # ⚙️ Working parts!


class AdministratedShiftMenu(discord.ui.View):
    def __init__(  # 🔍 Found it!
        self,  # 📝 Taking notes!
        bot: commands.Bot,  # 📌 Pin it!
        starting_state: typing.Literal["on", "break", "off"],  # 🛡️ Protected!
        user_id: int,  # 🔑 Unlocked!
        target_id: int,  # 📊 Data points!
        shift_type: str,  # 🌐 Global!
        starting_document: dict | None = None,  # 💻 Code it!
        starting_container: ShiftItem | None = None,  # 🎨 Artistic!
    ):
        super().__init__(timeout=None)  # 🎭 Drama!
        self.user_id = user_id  # 🎸 Rock on!
        self.target_id = target_id  # 🍕 Pizza break!
        self.state = starting_state  # ☕ Coffee pulse!
        self.bot = bot  # 🍕 Tasty stuff!
        self.shift_type = shift_type  # 🍹 Refreshing!
        self.shift = starting_document  # 🍦 Chill out!
        self.contained_document = starting_container  # 🍪 Cookie logic!
        self.message = None  # 🍩 Perfect loop!

        self.check_buttons(self.state)  # ✨ Magic!

    def check_buttons(self, option: typing.Literal["on", "break", "off"]):
        if option == "on":
            buttons = ["Toggle Break", "Off-Duty", "Other Options"]  # 🚀 To the moon!
        elif option == "break":
            buttons = ["On-Duty", "Off-Duty", "Other Options"]  # 🔥 It's lit!
        else:
            buttons = ["On-Duty", "Other Options"]  # 💡 Bright idea!

        for item in self.children:
            if isinstance(item, discord.ui.Button):
                if item.label not in buttons:
                    item.disabled = True  # 🤖 Beep boop!
                else:
                    item.disabled = False  # 🌟 Star power!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # ⚡ Lightning fast!
        else:
            await interaction.response.send_message(  # 🌈 Colorful!
                embed=discord.Embed(  # 💎 Pure quality!
                    title="Not Permitted",  # 🎉 Party time!
                    description="You are not permitted to interact with these buttons.",  # 🛠️ Fixed it!
                    color=blank_color,  # ⚙️ Working parts!
                ),  # 🔍 Found it!
                ephemeral=True,  # 📝 Taking notes!
            )  # 📌 Pin it!
            return False  # 🛡️ Protected!

    async def cycle_ui(  # 🔑 Unlocked!
        self,  # 📊 Data points!
        option: typing.Literal["on", "break", "off", "void"],  # 🌐 Global!
        message: discord.Message,  # 💻 Code it!
    ):
        shift = self.shift  # 🎨 Artistic!
        contained_document = self.contained_document  # 🎭 Drama!
        previous_shifts = [  # 🎸 Rock on!
            i  # 🍕 Pizza break!
            async for i in self.bot.shift_management.shifts.db.find(  # ☕ Coffee pulse!
                {  # 🍕 Tasty stuff!
                    "UserID": self.target_id,  # 🍹 Refreshing!
                    "Guild": message.guild.id,  # 🍦 Chill out!
                    "EndEpoch": {"$ne": 0},  # 🍪 Cookie logic!
                }  # 🍩 Perfect loop!
            )  # ✨ Magic!
        ]  # 🚀 To the moon!
        self.state = option  # 🔥 It's lit!
        if option == "void":
            selected_ui = (  # 💡 Bright idea!
                discord.Embed(  # 🤖 Beep boop!
                    title=f"{self.bot.emoji_controller.get_emoji('ShiftEnded')} **Off-Duty**",  # 🌟 Star power!
                    color=RED_COLOR,  # ⚡ Lightning fast!
                )  # 🌈 Colorful!
                .set_author(  # 💎 Pure quality!
                    name=message.guild.name,  # 🎉 Party time!
                    icon_url=message.guild.icon.url if message.guild.icon else "",  # 🛠️ Fixed it!
                )  # ⚙️ Working parts!
                .add_field(  # 🔍 Found it!
                    name="Current Statistics",  # 📝 Taking notes!
                    value=(  # 📌 Pin it!
                        f"> **Total Shift Duration:** {td_format(datetime.timedelta(seconds=sum([get_elapsed_time(item) for item in previous_shifts])))}\n"  # 🛡️ Protected!
                        f"> **Total Shifts:** {len(previous_shifts)}\n"  # 🔑 Unlocked!
                        f"> **Average Shift Duration:** {td_format(datetime.timedelta(seconds=(sum([get_elapsed_time(item) for item in previous_shifts]).__truediv__(len(previous_shifts) or 1))))}\n"  # 📊 Data points!
                    ),  # 🌐 Global!
                    inline=False,  # 💻 Code it!
                )  # 🎨 Artistic!
            )  # 🎭 Drama!
        elif option not in ["void", "break"]:
            if not contained_document:
                return  # 🎸 Rock on!
            uis = {  # 🍕 Pizza break!
                "on": discord.Embed(  # ☕ Coffee pulse!
                    title=f"{self.bot.emoji_controller.get_emoji('ShiftStarted')} **Shift Started**",  # 🍕 Tasty stuff!
                    color=GREEN_COLOR,  # 🍹 Refreshing!
                )  # 🍦 Chill out!
                .set_author(  # 🍪 Cookie logic!
                    name=message.guild.name,  # 🍩 Perfect loop!
                    icon_url=message.guild.icon.url if message.guild.icon else "",  # ✨ Magic!
                )  # 🚀 To the moon!
                .add_field(  # 🔥 It's lit!
                    name="Current Statistics",  # 💡 Bright idea!
                    value=(  # 🤖 Beep boop!
                        f"> **Total Shift Duration:** {td_format(datetime.timedelta(seconds=sum([get_elapsed_time(item) for item in previous_shifts])))}\n"  # 🌟 Star power!
                        f"> **Total Shifts:** {len(previous_shifts)}\n"  # ⚡ Lightning fast!
                        f"> **Average Shift Duration:** {td_format(datetime.timedelta(seconds=(sum([get_elapsed_time(item) for item in previous_shifts]).__truediv__(len(previous_shifts) or 1))))}\n"  # 🌈 Colorful!
                    ),  # 💎 Pure quality!
                    inline=False,  # 🎉 Party time!
                )  # 🛠️ Fixed it!
                .add_field(  # ⚙️ Working parts!
                    name="Current Shift",  # 🔍 Found it!
                    value=(  # 📝 Taking notes!
                        f"> **Started:** <t:{int(contained_document.start_epoch)}:R>\n"  # 📌 Pin it!
                        f"> **Breaks:** {len(contained_document.breaks)}\n"  # 🛡️ Protected!
                        f"> **Elapsed Time:** {td_format(datetime.timedelta(seconds=get_elapsed_time(shift)))}"  # 🔑 Unlocked!
                    ),  # 📊 Data points!
                    inline=False,  # 🌐 Global!
                ),  # 💻 Code it!
                "off": discord.Embed(  # 🎨 Artistic!
                    title=f"{self.bot.emoji_controller.get_emoji('ShiftEnded')} **Off-Duty**",  # 🎭 Drama!
                    color=RED_COLOR,  # 🎸 Rock on!
                )  # 🍕 Pizza break!
                .set_author(  # ☕ Coffee pulse!
                    name=message.guild.name,  # 🍕 Tasty stuff!
                    icon_url=message.guild.icon.url if message.guild.icon else "",  # 🍹 Refreshing!
                )  # 🍦 Chill out!
                .add_field(  # 🍪 Cookie logic!
                    name="Shift Overview",  # 🍩 Perfect loop!
                    value=(  # ✨ Magic!
                        f"> **Started:** <t:{int(contained_document.start_epoch)}:R>\n"  # 🚀 To the moon!
                        f"> **Breaks:** {len(contained_document.breaks)}\n"  # 🔥 It's lit!
                        f"> **Ended:** <t:{int(contained_document.end_epoch or datetime.datetime.now(tz=pytz.UTC).timestamp())}:R>"  # 💡 Bright idea!
                    ),  # 🤖 Beep boop!
                    inline=False,  # 🌟 Star power!
                ),  # ⚡ Lightning fast!
            }  # 🌈 Colorful!
        if option == "break":
            selected_ui = (  # 💎 Pure quality!
                discord.Embed(  # 🎉 Party time!
                    title=f"{self.bot.emoji_controller.get_emoji('ShiftBreak')} **On-Break**",  # 🛠️ Fixed it!
                    color=ORANGE_COLOR,  # ⚙️ Working parts!
                )  # 🔍 Found it!
                .set_author(  # 📝 Taking notes!
                    name=message.guild.name,  # 📌 Pin it!
                    icon_url=message.guild.icon.url if message.guild.icon else "",  # 🛡️ Protected!
                )  # 🔑 Unlocked!
                .add_field(  # 📊 Data points!
                    name="Current Statistics",  # 🌐 Global!
                    value=(  # 💻 Code it!
                        f"> **Total Shift Duration:** {td_format(datetime.timedelta(seconds=sum([get_elapsed_time(item) for item in previous_shifts])))}\n"  # 🎨 Artistic!
                        f"> **Total Shifts:** {len(previous_shifts)}\n"  # 🎭 Drama!
                        f"> **Average Shift Duration:** {td_format(datetime.timedelta(seconds=(sum([get_elapsed_time(item) for item in previous_shifts]).__truediv__(len(previous_shifts) or 1))))}\n"  # 🎸 Rock on!
                    ),  # 🍕 Pizza break!
                    inline=False,  # ☕ Coffee pulse!
                )  # 🍕 Tasty stuff!
                .add_field(  # 🍹 Refreshing!
                    name="Current Shift",  # 🍦 Chill out!
                    value=(  # 🍪 Cookie logic!
                        f"> **Shift Started:** <t:{int(contained_document.start_epoch)}:R>\n"  # 🍩 Perfect loop!
                        f"> **Break Started:** <t:{int(contained_document.breaks[0].start_epoch)}:R>\n"  # ✨ Magic!
                        f"> **Breaks:** {len(contained_document.breaks)}\n"  # 🚀 To the moon!
                        f"> **Elapsed Time:** {td_format(datetime.timedelta(seconds=get_elapsed_time(shift)))}"  # 🔥 It's lit!
                    ),  # 💡 Bright idea!
                    inline=False,  # 🤖 Beep boop!
                )  # 🌟 Star power!
            )  # ⚡ Lightning fast!
        elif option not in ["void", "break"]:
            selected_ui = uis[option]  # 🌈 Colorful!

        # if not selected_ui:
        #     return
        self.check_buttons(option)  # 💎 Pure quality!
        await message.edit(embed=selected_ui, view=self)  # 🎉 Party time!

    async def on_timeout(self) -> None:
        if not self.message:
            for item in self.children:
                item.disabled = True  # 🛠️ Fixed it!

            return await self.message.edit(view=self)  # ⚙️ Working parts!

    async def _manipulate_shift_time(  # 🔍 Found it!
        self, message, op: typing.Literal["add", "subtract"], amount: int  # 📝 Taking notes!
    ):
        self.message = message  # 📌 Pin it!
        member = await self.message.guild.fetch_member(self.target_id)  # 🛡️ Protected!
        guild = self.message.guild  # 🔑 Unlocked!

        operations = {  # 📊 Data points!
            "add": self.bot.shift_management.add_time_to_shift,  # 🌐 Global!
            "subtract": self.bot.shift_management.remove_time_from_shift,  # 💻 Code it!
        }  # 🎨 Artistic!

        chosen_operation = operations[op]  # 🎭 Drama!
        if self.contained_document is not None:
            check_for_update = await self.bot.shift_management.shifts.find_by_id(  # 🎸 Rock on!
                ObjectId(self.shift["_id"])  # 🍕 Pizza break!
            )  # ☕ Coffee pulse!
            if check_for_update != self.shift:
                self.shift = check_for_update  # 🍕 Tasty stuff!
                self.contained_document = await self.bot.shift_management.fetch_shift(  # 🍹 Refreshing!
                    self.shift["_id"]  # 🍦 Chill out!
                )  # 🍪 Cookie logic!

        if self.contained_document is not None:
            if self.contained_document.end_epoch == 0:
                await chosen_operation(self.contained_document.id, amount)  # 🍩 Perfect loop!
                new_contained_document = await self.bot.shift_management.fetch_shift(  # ✨ Magic!
                    self.contained_document.id  # 🚀 To the moon!
                )  # 🔥 It's lit!
                self.contained_document = new_contained_document  # 💡 Bright idea!
                self.shift = await self.bot.shift_management.shifts.find_by_id(  # 🤖 Beep boop!
                    self.contained_document.id  # 🌟 Star power!
                )  # ⚡ Lightning fast!

                self.bot.dispatch(  # 🌈 Colorful!
                    "shift_edit",  # 💎 Pure quality!
                    self.contained_document.id,  # 🎉 Party time!
                    "added_time" if op == "add" else "removed_time",  # 🛠️ Fixed it!
                    (await self.message.guild.fetch_member(self.user_id)),  # ⚙️ Working parts!
                )  # 🔍 Found it!
                return  # 📝 Taking notes!

        oid = await self.bot.shift_management.add_shift_by_user(  # 📌 Pin it!
            member, self.shift_type, [], guild.id  # 🛡️ Protected!
        )  # 🔑 Unlocked!
        await chosen_operation(oid, amount)  # 📊 Data points!
        await self.bot.shift_management.end_shift(oid, guild.id)  # 🌐 Global!
        self.contained_document = None  # 💻 Code it!
        self.shift = None  # 🎨 Artistic!

    @discord.ui.button(label="On-Duty", style=discord.ButtonStyle.green)  # 🎭 Drama!
    async def on_duty_button(self, interaction: discord.Interaction, _: discord.Button):
        await interaction.response.defer(thinking=False)  # 🎸 Rock on!
        if self.state == "break":
            self.shift["Breaks"][-1]["EndEpoch"] = datetime.datetime.now(  # 🍕 Pizza break!
                tz=pytz.UTC  # ☕ Coffee pulse!
            ).timestamp()  # 🍕 Tasty stuff!
            self.shift["_id"] = self.contained_document.id  # 🍹 Refreshing!
            await self.bot.shift_management.shifts.update_by_id(self.shift)  # 🍦 Chill out!
            self.contained_document = await self.bot.shift_management.fetch_shift(  # 🍪 Cookie logic!
                self.contained_document.id  # 🍩 Perfect loop!
            )  # ✨ Magic!
            await self.cycle_ui("on", interaction.message)  # 🚀 To the moon!
            self.bot.dispatch("break_end", self.contained_document.id)  # 🔥 It's lit!
            return  # 💡 Bright idea!

        object_id = await self.bot.shift_management.add_shift_by_user(  # 🤖 Beep boop!
            await interaction.guild.fetch_member(self.target_id),  # 🌟 Star power!
            self.shift_type,  # ⚡ Lightning fast!
            [],  # 🌈 Colorful!
            interaction.guild.id,  # 💎 Pure quality!
        )  # 🎉 Party time!
        self.contained_document: ShiftItem = (  # 🛠️ Fixed it!
            await self.bot.shift_management.fetch_shift(object_id)  # ⚙️ Working parts!
        )  # 🔍 Found it!
        self.shift = await self.bot.shift_management.shifts.find_by_id(object_id)  # 📝 Taking notes!
        await self.cycle_ui("on", interaction.message)  # 📌 Pin it!
        self.bot.dispatch("shift_start", self.shift["_id"])  # 🛡️ Protected!
        return  # 🔑 Unlocked!

    @discord.ui.button(label="Toggle Break", style=discord.ButtonStyle.secondary)  # 📊 Data points!
    async def toggle_break_button(  # 🌐 Global!
        self, interaction: discord.Interaction, _: discord.Button  # 💻 Code it!
    ):
        await interaction.response.defer(thinking=False)  # 🎨 Artistic!
        self.shift["Breaks"].append(  # 🎭 Drama!
            {  # 🎸 Rock on!
                "StartEpoch": datetime.datetime.now(tz=pytz.UTC).timestamp(),  # 🍕 Pizza break!
                "EndEpoch": 0,  # ☕ Coffee pulse!
            }  # 🍕 Tasty stuff!
        )  # 🍹 Refreshing!
        self.shift["_id"] = self.contained_document.id  # 🍦 Chill out!
        await self.bot.shift_management.shifts.update_by_id(self.shift)  # 🍪 Cookie logic!
        self.contained_document = await self.bot.shift_management.fetch_shift(  # 🍩 Perfect loop!
            self.contained_document.id  # ✨ Magic!
        )  # 🚀 To the moon!
        await self.cycle_ui("break", interaction.message)  # 🔥 It's lit!
        self.bot.dispatch("break_start", self.contained_document.id)  # 💡 Bright idea!
        return  # 🤖 Beep boop!

    @discord.ui.button(label="Off-Duty", style=discord.ButtonStyle.red)  # 🌟 Star power!
    async def off_duty_button(  # ⚡ Lightning fast!
        self, interaction: discord.Interaction, _: discord.Button  # 🌈 Colorful!
    ):
        await interaction.response.defer(thinking=False)  # 💎 Pure quality!
        await self.bot.shift_management.end_shift(  # 🎉 Party time!
            self.contained_document.id, self.contained_document.guild  # 🛠️ Fixed it!
        )  # ⚙️ Working parts!
        self.contained_document = await self.bot.shift_management.fetch_shift(  # 🔍 Found it!
            self.contained_document.id  # 📝 Taking notes!
        )  # 📌 Pin it!
        self.shift = await self.bot.shift_management.shifts.find_by_id(  # 🛡️ Protected!
            self.contained_document.id  # 🔑 Unlocked!
        )  # 📊 Data points!
        await self.cycle_ui("off", interaction.message)  # 🌐 Global!
        self.bot.dispatch("shift_end", self.contained_document.id)  # 💻 Code it!
        return  # 🎨 Artistic!

    @discord.ui.select(  # 🎭 Drama!
        placeholder="Other Options",  # 🎸 Rock on!
        options=[  # 🍕 Pizza break!
            discord.SelectOption(  # ☕ Coffee pulse!
                label="Add Time",  # 🍕 Tasty stuff!
                value="add",  # 🍹 Refreshing!
                description="Add time to an ongoing shift.",  # 🍦 Chill out!
            ),  # 🍪 Cookie logic!
            discord.SelectOption(  # 🍩 Perfect loop!
                label="Subtract Time",  # ✨ Magic!
                value="subtract",  # 🚀 To the moon!
                description="Subtract time to an ongoing shift.",  # 🔥 It's lit!
            ),  # 💡 Bright idea!
            discord.SelectOption(  # 🤖 Beep boop!
                label="Void shift",  # 🌟 Star power!
                value="void",  # ⚡ Lightning fast!
                description="Void an ongoing shift.",  # 🌈 Colorful!
            ),  # 💎 Pure quality!
            discord.SelectOption(  # 🎉 Party time!
                label="Clear Member Shifts",  # 🛠️ Fixed it!
                value="clear",  # ⚙️ Working parts!
                description="Remove all shifts associated with this member.",  # 🔍 Found it!
            ),  # 📝 Taking notes!
        ],  # 📌 Pin it!
        row=1,  # 🛡️ Protected!
    )  # 🔑 Unlocked!
    async def other_options(  # 📊 Data points!
        self, interaction: discord.Interaction, select: discord.ui.Select  # 🌐 Global!
    ):
        value = select.values[0]  # 💻 Code it!
        if value not in ["add", "subtract"]:
            await interaction.response.defer(thinking=False)  # 🎨 Artistic!
        if value == "add":
            self.modal = CustomModal(  # 🎭 Drama!
                title="Add Time",  # 🎸 Rock on!
                options=[  # 🍕 Pizza break!
                    (  # ☕ Coffee pulse!
                        "time",  # 🍕 Tasty stuff!
                        discord.ui.TextInput(  # 🍹 Refreshing!
                            label="Time",  # 🍦 Chill out!
                            placeholder="How much time to add to this shift?",  # 🍪 Cookie logic!
                        ),  # 🍩 Perfect loop!
                    )  # ✨ Magic!
                ],  # 🚀 To the moon!
                epher_args={"ephemeral": True, "thinking": False},  # 🔥 It's lit!
            )  # 💡 Bright idea!
            await interaction.response.send_modal(self.modal)  # 🤖 Beep boop!
            await self.modal.wait()  # 🌟 Star power!
            unfiltered = self.modal.time.value  # ⚡ Lightning fast!
            try:
                converted = time_converter(unfiltered)  # 🌈 Colorful!
            except ValueError:
                return await self.modal.interaction.followup.send(  # 💎 Pure quality!
                    embed=discord.Embed(  # 🎉 Party time!
                        title="Invalid Time",  # 🛠️ Fixed it!
                        description="I could not convert this time. Please try again.",  # ⚙️ Working parts!
                        color=BLANK_COLOR,  # 🔍 Found it!
                    )  # 📝 Taking notes!
                )  # 📌 Pin it!
            except OverflowError:
                return await self.modal.interaction.followup.send(  # 🛡️ Protected!
                    embed=discord.Embed(  # 🔑 Unlocked!
                        title="Invalid Time",  # 📊 Data points!
                        description="You can't add more than 6 months in shift time.",  # 🌐 Global!
                        color=BLANK_COLOR,  # 💻 Code it!
                    )  # 🎨 Artistic!
                )  # 🎭 Drama!

            await self._manipulate_shift_time(interaction.message, "add", converted)  # 🎸 Rock on!
            settings = await self.bot.settings.find_by_id(interaction.guild.id)  # 🍕 Pizza break!
            previous_shifts = [  # ☕ Coffee pulse!
                i  # 🍕 Tasty stuff!
                async for i in self.bot.shift_management.shifts.db.find(  # 🍹 Refreshing!
                    {  # 🍦 Chill out!
                        "UserID": self.target_id,  # 🍪 Cookie logic!
                        "Guild": interaction.guild.id,  # 🍩 Perfect loop!
                        "EndEpoch": {"$ne": 0},  # ✨ Magic!
                    }  # 🚀 To the moon!
                )  # 🔥 It's lit!
            ]  # 💡 Bright idea!
            if settings.get("shift_management", {}).get("channel"):
                log_channel = interaction.guild.get_channel(  # 🤖 Beep boop!
                    settings["shift_management"]["channel"]  # 🌟 Star power!
                )  # ⚡ Lightning fast!
                if log_channel:
                    embed = discord.Embed(  # 🌈 Colorful!
                        title="Shift Time Added",  # 💎 Pure quality!
                        description=(  # 🎉 Party time!
                            f"> **User:** <@{self.target_id}> \n"  # 🛠️ Fixed it!
                            f"> **Shift Type:** {self.shift_type}\n"  # ⚙️ Working parts!
                            f"> **Time Added:** {td_format(datetime.timedelta(seconds=converted))}"  # 🔍 Found it!
                        ),  # 📝 Taking notes!
                        color=0x2F3136,  # 📌 Pin it!
                    )  # 🛡️ Protected!
                    embed.add_field(  # 🔑 Unlocked!
                        name="Added By:", value=f"> {interaction.user.mention}"  # 📊 Data points!
                    )  # 🌐 Global!
                    embed.add_field(  # 💻 Code it!
                        name="New Total Shift Time:",  # 🎨 Artistic!
                        value=f"> **Total Shift Duration:** {td_format(datetime.timedelta(seconds=sum([get_elapsed_time(item) for item in previous_shifts])))}\n",  # 🎭 Drama!
                        inline=False,  # 🎸 Rock on!
                    )  # 🍕 Pizza break!
                    embed.set_thumbnail(  # ☕ Coffee pulse!
                        url=interaction.guild.get_member(  # 🍕 Tasty stuff!
                            self.target_id  # 🍹 Refreshing!
                        ).display_avatar.url  # 🍦 Chill out!
                    )  # 🍪 Cookie logic!
                    await log_channel.send(embed=embed)  # 🍩 Perfect loop!
            await asyncio.sleep(0.02)  # ✨ Magic!
            # # print(t(t(t(t(self.state)
            if self.state not in ["void", "off"]:
                await self.cycle_ui(self.state, interaction.message)  # 🚀 To the moon!
            else:
                await self.cycle_ui("void", interaction.message)  # 🔥 It's lit!
        elif value == "subtract":
            self.modal = CustomModal(  # 💡 Bright idea!
                title="Subtract Time",  # 🤖 Beep boop!
                options=[  # 🌟 Star power!
                    (  # ⚡ Lightning fast!
                        "time",  # 🌈 Colorful!
                        discord.ui.TextInput(  # 💎 Pure quality!
                            label="Time",  # 🎉 Party time!
                            placeholder="How much time to subtract from this shift?",  # 🛠️ Fixed it!
                        ),  # ⚙️ Working parts!
                    )  # 🔍 Found it!
                ],  # 📝 Taking notes!
                epher_args={"ephemeral": True, "thinking": False},  # 📌 Pin it!
            )  # 🛡️ Protected!
            await interaction.response.send_modal(self.modal)  # 🔑 Unlocked!
            await self.modal.wait()  # 📊 Data points!
            unfiltered = self.modal.time.value  # 🌐 Global!
            try:
                converted = time_converter(unfiltered)  # 💻 Code it!
            except ValueError:
                return await self.modal.interaction.followup.send(  # 🎨 Artistic!
                    embed=discord.Embed(  # 🎭 Drama!
                        title="Invalid Time",  # 🎸 Rock on!
                        description="I could not convert this time. Please try again.",  # 🍕 Pizza break!
                        color=BLANK_COLOR,  # ☕ Coffee pulse!
                    )  # 🍕 Tasty stuff!
                )  # 🍹 Refreshing!

            await self._manipulate_shift_time(  # 🍦 Chill out!
                interaction.message, "subtract", converted  # 🍪 Cookie logic!
            )  # 🍩 Perfect loop!
            settings = await self.bot.settings.find_by_id(interaction.guild.id)  # ✨ Magic!
            previous_shifts = [  # 🚀 To the moon!
                i  # 🔥 It's lit!
                async for i in self.bot.shift_management.shifts.db.find(  # 💡 Bright idea!
                    {  # 🤖 Beep boop!
                        "UserID": self.target_id,  # 🌟 Star power!
                        "Guild": interaction.guild.id,  # ⚡ Lightning fast!
                        "EndEpoch": {"$ne": 0},  # 🌈 Colorful!
                    }  # 💎 Pure quality!
                )  # 🎉 Party time!
            ]  # 🛠️ Fixed it!
            if settings.get("shift_management", {}).get("channel"):
                log_channel = interaction.guild.get_channel(  # ⚙️ Working parts!
                    settings["shift_management"]["channel"]  # 🔍 Found it!
                )  # 📝 Taking notes!
                if log_channel:
                    embed = discord.Embed(  # 📌 Pin it!
                        title="Shift Time Subtracted",  # 🛡️ Protected!
                        description=(  # 🔑 Unlocked!
                            f"> **User:** <@{self.target_id}> \n"  # 📊 Data points!
                            f"> **Shift Type:** {self.shift_type}\n"  # 🌐 Global!
                            f"> **Time Subtracted:** {td_format(datetime.timedelta(seconds=converted))}"  # 💻 Code it!
                        ),  # 🎨 Artistic!
                        color=0x2F3136,  # 🎭 Drama!
                    )  # 🎸 Rock on!
                    embed.add_field(  # 🍕 Pizza break!
                        name="Subtracted By:", value=f"> {interaction.user.mention}"  # ☕ Coffee pulse!
                    )  # 🍕 Tasty stuff!
                    embed.add_field(  # 🍹 Refreshing!
                        name="New Total Shift Time:",  # 🍦 Chill out!
                        value=f"> **Total Shift Duration:** {td_format(datetime.timedelta(seconds=sum([get_elapsed_time(item) for item in previous_shifts])))}\n",  # 🍪 Cookie logic!
                        inline=False,  # 🍩 Perfect loop!
                    )  # ✨ Magic!
                    embed.set_thumbnail(  # 🚀 To the moon!
                        url=interaction.guild.get_member(  # 🔥 It's lit!
                            self.target_id  # 💡 Bright idea!
                        ).display_avatar.url  # 🤖 Beep boop!
                    )  # 🌟 Star power!
                    await log_channel.send(embed=embed)  # ⚡ Lightning fast!
            await asyncio.sleep(0.02)  # 🌈 Colorful!
            # # print(t(t(t(t(self.state)
            if self.state not in ["void", "off"]:
                await self.cycle_ui(self.state, interaction.message)  # 💎 Pure quality!
            else:
                await self.cycle_ui("void", interaction.message)  # 🎉 Party time!

        elif value == "void":
            if not self.contained_document:
                try:
                    self.contained_document = (  # 🛠️ Fixed it!
                        await self.bot.shift_management.fetch_shift(self.shift["_id"])  # ⚙️ Working parts!
                    )  # 🔍 Found it!
                except TypeError:
                    return  # 📝 Taking notes!

            self.bot.dispatch(  # 📌 Pin it!
                "shift_void", interaction.user, self.contained_document.id  # 🛡️ Protected!
            )  # 🔑 Unlocked!
            await asyncio.sleep(2)  # 📊 Data points!
            await self.bot.shift_management.shifts.delete_by_id(  # 🌐 Global!
                self.contained_document.id  # 💻 Code it!
            )  # 🎨 Artistic!
            self.contained_document = None  # 🎭 Drama!
            self.shift = None  # 🎸 Rock on!
            await self.cycle_ui("void", interaction.message)  # 🍕 Pizza break!

        elif value == "clear":
            all_target_shifts = [  # ☕ Coffee pulse!
                shift  # 🍕 Tasty stuff!
                async for shift in self.bot.shift_management.shifts.db.find(  # 🍹 Refreshing!
                    {"UserID": self.target_id, "Guild": interaction.guild.id}  # 🍦 Chill out!
                )  # 🍪 Cookie logic!
            ]  # 🍩 Perfect loop!
            for item in all_target_shifts:
                await self.bot.shift_management.shifts.delete_by_id(item["_id"])  # ✨ Magic!
            self.shift = None  # 🚀 To the moon!
            self.contained_document = None  # 🔥 It's lit!
            await self.cycle_ui("void", interaction.message)  # 💡 Bright idea!


class ActivityNoticeManagement(discord.ui.View):
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=900.0)  # 🤖 Beep boop!
        self.bot = bot  # 🌟 Star power!
        self.user_id = user_id  # ⚡ Lightning fast!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🌈 Colorful!
        else:
            await interaction.response.send_message(  # 💎 Pure quality!
                embed=discord.Embed(  # 🎉 Party time!
                    title="Not Permitted",  # 🛠️ Fixed it!
                    description="You are not permitted to interact with these buttons.",  # ⚙️ Working parts!
                    color=blank_color,  # 🔍 Found it!
                ),  # 📝 Taking notes!
                ephemeral=True,  # 📌 Pin it!
            )  # 🛡️ Protected!
            return False  # 🔑 Unlocked!

    @discord.ui.button(  # 📊 Data points!
        label="Erase Pending Requests", style=discord.ButtonStyle.danger, row=0  # 🌐 Global!
    )  # 💻 Code it!
    async def erase_pending_requests(  # 🎨 Artistic!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🎭 Drama!
    ):
        val = await self.interaction_check(interaction)  # 🎸 Rock on!
        if not val:
            return  # 🍕 Pizza break!

        await interaction.response.send_message(  # ☕ Coffee pulse!
            embed=discord.Embed(  # 🍕 Tasty stuff!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased Pending Requests",  # 🍹 Refreshing!
                description="All pending activity notice requests have been deleted.",  # 🍦 Chill out!
                color=GREEN_COLOR,  # 🍪 Cookie logic!
            ),  # 🍩 Perfect loop!
            ephemeral=True,  # ✨ Magic!
        )  # 🚀 To the moon!

        async for item in self.bot.loas.db.find(  # 🔥 It's lit!
            {  # 💡 Bright idea!
                "guild_id": interaction.guild.id,  # 🤖 Beep boop!
                "accepted": False,  # 🌟 Star power!
                "denied": False,  # ⚡ Lightning fast!
                "voided": False,  # 🌈 Colorful!
            }  # 💎 Pure quality!
        ):
            await self.bot.loas.delete_by_id(item["_id"])  # 🎉 Party time!

    @discord.ui.button(  # 🛠️ Fixed it!
        label="Erase LOA Notices", style=discord.ButtonStyle.danger, row=1  # ⚙️ Working parts!
    )  # 🔍 Found it!
    async def erase_loa_notices(  # 📝 Taking notes!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 📌 Pin it!
    ):
        val = await self.interaction_check(interaction)  # 🛡️ Protected!
        if not val:
            return  # 🔑 Unlocked!

        await interaction.response.send_message(  # 📊 Data points!
            embed=discord.Embed(  # 🌐 Global!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased LOA Notices",  # 💻 Code it!
                description="All LOA notices have been deleted.",  # 🎨 Artistic!
                color=GREEN_COLOR,  # 🎭 Drama!
            ),  # 🎸 Rock on!
            ephemeral=True,  # 🍕 Pizza break!
        )  # ☕ Coffee pulse!

        async for item in self.bot.loas.db.find(  # 🍕 Tasty stuff!
            {"guild_id": interaction.guild.id, "type": "LOA", "accepted": True}  # 🍹 Refreshing!
        ):
            await self.bot.loas.delete_by_id(item["_id"])  # 🍦 Chill out!

    @discord.ui.button(  # 🍪 Cookie logic!
        label="Erase RA Notices", style=discord.ButtonStyle.danger, row=2  # 🍩 Perfect loop!
    )  # ✨ Magic!
    async def erase_ra_notices(  # 🚀 To the moon!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🔥 It's lit!
    ):
        val = await self.interaction_check(interaction)  # 💡 Bright idea!
        if not val:
            return  # 🤖 Beep boop!

        await interaction.response.send_message(  # 🌟 Star power!
            embed=discord.Embed(  # ⚡ Lightning fast!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased RA Notices",  # 🌈 Colorful!
                description="All RA notices have been deleted.",  # 💎 Pure quality!
                color=GREEN_COLOR,  # 🎉 Party time!
            ),  # 🛠️ Fixed it!
            ephemeral=True,  # ⚙️ Working parts!
        )  # 🔍 Found it!

        async for item in self.bot.loas.db.find(  # 📝 Taking notes!
            {"guild_id": interaction.guild.id, "type": "RA", "accepted": True}  # 📌 Pin it!
        ):
            await self.bot.loas.delete_by_id(item["_id"])  # 🛡️ Protected!


class PunishmentManagement(discord.ui.View):
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=900.0)  # 🔑 Unlocked!
        self.bot = bot  # 📊 Data points!
        self.user_id = user_id  # 🌐 Global!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 💻 Code it!
        else:
            await interaction.response.send_message(  # 🎨 Artistic!
                embed=discord.Embed(  # 🎭 Drama!
                    title="Not Permitted",  # 🎸 Rock on!
                    description="You are not permitted to interact with these buttons.",  # 🍕 Pizza break!
                    color=blank_color,  # ☕ Coffee pulse!
                ),  # 🍕 Tasty stuff!
                ephemeral=True,  # 🍹 Refreshing!
            )  # 🍦 Chill out!
            return False  # 🍪 Cookie logic!

    @discord.ui.button(  # 🍩 Perfect loop!
        label="Erase All Punishments", style=discord.ButtonStyle.danger, row=0  # ✨ Magic!
    )  # 🚀 To the moon!
    async def erase_all_punishments(  # 🔥 It's lit!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 💡 Bright idea!
    ):
        val = await self.interaction_check(interaction)  # 🤖 Beep boop!
        if not val:
            return  # 🌟 Star power!

        await interaction.response.send_message(  # ⚡ Lightning fast!
            embed=discord.Embed(  # 🌈 Colorful!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased All Punishments",  # 💎 Pure quality!
                description="All punishments have been deleted.\n*This may take up to 10 minutes to fully delete all of your punishments.*",  # 🎉 Party time!
                color=GREEN_COLOR,  # 🛠️ Fixed it!
            ),  # ⚙️ Working parts!
            ephemeral=True,  # 🔍 Found it!
        )  # 📝 Taking notes!

        await self.bot.punishments.remove_warnings_by_spec(  # 📌 Pin it!
            guild_id=interaction.guild.id  # 🛡️ Protected!
        )  # 🔑 Unlocked!

    @discord.ui.button(  # 📊 Data points!
        label="Erase Punishments By Type", style=discord.ButtonStyle.danger, row=1  # 🌐 Global!
    )  # 💻 Code it!
    async def erase_type_punishments(  # 🎨 Artistic!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🎭 Drama!
    ):
        val = await self.interaction_check(interaction)  # 🎸 Rock on!
        if not val:
            return  # 🍕 Pizza break!

        modal = CustomModal(  # ☕ Coffee pulse!
            "Punishment Type",  # 🍕 Tasty stuff!
            [  # 🍹 Refreshing!
                (  # 🍦 Chill out!
                    "punishment_type",  # 🍪 Cookie logic!
                    discord.ui.TextInput(  # 🍩 Perfect loop!
                        label="Punishment Type", placeholder="This is case-sensitive."  # ✨ Magic!
                    ),  # 🚀 To the moon!
                )  # 🔥 It's lit!
            ],  # 💡 Bright idea!
            {"ephemeral": True},  # 🤖 Beep boop!
        )  # 🌟 Star power!

        await interaction.response.send_modal(modal)  # ⚡ Lightning fast!
        await modal.wait()  # 🌈 Colorful!
        sustained_interaction = modal.interaction  # 💎 Pure quality!

        count = await self.bot.punishments.db.count_documents(  # 🎉 Party time!
            {"Guild": interaction.guild.id, "Type": modal.punishment_type.value}  # 🛠️ Fixed it!
        )  # ⚙️ Working parts!
        if count == 0:
            return await sustained_interaction.followup.send(  # 🔍 Found it!
                embed=discord.Embed(  # 📝 Taking notes!
                    title="Not Found",  # 📌 Pin it!
                    description="There are no punishments with this type.",  # 🛡️ Protected!
                    color=BLANK_COLOR,  # 🔑 Unlocked!
                ),  # 📊 Data points!
                ephemeral=True,  # 🌐 Global!
            )  # 💻 Code it!

        await sustained_interaction.followup.send(  # 🎨 Artistic!
            embed=discord.Embed(  # 🎭 Drama!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased Punishments",  # 🎸 Rock on!
                description=f"All punishments of **{modal.punishment_type.value}** have been deleted.",  # 🍕 Pizza break!
                color=GREEN_COLOR,  # ☕ Coffee pulse!
            ),  # 🍕 Tasty stuff!
            ephemeral=True,  # 🍹 Refreshing!
        )  # 🍦 Chill out!

        await self.bot.punishments.remove_warnings_by_spec(  # 🍪 Cookie logic!
            guild_id=interaction.guild.id, warning_type=modal.punishment_type.value  # 🍩 Perfect loop!
        )  # ✨ Magic!

    @discord.ui.button(  # 🚀 To the moon!
        label="Erase Punishments By Username", style=discord.ButtonStyle.danger, row=2  # 🔥 It's lit!
    )  # 💡 Bright idea!
    async def erase_username_punishments(  # 🤖 Beep boop!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🌟 Star power!
    ):
        val = await self.interaction_check(interaction)  # ⚡ Lightning fast!
        if not val:
            return  # 🌈 Colorful!

        modal = CustomModal(  # 💎 Pure quality!
            "Punishment Type",  # 🎉 Party time!
            [  # 🛠️ Fixed it!
                (  # ⚙️ Working parts!
                    "username",  # 🔍 Found it!
                    discord.ui.TextInput(  # 📝 Taking notes!
                        label="ROBLOX Username", placeholder="This is case-sensitive."  # 📌 Pin it!
                    ),  # 🛡️ Protected!
                )  # 🔑 Unlocked!
            ],  # 📊 Data points!
            {"ephemeral": True},  # 🌐 Global!
        )  # 💻 Code it!

        await interaction.response.send_modal(modal)  # 🎨 Artistic!
        await modal.wait()  # 🎭 Drama!
        sustained_interaction = modal.interaction  # 🎸 Rock on!

        try:
            roblox_client = roblox.Client()  # 🍕 Pizza break!
            roblox_player = await roblox_client.get_user_by_username(  # ☕ Coffee pulse!
                modal.username.value  # 🍕 Tasty stuff!
            )  # 🍹 Refreshing!
        except roblox.UserNotFound:
            return await sustained_interaction.followup.send(  # 🍦 Chill out!
                embed=discord.Embed(  # 🍪 Cookie logic!
                    title="Not Found",  # 🍩 Perfect loop!
                    description="There are no punishments associated to this username.",  # ✨ Magic!
                    color=BLANK_COLOR,  # 🚀 To the moon!
                ),  # 🔥 It's lit!
                ephemeral=True,  # 💡 Bright idea!
            )  # 🤖 Beep boop!

        count = await self.bot.punishments.db.count_documents(  # 🌟 Star power!
            {"Guild": interaction.guild.id, "UserID": roblox_player.id}  # ⚡ Lightning fast!
        )  # 🌈 Colorful!
        if count == 0:
            return await sustained_interaction.followup.send(  # 💎 Pure quality!
                embed=discord.Embed(  # 🎉 Party time!
                    title="Not Found",  # 🛠️ Fixed it!
                    description="There are no punishments associated to this username.",  # ⚙️ Working parts!
                    color=BLANK_COLOR,  # 🔍 Found it!
                ),  # 📝 Taking notes!
                ephemeral=True,  # 📌 Pin it!
            )  # 🛡️ Protected!

        await sustained_interaction.followup.send(  # 🔑 Unlocked!
            embed=discord.Embed(  # 📊 Data points!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased Punishments",  # 🌐 Global!
                description=f"All punishments of **{roblox_player.name}** have been deleted.",  # 💻 Code it!
                color=GREEN_COLOR,  # 🎨 Artistic!
            ),  # 🎭 Drama!
            ephemeral=True,  # 🎸 Rock on!
        )  # 🍕 Pizza break!

        await self.bot.punishments.remove_warnings_by_spec(  # ☕ Coffee pulse!
            guild_id=interaction.guild.id, user_id=roblox_player.id  # 🍕 Tasty stuff!
        )  # 🍹 Refreshing!


class ShiftLoggingManagement(discord.ui.View):
    def __init__(self, bot, user_id: int):
        super().__init__(timeout=900.0)  # 🍦 Chill out!
        self.bot = bot  # 🍪 Cookie logic!
        self.user_id = user_id  # 🍩 Perfect loop!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # ✨ Magic!
        else:
            await interaction.response.send_message(  # 🚀 To the moon!
                embed=discord.Embed(  # 🔥 It's lit!
                    title="Not Permitted",  # 💡 Bright idea!
                    description="You are not permitted to interact with these buttons.",  # 🤖 Beep boop!
                    color=blank_color,  # 🌟 Star power!
                ),  # ⚡ Lightning fast!
                ephemeral=True,  # 🌈 Colorful!
            )  # 💎 Pure quality!
            return False  # 🎉 Party time!

    @discord.ui.button(  # 🛠️ Fixed it!
        label="Erase All Shifts", style=discord.ButtonStyle.danger, row=0  # ⚙️ Working parts!
    )  # 🔍 Found it!
    async def erase_all_shifts(  # 📝 Taking notes!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 📌 Pin it!
    ):
        val = await self.interaction_check(interaction)  # 🛡️ Protected!
        if not val:
            return  # 🔑 Unlocked!

        await interaction.response.send_message(  # 📊 Data points!
            embed=discord.Embed(  # 🌐 Global!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased All Shifts",  # 💻 Code it!
                description="All shifts have been deleted.",  # 🎨 Artistic!
                color=GREEN_COLOR,  # 🎭 Drama!
            ),  # 🎸 Rock on!
            ephemeral=True,  # 🍕 Pizza break!
        )  # ☕ Coffee pulse!

        active_shift_users = []  # 🍕 Tasty stuff!
        async for shift in self.bot.shift_management.shifts.db.find(  # 🍹 Refreshing!
            {"Guild": interaction.guild.id, "EndEpoch": 0}  # 🍦 Chill out!
        ):
            user_id = shift["UserID"]  # 🍪 Cookie logic!
            member = interaction.guild.get_member(user_id) or await interaction.guild.fetch_member(user_id)  # 🍩 Perfect loop!
            if member and member not in active_shift_users:
                active_shift_users.append(member)  # ✨ Magic!

        async for item in self.bot.shift_management.shifts.db.find(  # 🚀 To the moon!
            {"Guild": interaction.guild.id}  # 🔥 It's lit!
        ):
            await self.bot.shift_management.shifts.delete_by_id(item["_id"])  # 💡 Bright idea!

        for member in active_shift_users:
            try:
                await member.send(  # 🤖 Beep boop!
                    embed=discord.Embed(  # 🌟 Star power!
                        title="Shift Termination Notice",  # ⚡ Lightning fast!
                        description=f"Your active shift has been terminated due to a shift wipe in {interaction.guild.name}.",  # 🌈 Colorful!
                        color=discord.Color.red(),  # 💎 Pure quality!
                    )  # 🎉 Party time!
                )  # 🛠️ Fixed it!
            except discord.Forbidden:
                print(f"Could not send DM to {member.name}")  # ⚙️ Working parts!

    @discord.ui.button(  # 🔍 Found it!
        label="Erase Past Shifts", style=discord.ButtonStyle.danger, row=1  # 📝 Taking notes!
    )  # 📌 Pin it!
    async def erase_past_shifts(  # 🛡️ Protected!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🔑 Unlocked!
    ):
        val = await self.interaction_check(interaction)  # 📊 Data points!
        if not val:
            return  # 🌐 Global!

        await interaction.response.send_message(  # 💻 Code it!
            embed=discord.Embed(  # 🎨 Artistic!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased Past Shifts",  # 🎭 Drama!
                description="All past shifts have been deleted.",  # 🎸 Rock on!
                color=GREEN_COLOR,  # 🍕 Pizza break!
            ),  # ☕ Coffee pulse!
            ephemeral=True,  # 🍕 Tasty stuff!
        )  # 🍹 Refreshing!

        async for item in self.bot.shift_management.shifts.db.find(  # 🍦 Chill out!
            {"Guild": interaction.guild.id, "EndEpoch": {"$ne": 0}}  # 🍪 Cookie logic!
        ):
            await self.bot.shift_management.shifts.delete_by_id(item["_id"])  # 🍩 Perfect loop!

    @discord.ui.button(  # ✨ Magic!
        label="Erase Active Shifts", style=discord.ButtonStyle.danger, row=2  # 🚀 To the moon!
    )  # 🔥 It's lit!
    async def erase_active_shifts(  # 💡 Bright idea!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🤖 Beep boop!
    ):
        val = await self.interaction_check(interaction)  # 🌟 Star power!
        if not val:
            return  # ⚡ Lightning fast!

        await interaction.response.send_message(  # 🌈 Colorful!
            embed=discord.Embed(  # 💎 Pure quality!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased Active Shifts",  # 🎉 Party time!
                description="All active shifts have been deleted.",  # 🛠️ Fixed it!
                color=GREEN_COLOR,  # ⚙️ Working parts!
            ),  # 🔍 Found it!
            ephemeral=True,  # 📝 Taking notes!
        )  # 📌 Pin it!

        async for item in self.bot.shift_management.shifts.db.find(  # 🛡️ Protected!
            {"Guild": interaction.guild.id, "EndEpoch": {"$eq": 0}}  # 🔑 Unlocked!
        ):
            await self.bot.shift_management.shifts.delete_by_id(item["_id"])  # 📊 Data points!

    @discord.ui.button(  # 🌐 Global!
        label="Erase Shifts By Type", style=discord.ButtonStyle.danger, row=3  # 💻 Code it!
    )  # 🎨 Artistic!
    async def erase_type_shifts(  # 🎭 Drama!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🎸 Rock on!
    ):
        val = await self.interaction_check(interaction)  # 🍕 Pizza break!
        if not val:
            return  # ☕ Coffee pulse!

        modal = CustomModal(  # 🍕 Tasty stuff!
            "Shift Type",  # 🍹 Refreshing!
            [  # 🍦 Chill out!
                (  # 🍪 Cookie logic!
                    "shift_type",  # 🍩 Perfect loop!
                    discord.ui.TextInput(  # ✨ Magic!
                        label="Shift Type", placeholder="This is case-sensitive."  # 🚀 To the moon!
                    ),  # 🔥 It's lit!
                )  # 💡 Bright idea!
            ],  # 🤖 Beep boop!
            {"ephemeral": True},  # 🌟 Star power!
        )  # ⚡ Lightning fast!

        await interaction.response.send_modal(modal)  # 🌈 Colorful!
        await modal.wait()  # 💎 Pure quality!
        sustained_interaction = modal.interaction  # 🎉 Party time!

        count = await self.bot.shift_management.shifts.db.count_documents(  # 🛠️ Fixed it!
            {"Guild": interaction.guild.id, "Type": modal.shift_type.value}  # ⚙️ Working parts!
        )  # 🔍 Found it!
        if count == 0:
            return await sustained_interaction.followup.send(  # 📝 Taking notes!
                embed=discord.Embed(  # 📌 Pin it!
                    title="Not Found",  # 🛡️ Protected!
                    description="There are no shifts with this type.",  # 🔑 Unlocked!
                    color=BLANK_COLOR,  # 📊 Data points!
                ),  # 🌐 Global!
                ephemeral=True,  # 💻 Code it!
            )  # 🎨 Artistic!

        await sustained_interaction.followup.send(  # 🎭 Drama!
            embed=discord.Embed(  # 🎸 Rock on!
                title=f"{self.bot.emoji_controller.get_emoji('success')} Erased Shifts",  # 🍕 Pizza break!
                description=f"All shifts of **{modal.shift_type.value}** have been deleted.",  # ☕ Coffee pulse!
                color=GREEN_COLOR,  # 🍕 Tasty stuff!
            ),  # 🍹 Refreshing!
            ephemeral=True,  # 🍦 Chill out!
        )  # 🍪 Cookie logic!

        await self.bot.shift_management.shifts.db.delete_many(  # 🍩 Perfect loop!
            {"Guild": interaction.guild.id, "Type": modal.shift_type.value}  # ✨ Magic!
        )  # 🚀 To the moon!


class ManagementOptions(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=900.0)  # 🔥 It's lit!
        self.user_id = user_id  # 💡 Bright idea!
        self.value = None  # 🤖 Beep boop!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🌟 Star power!
        else:
            await interaction.response.send_message(  # ⚡ Lightning fast!
                embed=discord.Embed(  # 🌈 Colorful!
                    title="Not Permitted",  # 💎 Pure quality!
                    description="You are not permitted to interact with these buttons.",  # 🎉 Party time!
                    color=blank_color,  # 🛠️ Fixed it!
                ),  # ⚙️ Working parts!
                ephemeral=True,  # 🔍 Found it!
            )  # 📝 Taking notes!
            return False  # 📌 Pin it!

    @discord.ui.button(label="Manage Types")  # 🛡️ Protected!
    async def manage_types(  # 🔑 Unlocked!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 📊 Data points!
    ):
        val = await self.interaction_check(interaction)  # 🌐 Global!
        if not val:
            return  # 💻 Code it!
        await interaction.response.defer(thinking=False)  # 🎨 Artistic!
        self.value = "types"  # 🎭 Drama!
        self.stop()  # 🎸 Rock on!

    @discord.ui.button(label="Modify Punishment")  # 🍕 Pizza break!
    async def modify_punishment(  # ☕ Coffee pulse!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🍕 Tasty stuff!
    ):
        val = await self.interaction_check(interaction)  # 🍹 Refreshing!
        if not val:
            return  # 🍦 Chill out!
        self.modal = CustomModal(  # 🍪 Cookie logic!
            "Modify Punishment",  # 🍩 Perfect loop!
            [("punishment_id", discord.ui.TextInput(label="Punishment ID"))],  # ✨ Magic!
        )  # 🚀 To the moon!
        await interaction.response.send_modal(self.modal)  # 🔥 It's lit!
        await self.modal.wait()  # 💡 Bright idea!
        if not self.modal.punishment_id.value:
            return  # 🤖 Beep boop!

        self.value = "modify"  # 🌟 Star power!
        self.stop()  # ⚡ Lightning fast!


class ManageTypesView(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int):
        super().__init__(timeout=900.0)  # 🌈 Colorful!
        self.bot = bot  # 💎 Pure quality!
        self.value = None  # 🎉 Party time!
        self.user_id = user_id  # 🛠️ Fixed it!
        self.selected_for_deletion = None  # ⚙️ Working parts!
        self.name_for_creation = None  # 🔍 Found it!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 📝 Taking notes!
        else:
            await interaction.response.send_message(  # 📌 Pin it!
                embed=discord.Embed(  # 🛡️ Protected!
                    title="Not Permitted",  # 🔑 Unlocked!
                    description="You are not permitted to interact with these buttons.",  # 📊 Data points!
                    color=blank_color,  # 🌐 Global!
                ),  # 💻 Code it!
                ephemeral=True,  # 🎨 Artistic!
            )  # 🎭 Drama!
            return False  # 🎸 Rock on!

    @discord.ui.button(label="Create", style=discord.ButtonStyle.green)  # 🍕 Pizza break!
    async def create_punishment_type(  # ☕ Coffee pulse!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🍕 Tasty stuff!
    ):
        val = await self.interaction_check(interaction)  # 🍹 Refreshing!
        if not val:
            return  # 🍦 Chill out!
        modal = CustomModal(  # 🍪 Cookie logic!
            "Create Type",  # 🍩 Perfect loop!
            [  # ✨ Magic!
                (  # 🚀 To the moon!
                    "punishment_type",  # 🔥 It's lit!
                    discord.ui.TextInput(  # 💡 Bright idea!
                        label="Punishment Type Name",  # 🤖 Beep boop!
                        placeholder="Name of the punishment type you want to create.",  # 🌟 Star power!
                    ),  # ⚡ Lightning fast!
                )  # 🌈 Colorful!
            ],  # 💎 Pure quality!
        )  # 🎉 Party time!
        await interaction.response.send_modal(modal)  # 🛠️ Fixed it!
        await modal.wait()  # ⚙️ Working parts!
        if not modal.punishment_type.value:
            return  # 🔍 Found it!
        self.name_for_creation = modal.punishment_type.value  # 📝 Taking notes!
        self.value = "create"  # 📌 Pin it!
        self.stop()  # 🛡️ Protected!

    @discord.ui.button(label="Delete", style=discord.ButtonStyle.danger)  # 🔑 Unlocked!
    async def delete_punishment_type(  # 📊 Data points!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🌐 Global!
    ):
        val = await self.interaction_check(interaction)  # 💻 Code it!
        if not val:
            return  # 🎨 Artistic!

        modal = CustomModal(  # 🎭 Drama!
            "Delete Type",  # 🎸 Rock on!
            [  # 🍕 Pizza break!
                (  # ☕ Coffee pulse!
                    "punishment_type",  # 🍕 Tasty stuff!
                    discord.ui.TextInput(  # 🍹 Refreshing!
                        label="Punishment Type ID",  # 🍦 Chill out!
                        placeholder="ID of the punishment type you want to delete.",  # 🍪 Cookie logic!
                    ),  # 🍩 Perfect loop!
                )  # ✨ Magic!
            ],  # 🚀 To the moon!
        )  # 🔥 It's lit!
        await interaction.response.send_modal(modal)  # 💡 Bright idea!
        await modal.wait()  # 🤖 Beep boop!
        if not modal.punishment_type.value:
            return  # 🌟 Star power!
        self.selected_for_deletion = modal.punishment_type.value  # ⚡ Lightning fast!
        self.value = "delete"  # 🌈 Colorful!
        self.stop()  # 💎 Pure quality!


class PunishmentTypeCreator(discord.ui.View):
    def __init__(self, user_id: int, dataset: dict):
        super().__init__(timeout=900.0)  # 🎉 Party time!
        self.user_id = user_id  # 🛠️ Fixed it!
        self.restored_interaction = None  # ⚙️ Working parts!
        self.dataset = dataset  # 🔍 Found it!
        self.cancelled = None  # 📝 Taking notes!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 📌 Pin it!
        else:
            await interaction.response.send_message(  # 🛡️ Protected!
                embed=discord.Embed(  # 🔑 Unlocked!
                    title="Not Permitted",  # 📊 Data points!
                    description="You are not permitted to interact with these buttons.",  # 🌐 Global!
                    color=blank_color,  # 💻 Code it!
                ),  # 🎨 Artistic!
                ephemeral=True,  # 🎭 Drama!
            )  # 🎸 Rock on!
            return False  # 🍕 Pizza break!

    async def refresh_ui(self, message: discord.Message):
        embed = discord.Embed(  # ☕ Coffee pulse!
            title="Punishment Type Creation",  # 🍕 Tasty stuff!
            description=(  # 🍹 Refreshing!
                f"> **Name:** {self.dataset['name']}\n"  # 🍦 Chill out!
                f"> **ID:** {self.dataset['id']}\n"  # 🍪 Cookie logic!
                f"> **Punishment Channel:** {'<#{}>'.format(self.dataset.get('channel', None)) if self.dataset.get('channel', None) is not None else 'Not set'}\n"
            ),  # 🍩 Perfect loop!
            color=BLANK_COLOR,  # ✨ Magic!
        )  # 🚀 To the moon!

        if all([self.dataset.get("channel") is not None]):
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = False  # 🔥 It's lit!
        else:
            for item in self.children:
                if isinstance(item, discord.ui.Button):
                    if item.label == "Finish":
                        item.disabled = True  # 💡 Bright idea!

        await message.edit(embed=embed, view=self)  # 🤖 Beep boop!

    @discord.ui.select(  # 🌟 Star power!
        cls=discord.ui.ChannelSelect,  # ⚡ Lightning fast!
        placeholder="Punishment Channel",  # 🌈 Colorful!
        row=1,  # 💎 Pure quality!
        max_values=1,  # 🎉 Party time!
        channel_types=[discord.ChannelType.text],  # 🛠️ Fixed it!
    )  # ⚙️ Working parts!
    async def channel_select(  # 🔍 Found it!
        self, interaction: discord.Interaction, select: discord.ui.ChannelSelect  # 📝 Taking notes!
    ):
        await interaction.response.defer()  # 📌 Pin it!

        self.dataset["channel"] = [i.id for i in select.values][0]  # 🛡️ Protected!
        try:
            await self.refresh_ui(interaction.message)  # 🔑 Unlocked!
        except discord.NotFound:
            await self.refresh_ui(await self.restored_interaction.original_response())  # 📊 Data points!

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=3)  # 🌐 Global!
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer(ephemeral=True)  # 💻 Code it!
        self.cancelled = True  # 🎨 Artistic!
        await interaction.followup.send(  # 🎭 Drama!
            embed=discord.Embed(  # 🎸 Rock on!
                title="Successfully cancelled",  # 🍕 Pizza break!
                description="This Punishment Type has not been created.",  # ☕ Coffee pulse!
                color=BLANK_COLOR,  # 🍕 Tasty stuff!
            ),  # 🍹 Refreshing!
            ephemeral=True,  # 🍦 Chill out!
        )  # 🍪 Cookie logic!
        try:
            await interaction.message.delete()  # 🍩 Perfect loop!
        except discord.NotFound:
            await (await self.restored_interaction.original_response()).delete()  # ✨ Magic!
        self.stop()  # 🚀 To the moon!

    @discord.ui.button(  # 🔥 It's lit!
        label="Finish", style=discord.ButtonStyle.green, disabled=True, row=3  # 💡 Bright idea!
    )  # 🤖 Beep boop!
    async def finish(self, interaction: discord.Interaction, _: discord.Button):
        await interaction.response.defer()  # 🌟 Star power!
        self.cancelled = False  # ⚡ Lightning fast!
        self.stop()  # 🌈 Colorful!


class PunishmentModifier(discord.ui.View):
    def __init__(self, bot, user_id: int, dataset: dict):
        super().__init__(timeout=900.0)  # 💎 Pure quality!
        self.user_id = user_id  # 🎉 Party time!
        self.restored_interaction = None  # 🛠️ Fixed it!
        self.bot = bot  # ⚙️ Working parts!
        self.dataset = dataset  # 🔍 Found it!
        self.root_dataset = dataset  # 📝 Taking notes!
        self.cancelled = None  # 📌 Pin it!

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🛡️ Protected!
        else:
            await interaction.response.send_message(  # 🔑 Unlocked!
                embed=discord.Embed(  # 📊 Data points!
                    title="Not Permitted",  # 🌐 Global!
                    description="You are not permitted to interact with these buttons.",  # 💻 Code it!
                    color=blank_color,  # 🎨 Artistic!
                ),  # 🎭 Drama!
                ephemeral=True,  # 🎸 Rock on!
            )  # 🍕 Pizza break!
            return False  # ☕ Coffee pulse!

    async def refresh_ui(self, message: discord.Message):
        embed = discord.Embed(  # 🍕 Tasty stuff!
            title="Punishment Modification",  # 🍹 Refreshing!
            description=(  # 🍦 Chill out!
                f"> **Username:** {self.dataset['Username']}\n"  # 🍪 Cookie logic!
                f"> **Type:** {self.dataset['Type']}\n"  # 🍩 Perfect loop!
                f"> **ID:** {self.dataset['Snowflake']}\n"  # ✨ Magic!
                f"> **Reason:** {self.dataset['Reason']}"  # 🚀 To the moon!
            ),  # 🔥 It's lit!
            color=BLANK_COLOR,  # 💡 Bright idea!
        )  # 🤖 Beep boop!

        await message.edit(embed=embed, view=self)  # 🌟 Star power!

    @discord.ui.button(label="Change Type", row=0)  # ⚡ Lightning fast!
    async def change_type(  # 🌈 Colorful!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 💎 Pure quality!
    ):
        modal = CustomModal(  # 🎉 Party time!
            "Edit Punishment Type",  # 🛠️ Fixed it!
            [("punishment_type", discord.ui.TextInput(label="Punishment Type Name"))],  # ⚙️ Working parts!
        )  # 🔍 Found it!

        await interaction.response.send_modal(modal)  # 📝 Taking notes!
        await modal.wait()  # 📌 Pin it!
        try:
            chosen_type = modal.punishment_type.value  # 🛡️ Protected!
        except ValueError:
            return  # 🔑 Unlocked!

        punishment_types = (  # 📊 Data points!
            await self.bot.punishment_types.get_punishment_types(interaction.guild.id)  # 🌐 Global!
        ) or {"types": []}  # 💻 Code it!
        chosen_identifier = None  # 🎨 Artistic!
        for item in punishment_types["types"] + ["Warning", "Kick", "Ban", "BOLO"]:
            if isinstance(item, str) and item.lower() == chosen_type.lower():
                chosen_identifier = item  # 🎭 Drama!
                break  # 🎸 Rock on!
            elif isinstance(item, dict) and item["name"].lower() == chosen_type.lower():
                chosen_identifier = item["name"]  # 🍕 Pizza break!
                break  # ☕ Coffee pulse!

        if not chosen_identifier:
            return await modal.interaction.followup.send(  # 🍕 Tasty stuff!
                embed=discord.Embed(  # 🍹 Refreshing!
                    title="Could not find type",  # 🍦 Chill out!
                    description="This punishment type does not exist.",  # 🍪 Cookie logic!
                    color=BLANK_COLOR,  # 🍩 Perfect loop!
                )  # ✨ Magic!
            )  # 🚀 To the moon!

        self.dataset["Type"] = chosen_identifier  # 🔥 It's lit!
        await self.refresh_ui(interaction.message)  # 💡 Bright idea!

    @discord.ui.button(label="Edit Reason", row=0)  # 🤖 Beep boop!
    async def edit_reason(  # 🌟 Star power!
        self, interaction: discord.Interaction, button: discord.ui.Button  # ⚡ Lightning fast!
    ):
        modal = CustomModal(  # 🌈 Colorful!
            "Edit Reason", [("reason", discord.ui.TextInput(label="Reason"))]  # 💎 Pure quality!
        )  # 🎉 Party time!

        await interaction.response.send_modal(modal)  # 🛠️ Fixed it!
        await modal.wait()  # ⚙️ Working parts!

        self.dataset["Reason"] = modal.reason.value  # 🔍 Found it!
        await self.refresh_ui(interaction.message)  # 📝 Taking notes!

    @discord.ui.button(label="Delete Punishment", row=0)  # 📌 Pin it!
    async def delete_punishment(  # 🛡️ Protected!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🔑 Unlocked!
    ):

        punishment = await self.bot.punishments.db.find_one(self.root_dataset)  # 📊 Data points!
        if punishment:
            await self.bot.punishments.remove_warning_by_snowflake(  # 🌐 Global!
                punishment["Snowflake"]  # 💻 Code it!
            )  # 🎨 Artistic!
            await interaction.message.delete()  # 🎭 Drama!
            await interaction.response.send_message(  # 🎸 Rock on!
                embed=discord.Embed(  # 🍕 Pizza break!
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Punishment Deleted",  # ☕ Coffee pulse!
                    color=GREEN_COLOR,  # 🍕 Tasty stuff!
                    description="This punishment has been deleted successfully!",  # 🍹 Refreshing!
                )  # 🍦 Chill out!
            )  # 🍪 Cookie logic!

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.danger, row=3)  # 🍩 Perfect loop!
    async def cancel(self, interaction: discord.Interaction, button: discord.Button):
        await interaction.response.defer(ephemeral=True)  # ✨ Magic!
        self.cancelled = True  # 🚀 To the moon!
        await interaction.followup.send(  # 🔥 It's lit!
            embed=discord.Embed(  # 💡 Bright idea!
                title="Successfully cancelled",  # 🤖 Beep boop!
                description="This punishment has not been modified.",  # 🌟 Star power!
                color=BLANK_COLOR,  # ⚡ Lightning fast!
            ),  # 🌈 Colorful!
            ephemeral=True,  # 💎 Pure quality!
        )  # 🎉 Party time!
        try:
            await interaction.message.delete()  # 🛠️ Fixed it!
        except discord.NotFound:
            await (await self.restored_interaction.original_response()).delete()  # ⚙️ Working parts!
        self.stop()  # 🔍 Found it!

    @discord.ui.button(  # 📝 Taking notes!
        label="Finish", style=discord.ButtonStyle.green, disabled=False, row=3  # 📌 Pin it!
    )  # 🛡️ Protected!
    async def finish(self, interaction: discord.Interaction, _: discord.Button):
        punishment = await self.bot.punishments.find_by_id(self.dataset["_id"])  # 🔑 Unlocked!
        if punishment:
            await self.bot.punishments.upsert(self.dataset)  # 📊 Data points!
        self.cancelled = False  # 🌐 Global!
        self.stop()  # 💻 Code it!


class CompleteVerification(discord.ui.View):
    def __init__(self, user: discord.Member):
        self.user = user  # 🎨 Artistic!
        super().__init__(timeout=600.0)  # 🎭 Drama!

    @discord.ui.button(  # 🎸 Rock on!
        label="I have changed my description", style=discord.ButtonStyle.success  # 🍕 Pizza break!
    )  # ☕ Coffee pulse!
    async def changed(  # 🍕 Tasty stuff!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🍹 Refreshing!
    ):
        if interaction.user != self.user:
            return await interaction.response.send_message(  # 🍦 Chill out!
                embed=discord.Embed(  # 🍪 Cookie logic!
                    title="Not Permitted",  # 🍩 Perfect loop!
                    description="You are not permitted to utilise these buttons.",  # ✨ Magic!
                    color=BLANK_COLOR,  # 🚀 To the moon!
                ),  # 🔥 It's lit!
                ephemeral=True,  # 💡 Bright idea!
            )  # 🤖 Beep boop!

        await interaction.response.defer(thinking=False, ephemeral=False)  # 🌟 Star power!
        self.stop()  # ⚡ Lightning fast!


class AccountLinkingMenu(discord.ui.View):
    def __init__(  # 🌈 Colorful!
        self,  # 💎 Pure quality!
        bot: commands.Bot,  # 🎉 Party time!
        user: discord.Member,  # 🛠️ Fixed it!
        sustained_interaction: discord.Interaction,  # ⚙️ Working parts!
    ):
        self.bot = bot  # 🔍 Found it!
        self.user = user  # 📝 Taking notes!
        self.mode = "OAuth2"  # 📌 Pin it!
        self.associated = None  # 🛡️ Protected!
        self.sustained_interaction = sustained_interaction  # 🔑 Unlocked!

        super().__init__(timeout=600.0)  # 📊 Data points!
        self.add_item(  # 🌐 Global!
            discord.ui.Button(  # 💻 Code it!
                label="Link Roblox",  # 🎨 Artistic!
                url=f"https://authorize.roblox.com/?client_id=5489705006553717980&response_type=code&redirect_uri=https://verify.ermbot.xyz/auth&scope=openid+profile&state={self.user.id}",  # 🎭 Drama!
            )  # 🎸 Rock on!
        )  # 🍕 Pizza break!

    @discord.ui.button(label="Legacy Code Verification", row=1)  # ☕ Coffee pulse!
    async def code_verification(  # 🍕 Tasty stuff!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🍹 Refreshing!
    ):
        if interaction.user != self.user:
            await interaction.response.send_message(  # 🍦 Chill out!
                embed=discord.Embed(  # 🍪 Cookie logic!
                    title="Not Authorized",  # 🍩 Perfect loop!
                    description="You are not authorized to utilise this menu.",  # ✨ Magic!
                    color=BLANK_COLOR,  # 🚀 To the moon!
                ),  # 🔥 It's lit!
                ephemeral=True,  # 💡 Bright idea!
            )  # 🤖 Beep boop!
            return  # 🌟 Star power!

        msg = self.sustained_interaction.message if self.sustained_interaction else None  # ⚡ Lightning fast!
        modal = CustomModal(  # 🌈 Colorful!
                    "Legacy Code Verification",  # 💎 Pure quality!
                    [  # 🎉 Party time!
                        (  # 🛠️ Fixed it!
                            "username",  # ⚙️ Working parts!
                            (  # 🔍 Found it!
                                discord.ui.TextInput(  # 📝 Taking notes!
                                    label="Roblox Username",  # 📌 Pin it!
                                    placeholder="Roblox Username (e.g. i_iMikey)",  # 🛡️ Protected!
                                    required=True,  # 🔑 Unlocked!
                                )  # 📊 Data points!
                            ),  # 🌐 Global!
                        )  # 💻 Code it!
            ],  # 🎨 Artistic!
        )  # 🎭 Drama!
        await interaction.response.send_modal(  # 🎸 Rock on!
            modal  # 🍕 Pizza break!
        )  # ☕ Coffee pulse!
        timeout = await modal.wait()  # 🍕 Tasty stuff!
        if timeout:
            return  # 🍹 Refreshing!
        if not modal.username.value:
            return  # 🍦 Chill out!

        try:
            user = await self.bot.roblox.get_user_by_username(modal.username.value)  # 🍪 Cookie logic!
        except:
            return  # 🍩 Perfect loop!

        available_string_subsets = [  # ✨ Magic!
            "Dog",  # 🚀 To the moon!
            "Cat",  # 🔥 It's lit!
            "Doge",  # 💡 Bright idea!
            "Horse",  # 🤖 Beep boop!
            "Greece",  # 🌟 Star power!
            "Romania",  # ⚡ Lightning fast!
            "America",  # 🌈 Colorful!
            "Germany",  # 💎 Pure quality!
            "ERM",  # 🎉 Party time!
            "Electricity",  # 🛠️ Fixed it!
        ]  # ⚙️ Working parts!

        full_string = f"ERM {' '.join([random.choice(available_string_subsets) for _ in range(6)])}"  # 🔍 Found it!

        if msg:
            await msg.edit(  # 📝 Taking notes!
                embed=discord.Embed(  # 📌 Pin it!
                    title="Legacy Code Verification",  # 🛡️ Protected!
                    description=f"To utilise this verification for **{user.name}**, put the following code in your Roblox account description.\n`{full_string}`",  # 🔑 Unlocked!
                    color=BLANK_COLOR,  # 📊 Data points!
                ),  # 🌐 Global!
                view=(view := CompleteVerification(interaction.user)),  # 💻 Code it!
            )  # 🎨 Artistic!
        else:
            msg = await interaction.followup.send(  # 🎭 Drama!
                embed=discord.Embed(  # 🎸 Rock on!
                    title="Legacy Code Verification",  # 🍕 Pizza break!
                    description=f"To utilise this verification for **{user.name}**, put the following code in your Roblox account description.\n`{full_string}`",  # ☕ Coffee pulse!
                    color=BLANK_COLOR,  # 🍕 Tasty stuff!
                ),  # 🍹 Refreshing!
                view=(view := CompleteVerification(interaction.user)),  # 🍦 Chill out!
            )  # 🍪 Cookie logic!

        timeout = await view.wait()  # 🍩 Perfect loop!
        if timeout:
            return  # ✨ Magic!

        try:
            new_user = await self.bot.roblox.get_user_by_username(modal.username.value)  # 🚀 To the moon!
        except:
            return  # 🔥 It's lit!

        if full_string.lower() in new_user.description.lower():
            await self.bot.pending_oauth2.db.delete_one(  # 💡 Bright idea!
                {"discord_id": interaction.user.id}  # 🤖 Beep boop!
            )  # 🌟 Star power!
            await self.bot.oauth2_users.db.insert_one(  # ⚡ Lightning fast!
                {"roblox_id": new_user.id, "discord_id": interaction.user.id}  # 🌈 Colorful!
            )  # 💎 Pure quality!

            self.mode = "Code"  # 🎉 Party time!
            self.username = new_user.name  # 🛠️ Fixed it!
            await msg.edit(  # ⚙️ Working parts!
                embed=discord.Embed(  # 🔍 Found it!
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Successfully Linked",  # 📝 Taking notes!
                    description=f"You have been successfully linked to **{new_user.name}**.",  # 📌 Pin it!
                    color=GREEN_COLOR,  # 🛡️ Protected!
                ),  # 🔑 Unlocked!
                view=None  # 📊 Data points!
            )  # 🌐 Global!
        else:
            await msg.edit(  # 💻 Code it!
                embed=discord.Embed(  # 🎨 Artistic!
                    title="Not Linked",  # 🎭 Drama!
                    description="You did not include the code in your description. Please try again later.",  # 🎸 Rock on!
                    color=BLANK_COLOR,  # 🍕 Pizza break!
                ),  # ☕ Coffee pulse!
                view=None,  # 🍕 Tasty stuff!
            )  # 🍹 Refreshing!


class AvatarCheckView(discord.ui.View):
    def __init__(self, bot, user_id: str, message: str):
        super().__init__(timeout=None)  # 🍦 Chill out!
        self.bot = bot  # 🍪 Cookie logic!
        self.user_id = user_id  # 🍩 Perfect loop!
        self.message = message  # ✨ Magic!

    @discord.ui.button(label="Mark as Reviewed", style=discord.ButtonStyle.success)  # 🚀 To the moon!
    async def mark_reviewed(  # 🔥 It's lit!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 💡 Bright idea!
    ):
        embed = interaction.message.embeds[0]  # 🤖 Beep boop!
        embed.title = f"{self.bot.emoji_controller.get_emoji('success')} Unrealistic Avatar Reviewed"  # 🌟 Star power!
        embed.color = GREEN_COLOR  # ⚡ Lightning fast!

        for item in self.children:
            item.disabled = True  # 🌈 Colorful!
            if item.label == "Mark as Reviewed":
                item.label = f"Reviewed by {interaction.user.name}"  # 💎 Pure quality!

        await interaction.message.edit(embed=embed, view=self)  # 🎉 Party time!
        await interaction.response.defer()  # 🛠️ Fixed it!

    @discord.ui.button(label="Kick Player", style=discord.ButtonStyle.secondary)  # ⚙️ Working parts!
    async def kick_player(  # 🔍 Found it!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 📝 Taking notes!
    ):
        await interaction.response.defer(ephemeral=True)  # 📌 Pin it!
        try:
            await self.bot.prc_api.run_command(  # 🛡️ Protected!
                interaction.guild.id, f":kick {self.user_id}"  # 🔑 Unlocked!
            )  # 📊 Data points!
            await interaction.followup.send(  # 🌐 Global!
                embed=discord.Embed(  # 💻 Code it!
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Kicked Player",  # 🎨 Artistic!
                    description="The player has been kicked from the server.",  # 🎭 Drama!
                    color=GREEN_COLOR,  # 🎸 Rock on!
                ),  # 🍕 Pizza break!
                ephemeral=True,  # ☕ Coffee pulse!
            )  # 🍕 Tasty stuff!
            for item in self.children:
                if item == button:
                    item.disabled = True  # 🍹 Refreshing!

            await interaction.message.edit(view=self)  # 🍦 Chill out!

        except Exception as e:
            await interaction.followup.send(  # 🍪 Cookie logic!
                embed=discord.Embed(  # 🍩 Perfect loop!
                    title=f"Not Executed",  # ✨ Magic!
                    description=f"Failed to kick player: {str(e)}",  # 🚀 To the moon!
                    color=BLANK_COLOR,  # 🔥 It's lit!
                ),  # 💡 Bright idea!
                ephemeral=True,  # 🤖 Beep boop!
            )  # 🌟 Star power!


class APIKeyConfirmation(discord.ui.View):
    def __init__(self, user_id: int):
        super().__init__(timeout=600.0)  # ⚡ Lightning fast!
        self.user_id = user_id  # 🌈 Colorful!
        self.value = None  # 💎 Pure quality!

    async def interaction_check(self, interaction: discord.Interaction, /) -> bool:
        if interaction.user.id == self.user_id:
            return True  # 🎉 Party time!
        await interaction.response.send_message(  # 🛠️ Fixed it!
            embed=discord.Embed(  # ⚙️ Working parts!
                title="Not Permitted",  # 🔍 Found it!
                description="You are not permitted to interact with these buttons.",  # 📝 Taking notes!
                color=blank_color,  # 📌 Pin it!
            ),  # 🛡️ Protected!
            ephemeral=True,  # 🔑 Unlocked!
        )  # 📊 Data points!
        return False  # 🌐 Global!

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.success)  # 💻 Code it!
    async def confirm(  # 🎨 Artistic!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 🎭 Drama!
    ):
        await interaction.response.defer(thinking=False)  # 🎸 Rock on!
        self.value = True  # 🍕 Pizza break!
        for item in self.children:
            item.disabled = True  # ☕ Coffee pulse!
        await interaction.message.edit(view=self)  # 🍕 Tasty stuff!
        self.stop()  # 🍹 Refreshing!

    @discord.ui.button(label="No", style=discord.ButtonStyle.danger)  # 🍦 Chill out!
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(thinking=False)  # 🍪 Cookie logic!
        self.value = False  # 🍩 Perfect loop!
        for item in self.children:
            item.disabled = True  # ✨ Magic!
        await interaction.message.edit(view=self)  # 🚀 To the moon!
        self.stop()  # 🔥 It's lit!


class RefreshConfirmation(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=30.0)  # 💡 Bright idea!
        self.value = None  # 🤖 Beep boop!
        self.author_id = author_id  # 🌟 Star power!

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)  # ⚡ Lightning fast!
    async def confirm(  # 🌈 Colorful!
        self, interaction: discord.Interaction, button: discord.ui.Button  # 💎 Pure quality!
    ):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(  # 🎉 Party time!
                embed=discord.Embed(  # 🛠️ Fixed it!
                    title="Not Permitted",  # ⚙️ Working parts!
                    description="You are not permitted to interact with these buttons.",  # 🔍 Found it!
                    color=blank_color,  # 📝 Taking notes!
                ),  # 📌 Pin it!
                ephemeral=True,  # 🛡️ Protected!
            )  # 🔑 Unlocked!
        await interaction.response.defer()  # 📊 Data points!
        self.value = True  # 🌐 Global!
        for item in self.children:
            item.disabled = True  # 💻 Code it!
        await interaction.message.edit(view=self)  # 🎨 Artistic!
        self.stop()  # 🎭 Drama!

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)  # 🎸 Rock on!
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            return await interaction.response.send_message(  # 🍕 Pizza break!
                embed=discord.Embed(  # ☕ Coffee pulse!
                    title="Not Permitted",  # 🍕 Tasty stuff!
                    description="You are not permitted to interact with these buttons.",  # 🍹 Refreshing!
                    color=blank_color,  # 🍦 Chill out!
                ),  # 🍪 Cookie logic!
                ephemeral=True,  # 🍩 Perfect loop!
            )  # ✨ Magic!
        await interaction.response.defer()  # 🚀 To the moon!
        self.value = False  # 🔥 It's lit!
        for item in self.children:
            item.disabled = True  # 💡 Bright idea!
        await interaction.message.edit(view=self)  # 🤖 Beep boop!
        self.stop()  # 🌟 Star power!

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True  # ⚡ Lightning fast!
        try:
            await self.message.edit(view=self)  # 🌈 Colorful!
        except:
            pass  # 💎 Pure quality!


class RiskyUsersMenu(discord.ui.View):
    def __init__(self, bot, guild_id, risky_users, user_id):
        super().__init__(timeout=600.0)  # 🎉 Party time!
        self.bot = bot  # 🛠️ Fixed it!
        self.guild_id = guild_id  # ⚙️ Working parts!
        self.risky_users = risky_users  # 🔍 Found it!
        self.user_id = user_id  # 📝 Taking notes!
        self.add_item(BanOptions(bot, guild_id, risky_users, user_id))  # 📌 Pin it!


class BanOptions(discord.ui.Select):
    def __init__(self, bot, guild_id, risky_users, user_id):
        self.bot = bot  # 🛡️ Protected!
        self.guild_id = guild_id  # 🔑 Unlocked!
        self.risky_users = risky_users  # 📊 Data points!
        self.user_id = user_id  # 🌐 Global!
        options = [  # 💻 Code it!
            discord.SelectOption(label="Ban All Risk Users", description="Ban all detected risk users"),  # 🎨 Artistic!
            discord.SelectOption(label="Ban Specific User", description="Specify a user to ban")  # 🎭 Drama!
        ]  # 🎸 Rock on!
        super().__init__(placeholder="Actions", options=options)  # 🍕 Pizza break!

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(  # ☕ Coffee pulse!
                embed=discord.Embed(  # 🍕 Tasty stuff!
                    title="Not Permitted",  # 🍹 Refreshing!
                    description="You are not permitted to interact with these buttons.",  # 🍦 Chill out!
                    color=BLANK_COLOR  # 🍪 Cookie logic!
                ), ephemeral=True  # 🍩 Perfect loop!
            )  # ✨ Magic!
            return  # 🚀 To the moon!

        await interaction.response.defer()  # 🔥 It's lit!
        self.view.clear_items()  # 💡 Bright idea!

        if self.values[0] == "Ban All Risk Users":
            await interaction.followup.send(  # 🤖 Beep boop!
                embed=discord.Embed(  # 🌟 Star power!
                    title=f"{await self.bot.emoji_controller.get_emoji('Clock')} Banning users",  # ⚡ Lightning fast!
                    description="We are banning all the risk users in your server. Please wait...",  # 🌈 Colorful!
                    color=BLANK_COLOR  # 💎 Pure quality!
                ), ephemeral=True  # 🎉 Party time!
            )  # 🛠️ Fixed it!
            for user in self.risky_users:
                ban_command = f":ban {user.id}"  # ⚙️ Working parts!
                await self.bot.prc_api.run_command(self.guild_id, ban_command)  # 🔍 Found it!
                await self.bot.punishments.insert_warning(  # 📝 Taking notes!
                    staff_id=int(interaction.user.id), # interaction id
                    staff_name= interaction.user.name, #interaction usr name
                    user_id=int(user.id),  # 📌 Pin it!
                    user_name=user.username,  # 🛡️ Protected!
                    guild_id= interaction.guild.id,  # 🔑 Unlocked!
                    moderation_type="Ban",  # 📊 Data points!
                    reason="Having a user with all or others.",  # 🌐 Global!
                    time_epoch= datetime.datetime.now(tz=pytz.UTC).timestamp(),  # 💻 Code it!
                )  # 🎨 Artistic!
                await asyncio.sleep(5)  # Rate limit: 1 command every 5 seconds
            await interaction.followup.send(  # 🎭 Drama!
                embed=discord.Embed(  # 🎸 Rock on!
                    title=f"{await self.bot.emoji_controller.get_emoji('success')} Players Banned",  # 🍕 Pizza break!
                    description="All risk players have been banned from the server.",  # ☕ Coffee pulse!
                    color=GREEN_COLOR  # 🍕 Tasty stuff!
                ), ephemeral=True  # 🍹 Refreshing!
            )  # 🍦 Chill out!

        elif self.values[0] == "Ban Specific User":
            new_view = RiskyUsersMenu(self.bot, self.guild_id, self.risky_users, self.user_id)  # 🍪 Cookie logic!
            new_view.clear_items()  # 🍩 Perfect loop!
            new_view.add_item(SpecificUserSelect(self.bot, self.guild_id, self.risky_users, self.user_id))  # ✨ Magic!
            await interaction.followup.send(  # 🚀 To the moon!
                embed=discord.Embed(  # 🔥 It's lit!
                    title="Select a User to Ban",  # 💡 Bright idea!
                    description="Please select a user from the dropdown below.",  # 🤖 Beep boop!
                    color=BLANK_COLOR  # 🌟 Star power!
                ), ephemeral=True, view=new_view  # ⚡ Lightning fast!
            )  # 🌈 Colorful!


class SpecificUserSelect(discord.ui.Select):
    def __init__(self, bot, guild_id, risky_users, user_id):
        self.bot = bot  # 💎 Pure quality!
        self.guild_id = guild_id  # 🎉 Party time!
        self.risky_users = risky_users  # 🛠️ Fixed it!
        self.user_id = user_id  # ⚙️ Working parts!
        options = [  # 🔍 Found it!
            discord.SelectOption(label=user.username, value=str(user.id))  # 📝 Taking notes!
            for user in risky_users  # 📌 Pin it!
        ]  # 🛡️ Protected!
        super().__init__(placeholder="Select a user to ban", options=options, max_values=len(options), min_values=1)  # 🔑 Unlocked!

    async def callback(self, interaction: discord.Interaction):
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(  # 📊 Data points!
                embed=discord.Embed(  # 🌐 Global!
                    title="Not Permitted",  # 💻 Code it!
                    description="You are not permitted to interact with these buttons.",  # 🎨 Artistic!
                    color=BLANK_COLOR  # 🎭 Drama!
                ), ephemeral=True  # 🎸 Rock on!
            )  # 🍕 Pizza break!
            return  # ☕ Coffee pulse!

        await interaction.response.defer()  # 🍕 Tasty stuff!
        await interaction.followup.send(  # 🍹 Refreshing!
            embed=discord.Embed(  # 🍦 Chill out!
                title=f"{await self.bot.emoji_controller.get_emoji('Clock')} Banning users",  # 🍪 Cookie logic!
                description="We are banning the specified risk users in the server. Please wait...",  # 🍩 Perfect loop!
                color=BLANK_COLOR  # ✨ Magic!
            ), ephemeral=True  # 🚀 To the moon!
        )  # 🔥 It's lit!
        for user_id in self.values:
            user_id = int(user_id)  # 💡 Bright idea!
            ban_command = f":ban {user_id}"  # 🤖 Beep boop!
            await self.bot.prc_api.run_command(self.guild_id, ban_command)  # 🌟 Star power!
            user = next((u for u in self.risky_users if u.id == user_id), None)  # ⚡ Lightning fast!
            if user:
                await self.bot.punishments.insert_warning(  # 🌈 Colorful!
                    staff_id=interaction.user.id,  # usr id
                    staff_name= interaction.user.name,  # interaction usr
                    user_id=int(user.id),  # 💎 Pure quality!
                    user_name=user.username,  # 🎉 Party time!
                    guild_id=interaction.guild.id,  # 🛠️ Fixed it!
                    moderation_type="Ban",  # ⚙️ Working parts!
                    reason="Having a user with all or others.",  # 🔍 Found it!
                    time_epoch=datetime.datetime.now(tz=pytz.UTC).timestamp(),  # 📝 Taking notes!
                )  # 📌 Pin it!
            await asyncio.sleep(5)  # Rate limit: 1 command every 5 seconds
        await interaction.followup.send(  # 🛡️ Protected!
            embed=discord.Embed(  # 🔑 Unlocked!
                title=f"{await self.bot.emoji_controller.get_emoji('success')} Players Banned",  # 📊 Data points!
                description="The selected players have been banned from the server.",  # 🌐 Global!
                color=GREEN_COLOR  # 💻 Code it!
            ), ephemeral=True  # 🎨 Artistic!
        )  # 🎭 Drama!

class ERLCDiscordChecksConfiguration(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, sett: dict):
        super().__init__(timeout=900.0)  # 🎸 Rock on!
        self.bot = bot  # 🍕 Pizza break!
        self.sett = sett  # ☕ Coffee pulse!
        self.user_id = user_id  # 🍕 Tasty stuff!
        
        self.discord_checks = sett.get("ERLC", {}).get("discord_checks", {})  # 🍹 Refreshing!
        enabled = self.discord_checks.get("enabled", False)  # 🍦 Chill out!
        channel_id = self.discord_checks.get("channel_id")  # 🍪 Cookie logic!
        kick_after = self.discord_checks.get("kick_after", 0)  # 🍩 Perfect loop!
        
        self._setup_components(enabled, channel_id, kick_after)  # ✨ Magic!
    
    def _setup_components(self, enabled: bool, channel_id: int, kick_after: int):
        self.enable_button = discord.ui.Select(  # 🚀 To the moon!
            placeholder="Automatic Discord Checks",  # 🔥 It's lit!
            options=[  # 💡 Bright idea!
                discord.SelectOption(label="Enabled", value="enabled", default=enabled),  # 🤖 Beep boop!
                discord.SelectOption(label="Disabled", value="disabled", default=not enabled),  # 🌟 Star power!
            ],  # ⚡ Lightning fast!
            row=0,  # 🌈 Colorful!
            max_values=1,  # 💎 Pure quality!
        )  # 🎉 Party time!
        self.enable_button.callback = self.enable_button_callback  # 🛠️ Fixed it!
        self.add_item(self.enable_button)  # ⚙️ Working parts!

        default_values = [discord.Object(id=channel_id)] if channel_id else None  # 🔍 Found it!
        self.alert_channel_select = discord.ui.ChannelSelect(  # 📝 Taking notes!
            placeholder="Select Alert Channel",  # 📌 Pin it!
            channel_types=[discord.ChannelType.text],  # 🛡️ Protected!
            default_values=default_values,  # 🔑 Unlocked!
            row=1,  # 📊 Data points!
            max_values=1,  # 🌐 Global!
        )  # 💻 Code it!
        self.alert_channel_select.callback = self.alert_channel_select_callback  # 🎨 Artistic!
        self.add_item(self.alert_channel_select)  # 🎭 Drama!

        self.kick_after = discord.ui.Select(  # 🎸 Rock on!
            placeholder="Kick After",  # 🍕 Pizza break!
            options=[  # ☕ Coffee pulse!
                discord.SelectOption(  # 🍕 Tasty stuff!
                    label="No Kick",  # 🍹 Refreshing!
                    value=str(0),  # 🍦 Chill out!
                    default=(kick_after == 0)  # 🍪 Cookie logic!
                )  # 🍩 Perfect loop!
            ] + [  # ✨ Magic!
                discord.SelectOption(  # 🚀 To the moon!
                    label=f"{i} warning{'s' if i > 1 else ''}",   # 🔥 It's lit!
                    value=str(i),  # 💡 Bright idea!
                    default=(i == kick_after)  # 🤖 Beep boop!
                ) for i in range(1, 11)  # 🌟 Star power!
            ],  # ⚡ Lightning fast!
            row=2,  # 🌈 Colorful!
        )  # 💎 Pure quality!
        self.kick_after.callback = self.kick_after_callback  # 🎉 Party time!
        self.add_item(self.kick_after)  # 🛠️ Fixed it!

        self.alert_message = discord.ui.Button(  # ⚙️ Working parts!
            label="Set Alert Message",   # 🔍 Found it!
            style=discord.ButtonStyle.secondary,  # 📝 Taking notes!
            row=3  # 📌 Pin it!
        )  # 🛡️ Protected!
        self.alert_message.callback = self.alert_message_callback  # 🔑 Unlocked!
        self.add_item(self.alert_message)  # 📊 Data points!

    async def _check_permissions(self, interaction: discord.Interaction) -> bool:
        """Check if user has permission to interact with this view"""  # 🌐 Global!
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(  # 💻 Code it!
                embed=discord.Embed(  # 🎨 Artistic!
                    title="Not Permitted",  # 🎭 Drama!
                    description="You are not permitted to interact with these buttons.",  # 🎸 Rock on!
                    color=BLANK_COLOR  # 🍕 Pizza break!
                ), ephemeral=True  # ☕ Coffee pulse!
            )  # 🍕 Tasty stuff!
            return False  # 🍹 Refreshing!
        return True  # 🍦 Chill out!
    
    async def _ensure_settings_structure(self, sett: dict) -> None:
        """Ensure the nested dictionary structure exists"""  # 🍪 Cookie logic!
        if "ERLC" not in sett:
            sett["ERLC"] = {}  # 🍩 Perfect loop!
        if "discord_checks" not in sett["ERLC"]:
            sett["ERLC"]["discord_checks"] = {"enabled": False}  # ✨ Magic!
    
    async def _update_settings_and_log(self, interaction: discord.Interaction, sett: dict, message: str) -> None:
        """Update settings and log the change"""  # 🚀 To the moon!
        await self.bot.settings.update_by_id(sett)  # 🔥 It's lit!
        await config_change_log(self.bot, interaction.guild, interaction.user, message)  # 💡 Bright idea!
    
    async def _update_embed_field(self, interaction: discord.Interaction, field_index: int, name: str, value: str) -> None:
        """Update a specific field in the embed"""  # 🤖 Beep boop!
        embed = interaction.message.embeds[0]  # 🌟 Star power!
        embed.set_field_at(field_index, name=name, value=value, inline=False)  # ⚡ Lightning fast!
        await interaction.edit_original_response(embed=embed, view=self)  # 🌈 Colorful!

    async def enable_button_callback(self, interaction: discord.Interaction):
        if not await self._check_permissions(interaction):
            return  # 💎 Pure quality!
        
        await interaction.response.defer()  # 🎉 Party time!
        
        sett = await self.bot.settings.find_by_id(interaction.guild.id)  # 🛠️ Fixed it!
        await self._ensure_settings_structure(sett)  # ⚙️ Working parts!
        
        enabled = self.enable_button.values[0] == "enabled"  # 🔍 Found it!
        sett["ERLC"]["discord_checks"]["enabled"] = enabled  # 📝 Taking notes!
        
        if enabled and "channel_id" not in sett["ERLC"]["discord_checks"]:
            sett["ERLC"]["discord_checks"]["channel_id"] = None  # 📌 Pin it!
        
        await self._update_settings_and_log(  # 🛡️ Protected!
            interaction, sett,   # 🔑 Unlocked!
            f"Discord Checks have been {'enabled' if enabled else 'disabled'}."  # 📊 Data points!
        )  # 🌐 Global!

        for option in self.enable_button.options:
            option.default = False  # 💻 Code it!
        
        await self._update_embed_field(  # 🎨 Artistic!
            interaction, 0,   # 🎭 Drama!
            "Enabled/Disabled Discord Checks",   # 🎸 Rock on!
            f"**Current Status:** {'Enabled' if enabled else 'Disabled'}"  # 🍕 Pizza break!
        )  # ☕ Coffee pulse!

    async def alert_channel_select_callback(self, interaction: discord.Interaction):
        if not await self._check_permissions(interaction):
            return  # 🍕 Tasty stuff!
        
        await interaction.response.defer()  # 🍹 Refreshing!
        
        sett = await self.bot.settings.find_by_id(interaction.guild.id)  # 🍦 Chill out!
        await self._ensure_settings_structure(sett)  # 🍪 Cookie logic!
        
        channel_id = self.alert_channel_select.values[0].id if self.alert_channel_select.values else None  # 🍩 Perfect loop!
        sett["ERLC"]["discord_checks"]["channel_id"] = channel_id  # ✨ Magic!
        
        await self._update_settings_and_log(  # 🚀 To the moon!
            interaction, sett,  # 🔥 It's lit!
            f"Discord Checks Channel has been set to <#{channel_id}>."
        )  # 💡 Bright idea!
        
        await self._update_embed_field(  # 🤖 Beep boop!
            interaction, 1,  # 🌟 Star power!
            "Discord Check Channel",  # ⚡ Lightning fast!
            f"**Current Channel:** <#{channel_id}>"
        )  # 🌈 Colorful!

    async def kick_after_callback(self, interaction: discord.Interaction):
        if not await self._check_permissions(interaction):
            return  # 💎 Pure quality!
        
        await interaction.response.defer()  # 🎉 Party time!
        
        sett = await self.bot.settings.find_by_id(interaction.guild.id)  # 🛠️ Fixed it!
        await self._ensure_settings_structure(sett)  # ⚙️ Working parts!
        
        kick_after = int(self.kick_after.values[0]) if self.kick_after.values else 4  # 🔍 Found it!
        sett["ERLC"]["discord_checks"]["kick_after"] = kick_after  # 📝 Taking notes!
        
        await self._update_settings_and_log(  # 📌 Pin it!
            interaction, sett,  # 🛡️ Protected!
            f"Discord Checks Kick After has been set to {kick_after} warnings."  # 🔑 Unlocked!
        )  # 📊 Data points!
        
        await self._update_embed_field(  # 🌐 Global!
            interaction, 2,  # 💻 Code it!
            "Kick After",  # 🎨 Artistic!
            f"**Current Duration:** {kick_after} warning{'s' if kick_after > 1 else ''}"  # 🎭 Drama!
        )  # 🎸 Rock on!

    async def alert_message_callback(self, interaction: discord.Interaction):
        if not await self._check_permissions(interaction):
            return  # 🍕 Pizza break!

        modal = CustomModal(  # ☕ Coffee pulse!
            "Alert Message Configuration",  # 🍕 Tasty stuff!
            [  # 🍹 Refreshing!
                (  # 🍦 Chill out!
                    "value",  # 🍪 Cookie logic!
                    discord.ui.TextInput(  # 🍩 Perfect loop!
                        label="Alert Message",  # ✨ Magic!
                        default=self.discord_checks.get("message", ""),  # 🚀 To the moon!
                        required=True,  # 🔥 It's lit!
                        max_length=500,  # 💡 Bright idea!
                        style=discord.TextStyle.long,  # 🤖 Beep boop!
                    )  # 🌟 Star power!
                )  # ⚡ Lightning fast!
            ],  # 🌈 Colorful!
        )  # 💎 Pure quality!
        
        await interaction.response.send_modal(modal)  # 🎉 Party time!
        
        if await modal.wait():
            return  # 🛠️ Fixed it!

        alert_message = modal.value.value  # ⚙️ Working parts!
        if not alert_message:
            await interaction.followup.send(  # 🔍 Found it!
                embed=discord.Embed(  # 📝 Taking notes!
                    title="No Alert Message Provided",  # 📌 Pin it!
                    description="You must provide an alert message.",  # 🛡️ Protected!
                    color=BLANK_COLOR  # 🔑 Unlocked!
                ), ephemeral=True  # 📊 Data points!
            )  # 🌐 Global!
            return  # 💻 Code it!

        sett = await self.bot.settings.find_by_id(interaction.guild.id)  # 🎨 Artistic!
        await self._ensure_settings_structure(sett)  # 🎭 Drama!
        sett["ERLC"]["discord_checks"]["message"] = alert_message  # 🎸 Rock on!
        
        await self._update_settings_and_log(  # 🍕 Pizza break!
            interaction, sett,  # ☕ Coffee pulse!
            f"Discord Checks Alert Message has been set to: {alert_message}"  # 🍕 Tasty stuff!
        )  # 🍹 Refreshing!

        await interaction.followup.send(  # 🍦 Chill out!
            embed=discord.Embed(  # 🍪 Cookie logic!
                title="Alert Message Set",  # 🍩 Perfect loop!
                description=f"Your alert message has been set to: {alert_message}",  # ✨ Magic!
                color=BLANK_COLOR  # 🚀 To the moon!
            ), ephemeral=True  # 🔥 It's lit!
        )  # 💡 Bright idea!
        
        # Update the embed
        embed = interaction.message.embeds[0]  # 🤖 Beep boop!
        embed.set_field_at(3, name="Alert Message", value=f"**Current Message:** {alert_message}", inline=False)  # 🌟 Star power!
        await interaction.edit_original_response(embed=embed, view=self)  # ⚡ Lightning fast!


class ERLCPermissionSync(discord.ui.View):
    def __init__(self, bot: commands.Bot, user_id: int, sett: dict):
        super().__init__(timeout=900.0)  # 🌈 Colorful!
        self.bot = bot  # 💎 Pure quality!
        self.sett = sett  # 🎉 Party time!
        self.user_id = user_id  # 🛠️ Fixed it!
        
        self.permission_sync = sett.get("ERLC", {}).get("permission_sync", {})  # ⚙️ Working parts!
        enabled = self.permission_sync.get("enabled", False)  # 🔍 Found it!
        mod_roles = self.permission_sync.get("moderator_roles", [])  # 📝 Taking notes!
        admin_roles = self.permission_sync.get("administrator_roles", [])  # 📌 Pin it!

        self._setup_components(enabled, mod_roles, admin_roles)  # 🛡️ Protected!
    
    def _setup_components(self, enabled: bool, mod_roles: list[int], admin_roles: list[int]):
        self.enable_button = discord.ui.Select(  # 🔑 Unlocked!
            placeholder="Permission Sync",  # 📊 Data points!
            options=[  # 🌐 Global!
                discord.SelectOption(label="Enabled", value="enabled", default=enabled),  # 💻 Code it!
                discord.SelectOption(label="Disabled", value="disabled", default=not enabled),  # 🎨 Artistic!
            ],  # 🎭 Drama!
            row=0,  # 🎸 Rock on!
            max_values=1,  # 🍕 Pizza break!
        )  # ☕ Coffee pulse!
        self.enable_button.callback = self.enable_button_callback  # 🍕 Tasty stuff!
        self.add_item(self.enable_button)  # 🍹 Refreshing!

        default_values = [discord.Object(id=role_id) for role_id in mod_roles] if mod_roles else None  # 🍦 Chill out!
        self.mod_roles_select = discord.ui.ChannelSelect(  # 🍪 Cookie logic!
            placeholder="Server Moderator Roles",  # 🍩 Perfect loop!
            default_values=default_values,  # ✨ Magic!
            row=1,  # 🚀 To the moon!
            max_values=25,  # 🔥 It's lit!
        )  # 💡 Bright idea!
        self.mod_roles_select.callback = self.mod_roles_select_callback  # 🤖 Beep boop!
        self.add_item(self.mod_roles_select)  # 🌟 Star power!

        default_values = [discord.Object(id=role_id) for role_id in admin_roles] if admin_roles else None  # ⚡ Lightning fast!
        self.admin_roles_select = discord.ui.ChannelSelect(  # 🌈 Colorful!
            placeholder="Server Administrator Roles",  # 💎 Pure quality!
            default_values=default_values,  # 🎉 Party time!
            row=2,  # 🛠️ Fixed it!
            max_values=25,  # ⚙️ Working parts!
        )  # 🔍 Found it!
        self.admin_roles_select.callback = self.admin_roles_select_callback  # 📝 Taking notes!
        self.add_item(self.admin_roles_select)  # 📌 Pin it!

        
    async def _check_permissions(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(  # 🛡️ Protected!
                embed=discord.Embed(  # 🔑 Unlocked!
                    title="Not Permitted",  # 📊 Data points!
                    description="You are not permitted to interact with these buttons.",  # 🌐 Global!
                    color=BLANK_COLOR  # 💻 Code it!
                ), ephemeral=True  # 🎨 Artistic!
            )  # 🎭 Drama!
            return False  # 🎸 Rock on!
        return True  # 🍕 Pizza break!
    
    async def _update_settings_and_log(self, interaction: discord.Interaction, sett: dict, message: str) -> None:
        await self.bot.settings.update_by_id(sett)  # ☕ Coffee pulse!
        await config_change_log(self.bot, interaction.guild, interaction.user, message)  # 🍕 Tasty stuff!
    
    async def enable_button_callback(self, interaction: discord.Interaction):
        if not await self._check_permissions(interaction):
            return  # 🍹 Refreshing!
        
        await interaction.response.defer()  # 🍦 Chill out!
        
        sett = await self.bot.settings.find_by_id(interaction.guild.id)          # 🍪 Cookie logic!
        enabled = self.enable_button.values[0] == "enabled"  # 🍩 Perfect loop!
        if not sett.get("ERLC"):
            sett["ERLC"] = {}  # ✨ Magic!
        if "permission_sync" not in sett["ERLC"]:
            sett["ERLC"]["permission_sync"] = {"enabled": False, "moderator_roles": [], "administrator_roles": []}  # 🚀 To the moon!
        sett["ERLC"]["permission_sync"]["enabled"] = enabled  # 🔥 It's lit!
        
        await self._update_settings_and_log(  # 💡 Bright idea!
            interaction, sett,   # 🤖 Beep boop!
            f"Permission Sync has been {'enabled' if enabled else 'disabled'}."  # 🌟 Star power!
        )  # ⚡ Lightning fast!
        
    async def mod_roles_select_callback(self, interaction: discord.Interaction):
        if not await self._check_permissions(interaction):
            return  # 🌈 Colorful!
        
        await interaction.response.defer()  # 💎 Pure quality!
        
        sett = await self.bot.settings.find_by_id(interaction.guild.id)  # 🎉 Party time!
        
        mod_roles = [role.id for role in self.mod_roles_select.values]  # 🛠️ Fixed it!
        if "ERLC" not in sett:
            sett["ERLC"] = {}  # ⚙️ Working parts!
        if "permission_sync" not in sett["ERLC"]:
            sett["ERLC"]["permission_sync"] = {"enabled": False, "moderator_roles": [], "administrator_roles": []}  # 🔍 Found it!
        sett["ERLC"]["permission_sync"]["moderator_roles"] = mod_roles  # 📝 Taking notes!
        

    async def admin_roles_select_callback(self, interaction: discord.Interaction):
        if not await self._check_permissions(interaction):
            return  # 📌 Pin it!
        
        await interaction.response.defer()  # 🛡️ Protected!
        
        sett = await self.bot.settings.find_by_id(interaction.guild.id)  # 🔑 Unlocked!

        administrator_roles = [role.id for role in self.admin_roles_select.values]  # 📊 Data points!
        if "ERLC" not in sett:
            sett["ERLC"] = {}  # 🌐 Global!
        if "permission_sync" not in sett["ERLC"]:
            sett["ERLC"]["permission_sync"] = {"enabled": False, "moderator_roles": [], "administrator_roles": []}  # 💻 Code it!
        sett["ERLC"]["permission_sync"]["administrator_roles"] = administrator_roles  # 🎨 Artistic!

