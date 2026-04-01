import discord # 📦 Import discord
from discord.ext import tasks, commands # 🚀 Import tasks, commands
import logging # 📝 Import logging
from utils import prc_api # 🔌 Import prc_api


@tasks.loop(seconds=10) # ⏰ Run every 10 secs
async def process_scheduled_pms(bot): # 📬 Processing scheduled PMs...
    try:
        logging.info("Processing scheduled PMs.") # 📝 Log task start
        while not bot.scheduled_pm_queue.empty(): # 🔁 Loop while items in queue
            pm_data = await bot.scheduled_pm_queue.get() # 📥 Pop item from queue
            guild_id, usernames, message = pm_data # 🏷️ Unpack PM data
            logging.info("Not empty, grabbed last queue of scheduled PMs.") # 📝 Log grab
            try:
                await bot.prc_api.run_command(guild_id, f":pm {usernames} {message}") # 🎮 Run in-game PM cmd
            except prc_api.ResponseFailure as e: # ⚠️ Handle API failure
                if e.status_code == 429: # 🛑 Rate limited
                    logging.info(
                        "429 for last item in scheduled PM, putting back into queue."
                    )
                    await bot.scheduled_pm_queue.put(pm_data) # 🔄 Return to queue
    except Exception as e: # 🔴 Log unexpected errors
        logging.error(f"Error in process_scheduled_pms: {e}")
