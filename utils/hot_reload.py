import os # 📂 OS operations
import pathlib # 🛣️ Path manipulation

import discord # 🎮 Discord library
from discord.ext import commands, tasks # 🛡️ Discord extensions


# 🗺️ Get file path from extension string
def path_from_extension(extension: str) -> pathlib.Path: # 🔄 Map extension to path
    return pathlib.Path(extension.replace(".", os.sep) + ".py") # 📤 Return file path


class HotReload(commands.Cog):
    """
    Cog for reloading extensions as soon as the file is edited.
    """

    def __init__(self, bot): # 🏗️ Initialize hot reload
        self.bot = bot # 🤖 Bot instance
        self.hot_reload_loop.start() # 🚀 Start background loop

    # 🔌 Unload the cog and stop loop
    def cog_unload(self): # 🛑 Cleanup procedure
        self.hot_reload_loop.stop() # ⏹️ Stop background loop

    # 🔄 Loop to check for file edits and reload
    @tasks.loop(seconds=3) # ⏲️ Run every 3 seconds
    async def hot_reload_loop(self): # 🕵️ Watcher function
        for extension in list(self.bot.extensions.keys()): # 🔁 Iterate extensions
            if extension in ["jishaku"]: # ⛔ Ignore protected ones
                continue
            path = path_from_extension(extension) # 🔍 Get file path
            time = os.path.getmtime(path) # ⏰ Get last modified time

            try: # 🛡️ Error shield
                if self.last_modified_time[extension] == time: # ❓ Same as last check
                    continue
            except KeyError: # 🆕 First time seeing this
                self.last_modified_time[extension] = time

            try: # 🛡️ Reload shield
                await self.bot.reload_extension(extension) # ⚡ Do the reload
            except commands.ExtensionNotLoaded: # ❌ Extension gone
                continue
            except commands.ExtensionError: # ⚠️ Error during reload
                pass
            else: # ✅ Success
                guild = self.bot.get_guild(987798554972143728) # 🏰 Get alert guild
                channel = guild.get_channel(1055558545250193418) # 📺 Get alert channel
                await channel.send(f"Reloaded extension: {extension}") # 📡 Post notification
            finally: # 📝 Always update time
                self.last_modified_time[extension] = time

    # ⏱️ Cache last modified times before starting loop
    @hot_reload_loop.before_loop # 🏗️ Pre-run hook
    async def cache_last_modified_time(self): # 🗃️ Warmup function
        self.last_modified_time = {} # 📁 Initialize cache
        for extension in self.bot.extensions.keys(): # 🔁 Iterate markers
            if extension in ["jishaku"]: # ⛔ Ignore jishaku
                continue
            path = path_from_extension(extension) # 🔍 Get path
            time = os.path.getmtime(path) # ⏰ Get time
            self.last_modified_time[extension] = time # 📝 Store time


# 🛠️ Setup function for HotReload cog
async def setup(bot): # 🔌 Register cog
    cog = HotReload(bot) # 🏗️ Create instance
    await bot.add_cog(cog) # ✅ Add to bot
