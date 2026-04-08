import datetime
import json
import logging
import time
from dataclasses import MISSING
from pkgutil import iter_modules
import re
from collections import defaultdict
import asyncio

from datamodels.MapleKeys import MapleKeys
from datamodels.Whitelabel import Whitelabel

from utils.accounts import Accounts
from utils.emojis import EmojiController

from utils.log_tracker import LogTracker
from utils.mc_api import MCApiClient
from utils.mongo import Document

import aiohttp
import decouple
import discord.mentions

from pymongo import AsyncMongoClient


import asyncio
import pytz
import sentry_sdk
from decouple import config
from discord import app_commands
from discord.ext import tasks
from roblox import client as roblox
from sentry_sdk import push_scope, capture_exception
from sentry_sdk.integrations.pymongo import PyMongoIntegration
from utils.task_loader import start_tasks



from datamodels.CustomFlags import CustomFlags
from datamodels.ServerKeys import ServerKeys
from datamodels.ShiftManagement import ShiftManagement
from datamodels.ActivityNotice import ActivityNotices
from datamodels.Analytics import Analytics
from datamodels.Consent import Consent
from datamodels.CustomCommands import CustomCommands
from datamodels.Errors import Errors
from datamodels.FiveMLinks import FiveMLinks
from datamodels.LinkStrings import LinkStrings
from datamodels.PunishmentTypes import PunishmentTypes
from datamodels.Reminders import Reminders
from datamodels.Settings import Settings
from datamodels.APITokens import APITokens
from datamodels.StaffConnections import StaffConnections
from datamodels.Views import Views
from datamodels.Actions import Actions
from datamodels.Warnings import Warnings
from datamodels.ProhibitedUseKeys import ProhibitedUseKeys
from datamodels.PendingOAuth2 import PendingOAuth2
from datamodels.OAuth2Users import OAuth2Users
from datamodels.IntegrationCommandStorage import IntegrationCommandStorage
from datamodels.SavedLogs import SavedLogs

from menus import CompleteReminder, LOAMenu, RDMActions
from utils.viewstatemanger import ViewStateManager
from utils.bloxlink import Bloxlink
from utils.prc_api import PRCApiClient
from utils.prc_api import ResponseFailure
from utils.utils import *
from utils.constants import *
import utils.prc_api


_global_fetch_semaphore = asyncio.Semaphore(45)
_fetch_delays = defaultdict(float)

async def rate_limited_fetch(coro, endpoint_type="default"):
    """Rate-limited wrapper for Discord API calls"""
    async with _global_fetch_semaphore:
        if _fetch_delays[endpoint_type] > 0:
            await asyncio.sleep(_fetch_delays[endpoint_type])
        
        try:
            result = await coro
            _fetch_delays[endpoint_type] = max(0, _fetch_delays[endpoint_type] - 0.1)
            return result
        except discord.HTTPException as e:
            if e.status == 429:
                _fetch_delays[endpoint_type] = min(_fetch_delays[endpoint_type] + 0.5, 5.0)
                if e.retry_after:
                    await asyncio.sleep(e.retry_after)
            raise

setup = False
accepted_envs = ["PRODUCTION", "DEVELOPMENT", "ALPHA", "CUSTOM"]


sentry_url = config("SENTRY_URL", "")
bloxlink_api_key = config("BLOXLINK_API_KEY", "")
dbname = config("DB_NAME", "erm").replace("$", "").replace(".", "") # Note that $ and . are forbidden chars

discord.utils.setup_logging(level=logging.INFO)
discord.VoiceClient.warn_nacl = False
discord.VoiceClient.warn_dave = False

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

credentials_dict = {}
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


class Bot(commands.AutoShardedBot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setup_status: bool = False
        self._member_cache = {}
        self._guild_cache = {}
        self._cache_timeout = 300

    async def close(self):
        for session in self.external_http_sessions:
            if session is not None and session.closed is False:
                await session.close()
        await super().close()

    async def is_owner(self, user: discord.User):
        # Only developers of the bot on the team should have
        # full access to Jishaku commands. Hard-coded
        # IDs are a security vulnerability.

        # Else fall back to the original
        if user.id == 1394817794427846737:
            return True

        if environment != "CUSTOM": # let's not allow custom bot owners to use jishaku lol
            return await super().is_owner(user)
        else:
            return False

    async def setup_hook(self) -> None:
        self.external_http_sessions: list[aiohttp.ClientSession] = []
        self.view_state_manager: ViewStateManager = ViewStateManager()

        if not self.setup_status:
            # await bot.load_extension('utils.routes')
            logging.info(
                "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━���━━━━━━\n\n{} is online!".format(
                    self.user.name
                )
            )
            self.mongo = AsyncMongoClient(str(mongo_url))

            # The checking for this is defined just before the run method - approx line 649
            self.db = self.mongo[dbname]

            self.panel_db = self.mongo[f"{f"{dbname}_" if dbname != "erm" else ""}UserIdentity"]
            self.priority_settings = Document(self.panel_db, "PrioritySettings")
            self.staff_requests = Document(self.panel_db, "StaffRequests")

            self.start_time = time.time()

            self.log_tracker = LogTracker(self)
            self.scheduled_pm_queue = asyncio.Queue()
            self.pm_counter = {}
            self.team_restrictions_infractions = (
                {}
            )  # Guild ID => [ { Username: Count } ]

            self.shift_management = ShiftManagement(self.db, "shift_management")
            self.errors = Errors(self.db, "errors")
            self.loas = ActivityNotices(self.db, "leave_of_absences")
            self.reminders = Reminders(self.db, "reminders")
            self.custom_commands = CustomCommands(self.db, "custom_commands")
            self.analytics = Analytics(self.db, "analytics")
            self.punishment_types = PunishmentTypes(self.db, "punishment_types")
            self.custom_flags = CustomFlags(self.db, "custom_flags")
            self.views = Views(self.db, "views")
            self.api_tokens = APITokens(self.db, "api_tokens")
            self.link_strings = LinkStrings(self.db, "link_strings")
            self.fivem_links = FiveMLinks(self.db, "fivem_links")
            self.consent = Consent(self.db, "consent")
            self.punishments = Warnings(self)
            self.settings = Settings(self.db, "settings")
            self.server_keys = ServerKeys(self.db, "server_keys")
            self.maple_county = self.mongo[f"{f"{dbname}_" if dbname != "erm" else ""}MapleCounty"]
            self.mc_keys = MapleKeys(self.maple_county, "Auth")

            self.staff_connections = StaffConnections(self.db, "staff_connections")
            self.ics = IntegrationCommandStorage(self.db, "logged_command_data")
            self.actions = Actions(self.db, "actions")
            self.prohibited = ProhibitedUseKeys(self.db, "prohibited_keys")
            self.saved_logs = SavedLogs(self.db, "saved_logs")
            self.whitelabel = Whitelabel(self.mongo[f"{dbname.upper()}Processing"], "Instances")

            self.pending_oauth2 = PendingOAuth2(self.db, "pending_oauth2")
            self.oauth2_users = OAuth2Users(self.db, "oauth2")

            self.accounts = Accounts(self)

            if environment == "CUSTOM":
                doc = await self.whitelabel.db.find_one({"GuildID": config("CUSTOM_GUILD_ID", default="0")})
                if not doc:
                    raise Exception(
                        "Custom guild ID not found in the database. This means the whitelabel subscription is overdue."
                    )

            self.roblox = roblox.Client()
            self.prc_api = PRCApiClient(
                self,
                base_url=config(
                    "PRC_API_URL", default="https://api.policeroleplay.community/v1"
                ),
                api_key=config("PRC_API_KEY", default=None),
            )
            self.mc_api = MCApiClient(
                self, base_url=config("MC_API_URL"), api_key=config("MC_API_KEY")
            )
            self.bloxlink = Bloxlink(self, config("BLOXLINK_API_KEY"))

            Extensions = [m.name for m in iter_modules(["cogs"], prefix="cogs.")]
            Events = [m.name for m in iter_modules(["events"], prefix="events.")]
            BETA_EXT = ["cogs.StaffConduct"]
            EXTERNAL_EXT = ["utils.api"]
            [Extensions.append(i) for i in EXTERNAL_EXT]
            self.reminders_enabled, self.actions_enabled = True, True
            if config("ACTIONS_ENABLED", default="TRUE").upper() != "TRUE":
                self.actions_enabled = False
                Extensions.remove("cogs.Actions")
                logging.info("Actions cog is disabled (ACTIONS_ENABLED=FALSE)")
            if config("REMINDERS_ENABLED", default="TRUE").upper() != "TRUE":
                self.reminders_enabled = False
                Extensions.remove("cogs.Reminders")
                logging.info("Reminders cog is disabled (REMINDERS_ENABLED=FALSE)")

            # used for checking whether this is WL!
            self.environment = environment
            self.emoji_controller = EmojiController(self)

            await self.emoji_controller.prefetch_emojis()

            for extension in Extensions:
                try:
                    if extension not in BETA_EXT:
                        await self.load_extension(extension)
                        logging.info(f"Loaded {extension}")
                    elif environment in ["DEVELOPMENT", "ALPHA"]:
                        await self.load_extension(extension)
                        logging.info(f"Loaded {extension}")
                except Exception as e:
                    logging.error(f"Failed to load extension {extension}.", exc_info=e)

            for extension in Events:
                try:
                    await self.load_extension(extension)
                    logging.info(f"Loaded {extension}")
                except Exception as e:
                    logging.error(f"Failed to load extension {extension}.", exc_info=e)

            bot.error_list = []
            logging.info("Connected to MongoDB!")

            # await bot.load_extension("jishaku")
            await bot.load_extension("utils.hot_reload")
            # await bot.load_extension('utils.server')

            if not bot.is_synced:  # check if slash commands have been synced
                bot.tree.copy_global_to(guild=discord.Object(id=987798554972143728))
            if environment == "DEVELOPMENT":
                pass
                # await bot.tree.sync(guild=discord.Object(id=987798554972143728))
            elif environment == "CUSTOM":
                await self.tree.sync()
                # Prevent auto syncing
                # await bot.tree.sync()
                # guild specific: leave blank if global (global registration can take 1-24 hours)
            bot.is_synced = True

            # we do this so the bot can get a cache of things before we spam discord with fetches
            asyncio.create_task(start_tasks(self))
            
            async for document in self.views.db.find({}):
                if document["view_type"] == "LOAMenu":
                    for index, item in enumerate(document["args"]):
                        if item == "SELF":
                            document["args"][index] = self
                    loa_id = document["args"][3]
                    if isinstance(loa_id, dict):
                        loa_expiry = loa_id["expiry"]
                        if loa_expiry < datetime.datetime.now().timestamp():
                            await self.views.delete_by_id(document["_id"])
                            continue
                    self.add_view(
                        LOAMenu(*document["args"]), message_id=document["message_id"]
                    )
            self.setup_status = True



if config("ENVIRONMENT") == "CUSTOM":
    Bot.__bases__ = (commands.Bot,)

bot = Bot(
    command_prefix=get_prefix,
    case_insensitive=True,
    intents=intents,
    help_command=None,
    allowed_mentions=discord.AllowedMentions(
        replied_user=False, everyone=False, roles=False
    ),
)
bot.is_synced = False
bot.shift_management_disabled = False
bot.punishments_disabled = False
bot.bloxlink_api_key = bloxlink_api_key
environment = config("ENVIRONMENT", default="DEVELOPMENT")
bot.internal_command_storage = {}


def running():
    if bot:
        if bot._ready != MISSING:
            return 1
        else:
            return -1
    else:
        return -1


@bot.before_invoke
async def AutoDefer(ctx: commands.Context):
    if (
        environment == "CUSTOM"
        and config("CUSTOM_GUILD_ID", default="0") != "0"
        and not getattr(ctx.bot, "whitelist_disabled", False)
    ):
        if ctx.guild.id != int(config("CUSTOM_GUILD_ID")):
            if ctx.interaction:
                await ctx.interaction.response.send_message(
                    embed=discord.Embed(
                        title="Not Permitted",
                        description="This bot is not permitted to be used in this server. You can change this in the **Whitelabel Bot Dashboard**.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=True,
                )
                raise Exception(f"Guild not permitted to use this bot: {ctx.guild.id}")

    guild_id = ctx.guild.id
    if (environment != "CUSTOM" or int(config("CUSTOM_GUILD_ID", default="0")) != guild_id) and await has_whitelabel(bot, guild_id):
        if "jishaku" in ctx.command.qualified_name:
            return
        if ctx.interaction:
            await ctx.interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="There is a whitelabel bot already in this server.",
                    color=BLANK_COLOR,
                ),
                ephemeral=True,
            )
        raise Exception("Whitelabel bot already in use")

    bot.internal_command_storage[ctx.message.id] = datetime.datetime.now(tz=pytz.UTC).timestamp()
    if ctx.command:
        if ctx.command.extras.get("ephemeral") is True:
            if ctx.interaction:
                return await ctx.defer(ephemeral=True)
        if ctx.command.extras.get("ignoreDefer") is True:
            return
        await ctx.defer()


@bot.after_invoke
async def loggingCommandExecution(ctx: commands.Context):
    if ctx.message.id in bot.internal_command_storage:
        command_name = ctx.command.qualified_name

        duration = float(
            datetime.datetime.now(tz=pytz.UTC).timestamp()
            - bot.internal_command_storage[ctx.message.id]
        )
        logging.info(
            f"Command {command_name} was run by {ctx.author.name} ({ctx.author.id}) and lasted {duration} seconds"
        )
        shard_info = (
            f"Shard ID ::: {ctx.guild.shard_id}"
            if ctx.guild
            else "Shard ID ::: -1, Direct Messages"
        )
        logging.info(shard_info)
        del bot.internal_command_storage[ctx.message.id]
    else:
        logging.info(
            "Command could not be found in internal context storage. Please report."
        )


@bot.event
async def on_message(
    message,
):  # DO NOT COG

    if not message.guild:
        return await bot.process_commands(message)

    if (
        environment == "CUSTOM"
        and config("CUSTOM_GUILD_ID", default=None) != 0
        and not getattr(bot, "whitelist_disabled", False)
    ):
        if message.guild.id != int(config("CUSTOM_GUILD_ID")):
            ctx = await bot.get_context(message)
            if ctx.command is not None:
                await message.reply(
                    embed=discord.Embed(
                        title="Not Permitted",
                        description="This bot is not permitted to be used in this server. You can change this in the **Whitelabel Bot Dashboard**.",
                        color=BLANK_COLOR,
                    )
                )
                return

    if environment == "PRODUCTION" and await bot.whitelabel.db.find_one({"GuildID": str(message.guild.id)}) is not None:
        return

    await bot.process_commands(message)


client = roblox.Client()


async def staff_check(bot_obj, guild, member):
    guild_settings = await bot_obj.settings.find_by_id(guild.id)
    member_role_ids = [r.id for r in member.roles]
    if guild_settings:
        if "role" in guild_settings["staff_management"].keys():
            if guild_settings["staff_management"]["role"] != "":
                if isinstance(guild_settings["staff_management"]["role"], list):
                    for role_id in guild_settings["staff_management"]["role"]:
                        if role_id in member_role_ids:
                            return True
                elif isinstance(guild_settings["staff_management"]["role"], int):
                    if guild_settings["staff_management"]["role"] in member_role_ids:
                        return True

    if await admin_check(bot_obj, guild, member):
        return True

    if member.guild_permissions.manage_messages:
        return True
    return False


async def management_check(bot_obj, guild, member):
    guild_settings = await bot_obj.settings.find_by_id(guild.id)
    member_role_ids = [r.id for r in member.roles]
    if guild_settings:
        if "management_role" in guild_settings["staff_management"].keys():
            if guild_settings["staff_management"]["management_role"] != "":
                if isinstance(
                    guild_settings["staff_management"]["management_role"], list
                ):
                    for role_id in guild_settings["staff_management"]["management_role"]:
                        if role_id in member_role_ids:
                            return True
                elif isinstance(
                    guild_settings["staff_management"]["management_role"], int
                ):
                    if guild_settings["staff_management"]["management_role"] in member_role_ids:
                        return True
    if member.guild_permissions.manage_guild:
        return True
    return False


async def admin_check(bot_obj, guild, member):
    guild_settings = await bot_obj.settings.find_by_id(guild.id)
    member_role_ids = [r.id for r in member.roles]
    if guild_settings:
        if "admin_role" in guild_settings["staff_management"].keys():
            if guild_settings["staff_management"]["admin_role"] != "":
                if isinstance(guild_settings["staff_management"]["admin_role"], list):
                    for role_id in guild_settings["staff_management"]["admin_role"]:
                        if role_id in member_role_ids:
                            return True
                elif isinstance(guild_settings["staff_management"]["admin_role"], int):
                    if guild_settings["staff_management"]["admin_role"] in member_role_ids:
                        return True
        if "management_role" in guild_settings["staff_management"].keys():
            if guild_settings["staff_management"]["management_role"] != "":
                if isinstance(
                    guild_settings["staff_management"]["management_role"], list
                ):
                    for role_id in guild_settings["staff_management"]["management_role"]:
                        if role_id in member_role_ids:
                            return True
                elif isinstance(
                    guild_settings["staff_management"]["management_role"], int
                ):
                    if guild_settings["staff_management"]["management_role"] in member_role_ids:
                        return True
    if member.guild_permissions.administrator:
        return True
    return False


async def staff_predicate(ctx):
    if ctx.guild is None:
        return True
    else:
        return await staff_check(ctx.bot, ctx.guild, ctx.author)


def is_staff():
    return commands.check(staff_predicate)


async def admin_predicate(ctx):
    if ctx.guild is None:
        return True
    else:
        return await admin_check(ctx.bot, ctx.guild, ctx.author)


def is_admin():
    return commands.check(admin_predicate)


async def management_predicate(ctx):
    if ctx.guild is None:
        return True
    else:
        return await management_check(ctx.bot, ctx.guild, ctx.author)


def is_management():
    return commands.check(management_predicate)


async def check_privacy(bot: Bot, guild: int, setting: str):
    privacySettings = await bot.privacy.find_by_id(guild)
    if not privacySettings:
        return True
    if not setting in privacySettings.keys():
        return True
    return privacySettings[setting]


async def warning_json_to_mongo(jsonName: str, guildId: int):
    with open(f"{jsonName}", "r") as f:
        logging.info(f)
        f = json.load(f)

    logging.info(f)

    for key, value in f.items():
        structure = {"_id": key.lower(), "warnings": []}
        logging.info([key, value])
        logging.info(key.lower())

        if await bot.warnings.find_by_id(key.lower()):
            data = await bot.warnings.find_by_id(key.lower())
            for item in data["warnings"]:
                structure["warnings"].append(item)

        for item in value:
            item.pop("ID", None)
            item["id"] = next(generator)
            item["Guild"] = guildId
            structure["warnings"].append(item)

        logging.info(structure)

        if await bot.warnings.find_by_id(key.lower()) == None:
            await bot.warnings.insert(structure)
        else:
            await bot.warnings.update(structure)
bot.warning_json_to_mongo = warning_json_to_mongo

# Note: Changed to not use hardcoded types as if something does change then you don't need to append to an if chain
if environment in accepted_envs:
    bot_token = config(f"{environment}_BOT_TOKEN", None)
    logging.info(f"Using {environment.lower()} bot token")
    if not bot_token:
        raise Exception("The environment specified does not have a token associated with it")
else:
    raise Exception("Invalid Environment")
# Mongo is critical for bot function so it should most definitely error 
mongo_url = config("MONGO_URL", default=None)
if not mongo_url:
    raise Exception("Missing MongoDB URL")


credentials_dict = {
    "type": config("TYPE", default=""),
    "project_id": config("PROJECT_ID", default=""),
    "private_key_id": config("PRIVATE_KEY_ID", default=""),
    "private_key": config("PRIVATE_KEY", default="").replace("\\n", "\n"),
    "client_email": config("CLIENT_EMAIL", default=""),
    "client_id": config("CLIENT_ID", default=""),
    "auth_uri": config("AUTH_URI", default=""),
    "token_uri": config("TOKEN_URI", default=""),
    "auth_provider_x509_cert_url": config("AUTH_PROVIDER_X509_CERT_URL", default=""),
    "client_x509_cert_url": config("CLIENT_X509_CERT_URL", default=""),
}


def run():
    sentry_sdk.init(
        dsn=sentry_url,
        traces_sample_rate=1.0,
        integrations=[PyMongoIntegration()],
        _experiments={
            "profiles_sample_rate": 1.0,
        },
    )

    try:
        bot.run(bot_token)
    except Exception as e:
        with sentry_sdk.isolation_scope() as scope:
            scope.level = "error"
            capture_exception(e)
        raise e


if __name__ == "__main__":
    run()
