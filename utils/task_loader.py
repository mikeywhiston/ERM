from tasks.iterate_ics import iterate_ics
from tasks.check_loa import check_loa
from tasks.check_reminders import check_reminders
from tasks.check_infractions import check_infractions
from tasks.iterate_prc_logs import iterate_prc_logs
from tasks.tempban_checks import tempban_checks
from tasks.process_scheduled_pms import process_scheduled_pms
from tasks.statistics_check import statistics_check
from tasks.change_status import change_status
from tasks.check_whitelisted_car import check_whitelisted_car
from tasks.sync_weather import sync_weather
from tasks.iterate_conditions import iterate_conditions
from tasks.prc_automations import prc_automations
from tasks.mc_discord_checks import mc_discord_checks
import asyncio
import logging

async def start_tasks(bot):
        logging.info("Starting tasks...")
        if bot.reminders_enabled:
            check_reminders.start(bot)
            logging.info("Starting the Check Reminders task...")
        else:
            logging.warning("Reminders disabled. Not running check reminders task")
        await asyncio.sleep(30)
        check_loa.start(bot)
        logging.info("Starting the Check LOA task...")
        await asyncio.sleep(30)
        iterate_ics.start(bot)
        logging.info("Starting the Iterate ICS task...")
        await asyncio.sleep(30)
        iterate_prc_logs.start(bot)
        logging.info("Starting the Iterate PRC Logs task...")
        await asyncio.sleep(30)
        statistics_check.start(bot)
        logging.info("Starting the Statistics Check task...")
        await asyncio.sleep(30)
        tempban_checks.start(bot)
        logging.info("Starting the Tempban Checks task...")
        await asyncio.sleep(30)
        check_whitelisted_car.start(bot)
        logging.info("Starting the Check Whitelisted Car task...")
        if bot.environment != "CUSTOM":
            await asyncio.sleep(30)
            change_status.start(bot)
        logging.info("Starting the Change Status task...")
        await asyncio.sleep(30)
        process_scheduled_pms.start(bot)
        logging.info("Starting the Process Scheduled PMs task...")
        await asyncio.sleep(30)
        sync_weather.start(bot)
        logging.info("Starting the Sync Weather task...")
        await asyncio.sleep(30)
        if bot.actions_enabled:
            iterate_conditions.start(bot)
            logging.info("Starting the Iterate Conditions task...")
        else:
            logging.warning("Actions task is disabled.")
        await asyncio.sleep(30)
        check_infractions.start(bot)
        logging.info("Starting the Check Infractions task...")
        await asyncio.sleep(30)
        prc_automations.start(bot)
        logging.info("Starting the ER:LC Discord Checks task...")
        await asyncio.sleep(30)
        mc_discord_checks.start(bot)
        logging.info("Starting the MC Discord Checks task...")
        logging.info("All tasks are now running!")