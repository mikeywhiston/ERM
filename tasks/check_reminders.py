import logging

import discord
from discord.ext import commands, tasks
import datetime

from menus import CompleteReminder
from utils import prc_api
import pytz
from utils.constants import BLANK_COLOR
import aiohttp
from decouple import config

from utils.utils import has_whitelabel

ALLOWED_MENTIONS = discord.AllowedMentions(
    replied_user=True,
    everyone=True,
    roles=True,
    users=True,
)


async def run_erlc_integration(bot, guild_id, integration):
    """Execute an ER:LC integration command for a reminder."""
    command_map = {"Hint": "h", "Message": "m"}
    command = command_map.get(integration["type"])
    if not command:
        return

    content = integration["content"]
    full_command = f":{command} {content}"

    has_key = await bot.server_keys.db.count_documents({"_id": guild_id}) != 0
    if not has_key:
        return

    try:
        await bot.prc_api.get_server_status(guild_id)
    except prc_api.ResponseFailure:
        logging.info(f"Cancelled execution of reminder for {guild_id}")
        return

    resp = await bot.prc_api.run_command(guild_id, full_command)
    if resp[0] != 200:
        logging.warning(f"Failed reaching PRC due to {resp[0]} status code")
    else:
        logging.info("Integration success with 200 status code")


async def notify_panel(guild_id, message):
    """Notify the panel API that a reminder was triggered."""
    try:
        panel_url = config("PANEL_API_URL", default="")
        if not panel_url:
            return
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{panel_url}/Internal/{guild_id}/TriggerReminder",
                headers={
                    "Authorization": config("INTERNAL_API_AUTH", default=""),
                    "Content-Type": "application/json",
                },
                json={"message": message},
                timeout=aiohttp.ClientTimeout(total=10),
            ):
                pass
    except Exception as e:
        logging.warning(f"Failed to trigger panel reminder: {e}")


async def process_reminder(bot, guild, item, guild_obj):
    """Process a single reminder item."""
    channel = guild.get_channel(int(item["channel"]))
    if not channel:
        try:
            channel = await guild.fetch_channel(int(item["channel"]))
        except discord.HTTPException:
            return

    # Build role mentions
    roles = []
    for role_id in item.get("role") or []:
        role_obj = guild.get_role(int(role_id))
        if role_obj:
            roles.append(role_obj.mention)

    # Build view
    view = CompleteReminder(bot) if item.get("completion_ability") is True else None

    # Build embed
    embed = discord.Embed(
        title="Notification",
        description=item["message"],
        color=BLANK_COLOR,
    )

    # Update last triggered time
    item["lastTriggered"] = datetime.datetime.now(tz=pytz.UTC).timestamp()
    await bot.reminders.update_by_id(guild_obj)

    # Run ER:LC integration if configured
    if isinstance(item.get("integration"), dict):
        await run_erlc_integration(bot, guild.id, item["integration"])

    # Send the reminder
    await channel.send(
        " ".join(roles),
        embed=embed,
        view=view,
        allowed_mentions=ALLOWED_MENTIONS,
    )

    # Notify panel
    await notify_panel(guild.id, item["message"])


async def iterate_reminder(bot, guild_obj):
    """Iterate through all reminders for a guild and process any that are due."""
    if await has_whitelabel(bot, guild_obj["_id"]):
        return

    guild = bot.get_guild(int(guild_obj["_id"]))
    if not guild:
        return

    current_timestamp = datetime.datetime.now(tz=pytz.UTC).timestamp()

    for item in guild_obj["reminders"].copy():
        if item.get("paused") is True:
            continue

        if current_timestamp - item["lastTriggered"] < item["interval"]:
            continue

        try:
            await process_reminder(bot, guild, item, guild_obj)
        except Exception as e:
            logging.warning(f"Reminder '{item.get('name', 'unknown')}' failed in guild {guild_obj['_id']}: {e}")


@tasks.loop(minutes=1)
async def check_reminders(bot):
    query = {}
    if bot.environment != "PRODUCTION":
        try:
            query = {"_id": int(config("CUSTOM_GUILD_ID"))}
        except Exception as e:
            logging.warning(f"Reminder task failed: {e}")
            return

    try:
        for guild_obj in await bot.reminders.db.find(query).to_list(None):
            try:
                await iterate_reminder(bot, guild_obj)
            except Exception as e:
                logging.warning(f"Reminder task failed for guild {guild_obj.get('_id')}: {e}")
    except Exception as e:
        logging.warning(f"Reminder task failed: {e}")
