import logging # 📝 Import logging

import discord # 📦 Import discord
from discord.ext import commands, tasks # 🚀 Import commands, tasks
import datetime # 📅 Import datetime

from menus import CompleteReminder # 📋 Import CompleteReminder menu
from utils import prc_api # 🔌 Import prc_api
import pytz # 🌍 Import pytz
from utils.constants import BLANK_COLOR # 🎨 Import BLANK_COLOR
import aiohttp # 🌐 Import aiohttp
from decouple import config # ⚙️ Import config

from utils.utils import has_whitelabel # 🛡️ Import whitelabel check


async def iterate_reminder(bot, guildObj): # 🔁 Reminder iteration logic
    # ⏰ Iterating through guild reminders...
    if await has_whitelabel(bot, guildObj["_id"]): # 🚫 Skip if whitelabeled
        return

    for item in guildObj["reminders"].copy(): # 📑 Loop through reminders
        if item.get("paused") is True: # ⏸️ Skip if paused
            continue

        current_time = datetime.datetime.now(tz=pytz.UTC) # 🕒 Get UTC time
        interval = item["interval"] # ⏲️ Get reminder interval

        if current_time.timestamp() - item["lastTriggered"] >= interval: # ⌛ Check if due
            guild = bot.get_guild(int(guildObj["_id"])) # 🏰 Get guild object
            if not guild: # ❓ Skip if guild missing
                continue
            channel = guild.get_channel(int(item["channel"])) # 📺 Get target channel
            if not channel: # ❓ Skip if channel missing
                continue

            roles = [] # 👥 List for mentions
            try:
                for role in item["role"]: # 📑 Loop through roles to ping
                    role_obj = guild.get_role(int(role))
                    if role_obj is not None: # ✅ Add role mention
                        roles.append(role_obj.mention)
            except TypeError: # ⚠️ Handle invalid role data
                roles = [""]

            if (
                    item.get("completion_ability") # ✨ Check if completion view needed
                    and item.get("completion_ability") is True
            ):
                view = CompleteReminder(bot) # 🔘 Create button view
            else:
                view = None # 🚫 No buttons
            embed = discord.Embed( # 📧 Create reminder message
                title="Notification",
                description=f"{item['message']}",
                color=BLANK_COLOR,
            )

            lastTriggered = next_time.timestamp() # 🕒 Set new trigger time
            item["lastTriggered"] = lastTriggered # 💾 Update object
            await bot.reminders.update_by_id(guildObj) # 🆙 Save to DB

            if isinstance(item.get("integration"), dict): # 🧩 Check game integration
                # This has the ERLC integration enabled
                command = (
                    "h" # 💡 Hint command
                    if item["integration"]["type"] == "Hint"
                    else (
                        "m" # 💬 Message command
                        if item["integration"]["type"] == "Message"
                        else None
                    )
                )
                content = item["integration"]["content"] # 📝 Game message content
                total = ":" + command + " " + content # 🔡 Formulate game command
                if (
                        await bot.server_keys.db.count_documents( # 🔑 Check for API keys
                            {"_id": channel.guild.id}
                        )
                        != 0
                ):
                    do_not_complete = False # 🚦 Proceed by default
                    try:
                        status = await bot.prc_api.get_server_status( # 🏥 Check server status
                            channel.guild.id
                        )
                    except prc_api.ResponseFailure: # ⚠️ Fail if status check fails
                        do_not_complete = True

                    if not do_not_complete: # 🚀 Run game command
                        resp = await bot.prc_api.run_command(
                            channel.guild.id, total
                        )
                        if resp[0] != 200: # 🔴 Log failure
                            logging.info(
                                "Failed reaching PRC due to {} status code".format(
                                    resp
                                )
                            )
                        else:
                            logging.info(
                                "Integration success with 200 status code"
                            )
                    else:
                        logging.info(
                            f"Cancelled execution of reminder for {channel.guild.id}"
                        )

            if not view:
                await channel.send(
                    " ".join(roles),
                    embed=embed,
                    allowed_mentions=discord.AllowedMentions(
                        replied_user=True,
                        everyone=True,
                        roles=True,
                        users=True,
                    ),
                )
            else:
                await channel.send(
                    " ".join(roles),
                    embed=embed,
                    view=view,
                    allowed_mentions=discord.AllowedMentions(
                        replied_user=True,
                        everyone=True,
                        roles=True,
                        users=True,
                    ),
                )

            try:
                panel_url_var = config("PANEL_API_URL")
                if panel_url_var not in ["", None]:
                    async with aiohttp.ClientSession() as session:
                        async with session.post(
                                f"{panel_url_var}/Internal/{channel.guild.id}/TriggerReminder",
                                headers={
                                    "Authorization": config(
                                        "INTERNAL_API_AUTH"
                                    ),
                                    "Content-Type": "application/json",
                                },
                                json={"message": item["message"]},
                        ):
                            pass
            except Exception as e:
                logging.warning(f"Failed to trigger reminder: {e}")



@tasks.loop(minutes=1)
async def check_reminders(bot):
    # 🔔 Checking for due reminders...
    if bot.environment == "PRODUCTION":
        try:
            async for guildObj in bot.reminders.db.find({}):
                try:
                    await iterate_reminder(bot, guildObj)
                except Exception as e:
                    logging.warning(f"Reminder failed: {e}")
        except Exception as e:
            logging.warning(f"Reminder task failed: {e}")
    else:
        try:
            async for guildObj in bot.reminders.db.find({"_id": int(config("CUSTOM_GUILD_ID"))}):
                try:
                    await iterate_reminder(bot, guildObj)
                except Exception as e:
                    logging.warning(f"Reminder failed: {e}")
        except Exception as e:
            logging.warning(f"Reminder task failed: {e}")
