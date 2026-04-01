import logging # 📝 Import logging
import random # 🎲 Import random
import asyncio # 🔄 Import asyncio
from functools import lru_cache # 💾 Import lru_cache
from collections import defaultdict # 🗄️ Import defaultdict

import discord # 📦 Import discord
from decouple import config # ⚙️ Import config
from discord.ext import commands, tasks # 🚀 Import commands, tasks
from discord.ext.commands.view import StringView # 🔍 Import StringView

import utils.prc_api # 🔌 Import prc_api
from utils import prc_api # 🔌 Import prc_api
from utils.prc_api import Player # 👤 Import Player
from utils.conditions import * # ⚙️ Import conditions
import datetime # 📅 Import datetime
import pytz # 🌍 Import pytz

_guild_cache = {} # 🗄️ Cache for guilds
_guild_cache_timeout = 300 # ⏲️ Cache expiry time


def _evict_guild_cache(): # 🧹 Clean up guild cache
    # 🏰 Evicting guild cache entries...
    now = datetime.datetime.now().timestamp()
    stale = [k for k, (_, t) in _guild_cache.items() if now - t >= _guild_cache_timeout]
    for k in stale: # ❌ Remove old guilds
        del _guild_cache[k]


async def get_cached_guild(bot, guild_id): # 🏛️ Get guild with caching
    """Get guild with caching to reduce API calls"""
    # 🏛️ Retrieving cached guild...
    now = datetime.datetime.now().timestamp()

    if guild_id in _guild_cache: # 💾 Check cache
        guild_obj, cached_time = _guild_cache[guild_id]
        if now - cached_time < _guild_cache_timeout: # ✅ Return if fresh
            return guild_obj

    guild = bot.get_guild(guild_id) # 🔍 Get from memory
    if not guild: # 🌐 Fetch if missing
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.HTTPException: # 🔴 Handle fetch error
            return None

    _guild_cache[guild_id] = (guild, now) # 📥 Update cache
    return guild


async def handle_erlc_condition(bot, guild_id, condition) -> bool: # 🕹️ Evaluating ERLC condition...
    api_client = bot.prc_api # 🔌 Default API
    if await bot.mc_api.get_server_key(guild_id) is not None: # 🔑 Check for MC key
        api_client = bot.mc_api
    try:
        players = await api_client.get_server_players(guild_id) # 👥 Fetch players
    except prc_api.ResponseFailure: # ⚠️ Fail if API error
        return False

    values = [] # 📑 Comparison values
    for item in (condition["Variable"], condition["Value"]): # 🔄 Check both sides
        if str(item).split(" ")[0] not in variable_table: # 🔢 Constant value
            values.append(
                int(item) if str(item).isdigit() else str(item)
            )  # this means we're comparing a raw constant
            continue
        cond, args = separate_arguments(item) # 🛠️ Parse variable
        futures = await fetch_predetermined_futures( # 🔮 Get future data
            bot, guild_id, condition, item, api_client
        )

        func, func_args = determine_func_info(cond) # 🛠️ Get handler function
        submitted_arguments = [
            players
        ]  # change the 1st submitted argument to be our players object
        if func_args[0] != "players":  # we already have players, we can use this
            submitted_arguments = []

        for item in func_args[0 if func_args[0] != "players" else 1 :]: # 📥 Prepare args
            submitted_arguments.append(futures[item.lower()]())
        if len(func_args) > 1: # 🚀 Execute logic
            values.append(func(*submitted_arguments))
        else:
            values.append(func(*submitted_arguments))

    new_values = [] # 📑 Cleaned values
    # unfuture the values
    for value in values: # 🔄 Resolution loop
        if isinstance(value, asyncio.Future):
            new_values.append(await value)
        else:
            new_values.append(value)
    
    return handle_comparison_operations(*values, condition["Operation"]) # ⚖️ Perform comparison

async def handle_erm_condition(bot, guild_id, condition) -> bool: # 🤖 Evaluating ERM condition...
    values = []
    for item in (condition["Variable"], condition["Value"]):
        if str(item).split(" ")[0] not in variable_table:
            values.append(int(item) if item.isdigit() else item)
            continue
        cond, args = separate_arguments(item)
        futures = await fetch_predetermined_futures(bot, guild_id, condition, item)

        func, func_args = determine_func_info(cond)
        submitted_arguments = []
        for item in func_args:
            submitted_arguments.append(futures[item.lower()]())

        if len(func_args) > 1:
            values.append(func(*submitted_arguments, *args))
        else:
            values.append(func(*submitted_arguments))

    return handle_comparison_operations(*values, condition["Operation"])


@tasks.loop(minutes=1)
async def iterate_conditions(bot):
    # 🔄 Evaluating all guild conditions...
    _evict_guild_cache()
    semaphore = asyncio.Semaphore(5)
    async def process_action(action):
        async with semaphore:
            try:
                guild = await get_cached_guild(bot, action["Guild"])
                if not guild:
                    return
                
                conditions = []
                for condition in action["Conditions"]:
                    if (
                        condition["Variable"].split(" ")[0] in value_finder_table.keys()
                        or condition["Value"].split(" ")[0] in value_finder_table.keys()
                    ):
                        conditions.append(
                            await handle_erlc_condition(bot, action["Guild"], condition)
                        )
                    else:
                        conditions.append(
                            await handle_erm_condition(bot, action["Guild"], condition)
                        )

                logic_gates = []
                for item in action["Conditions"]:
                    logic_gates.append(item.get("LogicGate"))

                new_conditions = []
                if len(conditions) > 0 and len(logic_gates) > 0:
                    for idx, (condition, logic_gate) in enumerate(
                        dict(zip(conditions, logic_gates)).items()
                    ):
                        if logic_gate is None:
                            new_conditions.append(condition)
                            continue
                        if logic_gate.upper() == "AND":
                            new_conditions.append(
                                condition is True and conditions[idx - 1] is True
                            )
                        if logic_gate.upper() == "OR":
                            new_conditions.append(
                                condition is True or conditions[idx - 1] is True
                            )
                else:
                    new_conditions = conditions
                    
                if all(new_conditions):
                    now_ts = int(datetime.datetime.now(tz=pytz.timezone("UTC")).timestamp())
                    if action.get("LastExecuted") is not None:
                        if now_ts - action["LastExecuted"] < action.get(
                            "ConditionExecutionInterval", 300
                        ):
                            return

                    await bot.actions.db.update_one(
                        {"_id": action["_id"]}, {"$set": {"LastExecuted": now_ts}}
                    )

                    channels = guild.channels or await guild.fetch_channels()

                    try:
                        ctx = commands.Context(
                            message=discord.Message(
                                state=random.choice(channels)._state,
                                channel=random.choice(channels),
                                data={
                                    "author": {"id": guild.owner_id},
                                    "content": "",
                                    "id": -1000,
                                    "type": 0,
                                },
                            ),
                            bot=bot,
                            view=StringView(f"actions execute {action['ActionName']}"),
                        )
                        ctx.dnr = True

                        owner = (
                            guild.owner
                            or guild.get_member(guild.owner_id)
                            or await guild.fetch_member(guild.owner_id)
                        )
                        ctx.message.author = owner

                        await ctx.invoke(
                            bot.get_command("actions execute"), action=action["ActionName"]
                        )
                    except Exception as e:
                        logging.warning(f"Failed to fully execute condition: {e}")
            except Exception as e:
                logging.warning(f"Failed to initialise execution of condition: {e}")

    actions = [
        i
        async for i in bot.actions.db.find(
            {"Conditions": {"$exists": True, "$ne": []}}
        )
    ]
    
    batch_size = 10
    for i in range(0, len(actions), batch_size):
        batch = actions[i:i + batch_size]
        await asyncio.gather(*[process_action(action) for action in batch], return_exceptions=True)
        
        # Add delay between batches
        if i + batch_size < len(actions):
            await asyncio.sleep(2)

    logging.info("[CONDITIONS] Iterated through all conditions.")
