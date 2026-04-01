from discord.ext import commands
import discord
from utils.mongo import Document


class BaseDataClass:
    def __init__(self, *args, **kwargs):
        # 📦 Data model helper: Initialize BaseDataClass with arguments
        for key, value in kwargs.items():
            setattr(self, key, value)


class ServerKey(BaseDataClass):
    guild_id: int
    key: str


class ServerKeys(Document):
    async def get_server_key(self, guild_id: int):
        # 🔑 Data model helper: Retrieve the unique server key for a guild
        doc = await self.find_by_id(guild_id)
        if not doc:
            return None
        return ServerKey(guild_id=doc["_id"], key=doc["key"])

    async def insert_server_key(self, guild_id: int, key: str):
        # 🔑 Data model helper: Store or update the server key for a guild
        await self.upsert({"_id": guild_id, "key": key})
