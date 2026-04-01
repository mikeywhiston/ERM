from discord.ext import commands
import discord
from utils.mongo import Document
from utils.basedataclass import BaseDataClass


class SavedLog(BaseDataClass):
    # 📄 Data class for saved log entries
    guild_id: int
    timestamp: int
    logs: list[dict]


class SavedLogs(Document):
    # 📁 Data model for saved guild logs
    pass
