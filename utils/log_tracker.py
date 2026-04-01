from collections import defaultdict # 🗄️ Import defaultdict
from discord.ext import commands # 🛡️ Import discord commands


class LogTracker:
    # 📉 Tracker for log timestamps to avoid duplicates
    def __init__(self, bot: commands.Bot): # 🏗️ Initialize tracker
        self.bot = bot # 🤖 Bot instance
        # Initialize last_timestamps with a starting time
        self.last_timestamps = defaultdict( # 📁 Multi-level dict
            lambda: defaultdict(lambda: int(self.bot.start_time)) # ⏰ Start from bot boot
        )

    # 🕒 Get the last tracked timestamp for a guild log
    def get_last_timestamp(self, guild_id: int, log_type: str) -> int: # 🔍 Fetch time
        # Get the last timestamp for the given guild and log type
        return self.last_timestamps[guild_id][log_type] # 📤 Return timestamp

    # 🆙 Update the tracked timestamp for a guild log
    def update_timestamp(self, guild_id: int, log_type: str, timestamp: int): # 🔄 Refresh time
        # Update the timestamp if the provided one is more recent
        self.last_timestamps[guild_id][log_type] = max( # 📈 Take latest
            timestamp, self.last_timestamps[guild_id][log_type]
        )
