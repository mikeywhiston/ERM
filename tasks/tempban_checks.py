import discord # 📦 Import discord
import logging # 📝 Import logging

from decouple import config # ⚙️ Import config
from discord.ext import commands, tasks # 🚀 Import commands, tasks
import time # ⏱️ Import time
import datetime # 📅 Import datetime
import pytz # 🌍 Import pytz


@tasks.loop(minutes=10, reconnect=True) # ⏰ Run every 10 mins
async def tempban_checks(bot): # 🚫 Checking temporary bans...
    # This will check for expired time bans
    # and for servers which have this feature enabled
    # to automatically remove the ban in-game
    # using POST /server/command

    # This will also use a GET request before
    # sending that POST request, particularly
    # GET /server/bans

    # We also check if the punishment item is
    # before the update date, because else we'd
    # have too high influx of invalid
    # temporary bans

    # For diagnostic purposes, we also choose to
    # capture the amount of time it takes for this
    # event to run, as it may cause issues in
    # time registration.

    cached_servers = {} # 🗄️ Cache for bans
    initial_time = time.time() # ⏱️ Start benchmark
    async for punishment_item in bot.punishments.db.find( # 🔍 Find expired temp bans
        {
            "Epoch": {"$gt": 1709164800},
            "CheckExecuted": {"$exists": False},
            "UntilEpoch": {"$lt": int(datetime.datetime.now(tz=pytz.UTC).timestamp())},
            "Type": "Temporary Ban",
        }
    ):
        try:
            guild = bot.get_guild(punishment_item["Guild"]) # 🏰 Get guild
            if guild is None: # 🏢 Fetch if missing
                guild = await bot.fetch_guild(punishment_item["Guild"])
        except discord.HTTPException: # 🛡️ Handle fetch errors
            continue

        if not cached_servers.get(punishment_item["Guild"]): # 🌩️ Check server cache
            try:
                cached_servers[punishment_item["Guild"]] = await bot.prc_api.fetch_bans( # 📑 Get bans
                    punishment_item["Guild"]
                )
            except: # 🔴 Skip if API fail
                continue

        punishment_item["CheckExecuted"] = True # ✅ Mark as processed
        await bot.punishments.update_by_id(punishment_item) # 💾 Save update

        if punishment_item["UserID"] not in [ # 🔍 Confirm user is banned
            i.user_id for i in cached_servers[punishment_item["Guild"]]
        ]:
            continue

        sorted_punishments = sorted( # 📑 Get history
            [
                i
                async for i in bot.punishments.db.find(
                    {
                        "UserID": punishment_item["UserID"],
                        "Guild": punishment_item["Guild"],
                    }
                )
            ],
            key=lambda x: x["Epoch"], # ⏱️ Sort by time
            reverse=True,
        )
        new_sorted_punishments = [] # 📥 Filter history
        for item in sorted_punishments:
            if item == punishment_item: # 🏁 Stop at current
                break
            new_sorted_punishments.append(item)

        if any([i["Type"] in ["Ban", "Temporary Ban"] for i in new_sorted_punishments]): # 🚫 Skip if newer bans exist
            continue

        await bot.prc_api.unban_user( # 🔓 Unban in-game
            punishment_item["Guild"], punishment_item["user_id"]
        )
    del cached_servers # 🧹 Clear local cache
    end_time = time.time() # ⏱️ End benchmark
    logging.warning( # 📝 Log task duration
        "Event tempban_checks took {} seconds".format(str(end_time - initial_time))
    )
