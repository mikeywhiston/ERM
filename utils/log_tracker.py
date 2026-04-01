from collections import defaultdict
from discord.ext import commands


class LogTracker:
    # 📉 Tracker for log timestamps to avoid duplicates
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Initialize last_timestamps with a starting time
        self.last_timestamps = defaultdict(
            lambda: defaultdict(lambda: int(self.bot.start_time))
        )

    # 🕒 Get the last tracked timestamp for a guild log
    def get_last_timestamp(self, guild_id: int, log_type: str) -> int:
        # Get the last timestamp for the given guild and log type
        return self.last_timestamps[guild_id][log_type]

    # 🆙 Update the tracked timestamp for a guild log
    def update_timestamp(self, guild_id: int, log_type: str, timestamp: int):
        # Update the timestamp if the provided one is more recent
        self.last_timestamps[guild_id][log_type] = max(
            timestamp, self.last_timestamps[guild_id][log_type]
        )
