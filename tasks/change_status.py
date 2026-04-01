from discord.ext import tasks # 📦 Importing tasks
import discord # 📦 Importing discord
import logging # 📦 Importing logging


@tasks.loop(hours=1) # ⏰ Run every hour
async def change_status(bot):
    # 🔌 Updating bot status...
    await bot.wait_until_ready() # ⏳ Wait for bot to be ready
    logging.info("Changing status") # 📝 Log status change
    status = "⚡ /about | ermbot.xyz" # 🏷️ Define status string
    await bot.change_presence(activity=discord.CustomActivity(name=status)) # 🛠️ Update bot presence
