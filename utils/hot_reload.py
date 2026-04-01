import os
import pathlib

import discord
from discord.ext import commands, tasks


# 🗺️ Get file path from extension string
def path_from_extension(extension: str) -> pathlib.Path:
    return pathlib.Path(extension.replace(".", os.sep) + ".py")


class HotReload(commands.Cog):
    """
    Cog for reloading extensions as soon as the file is edited.
    """

    def __init__(self, bot):
        self.bot = bot
        self.hot_reload_loop.start()

    # 🔌 Unload the cog and stop loop
    def cog_unload(self):
        self.hot_reload_loop.stop()

    # 🔄 Loop to check for file edits and reload
    @tasks.loop(seconds=3)
    async def hot_reload_loop(self):
        for extension in list(self.bot.extensions.keys()):
            if extension in ["jishaku"]:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)

            try:
                if self.last_modified_time[extension] == time:
                    continue
            except KeyError:
                self.last_modified_time[extension] = time

            try:
                await self.bot.reload_extension(extension)
            except commands.ExtensionNotLoaded:
                continue
            except commands.ExtensionError:
                pass
            else:
                guild = self.bot.get_guild(987798554972143728)
                channel = guild.get_channel(1055558545250193418)
                await channel.send(f"Reloaded extension: {extension}")
            finally:
                self.last_modified_time[extension] = time

    # ⏱️ Cache last modified times before starting loop
    @hot_reload_loop.before_loop
    async def cache_last_modified_time(self):
        self.last_modified_time = {}
        for extension in self.bot.extensions.keys():
            if extension in ["jishaku"]:
                continue
            path = path_from_extension(extension)
            time = os.path.getmtime(path)
            self.last_modified_time[extension] = time


# 🛠️ Setup function for HotReload cog
async def setup(bot):
    cog = HotReload(bot)
    await bot.add_cog(cog)
