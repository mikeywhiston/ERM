import discord
from discord.ext import commands


class DutyManageOptions(commands.FlagConverter, delimiter="=", prefix="/"):
    # ⚙️ Options for managing duty session state
    onduty: bool = False
    togglebreak: bool = False
    offduty: bool = False
    without_command_execution: bool = False


class PunishOptions(commands.FlagConverter, delimiter="=", prefix="/"):
    # ⚙️ Options for issuing punishments
    without_command_execution: bool = False
    ephemeral: bool = False
    noconfirm: bool = False


class SearchOptions(commands.FlagConverter, delimiter="=", prefix="/"):
    # ⚙️ Options for search-related commands
    without_command_execution: bool = False
    ephemeral: bool = False
