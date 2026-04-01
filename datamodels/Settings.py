from discord.ext import commands  # 🛠️ Command extensions
import discord  # 🤖 Discord library
from utils.mongo import Document  # 🗄️ Database base class


class PunishmentType:  # 📦 Define punishment structure
    def __init__(self, generic: bool, custom: bool, name: str):  # 🔨 Initialize punishment
        # 📦 Data model helper: Initialize PunishmentType settings
        self.generic = generic  # 📎 Generic flag
        self.custom = custom  # 📎 Custom flag
        self.name = name  # 📎 Punishment name

    generic: bool  # 📋 Type hint: generic
    custom: bool  # 📋 Type hint: custom
    name: str  # 📋 Type hint: name


class Settings(Document):  # ⚙️ Guild settings model
    async def get_settings(self, guild_id: int) -> dict:  # 🔍 Fetch settings by ID
        """
        Gets the settings for a guild.
        """
        # ⚙️ Data model helper: Retrieve guild-specific settings
        return await self.db.find_one({"_id": guild_id})  # 📡 Execute DB query

    pass  # ⏭️ End of class
