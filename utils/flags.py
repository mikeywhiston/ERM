import discord # 🎮 Import discord
from discord.ext import commands # 🛡️ Import discord commands


class DutyManageOptions(commands.FlagConverter, delimiter="=", prefix="/"):
    # ⚙️ Options for managing duty session state
    onduty: bool = False # 🔘 Set on-duty status
    togglebreak: bool = False # ⏸️ Toggle break session
    offduty: bool = False # ⏹️ Set off-duty status
    without_command_execution: bool = False # 🔇 Skip command logic


class PunishOptions(commands.FlagConverter, delimiter="=", prefix="/"):
    # ⚙️ Options for issuing punishments
    without_command_execution: bool = False # 🔇 Skip command logic
    ephemeral: bool = False # 👻 Hidden response
    noconfirm: bool = False # ✅ Skip confirmation


class SearchOptions(commands.FlagConverter, delimiter="=", prefix="/"):
    # ⚙️ Options for search-related commands
    without_command_execution: bool = False # 🔇 Skip command logic
    ephemeral: bool = False # 👻 Hidden response
