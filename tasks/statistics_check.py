import asyncio # 🔄 Import asyncio
import logging # 📝 Import logging
import time # ⏱️ Import time

import discord # 📦 Import discord
from decouple import config # ⚙️ Import config
from discord.ext import tasks # 🚀 Import tasks

from utils import prc_api # 🔌 Import prc_api
from utils.prc_api import Player, ServerStatus # 👤 Import models
from utils.utils import fetch_get_channel # 🛠️ Import channel helper

_guild_cache = {} # 🗄️ Cache for guilds
_channel_cache = {} # 🗄️ Cache for channels
_cache_timeout = 300 # ⏲️ Cache expiry

async def get_cached_guild(bot, guild_id): # 🏰 Get guild with caching
    """Get guild with caching"""
    # 🏰 Getting guild from cache...
    cache_key = f"guild_{guild_id}" # 🔑 Cache key
    now = time.time() # 🕒 Current time
    
    if cache_key in _guild_cache: # 💾 Check cache
        guild, timestamp = _guild_cache[cache_key]
        if now - timestamp < _cache_timeout and guild: # ✅ Return if valid
            return guild
    
    try: # 🏢 Fetch guild from API
        guild = await bot.fetch_guild(guild_id)
    except discord.errors.NotFound: # ❓ Flag as None if missing
        guild = None
    except Exception as e: # 🔴 Log other errors
        logging.error(f"Error fetching guild {guild_id}: {e}")
        guild = None
    
    _guild_cache[cache_key] = (guild, now) # 📥 Update cache
    return guild

async def get_cached_channel(bot, guild, channel_id): # 📺 Get channel with caching
    """Get channel with caching"""
    # 📺 Getting channel from cache...
    cache_key = f"channel_{guild.id}_{channel_id}" # 🔑 Cache key
    now = time.time() # 🕒 Current time
    
    if cache_key in _channel_cache: # 💾 Check cache
        channel, timestamp = _channel_cache[cache_key]
        if now - timestamp < _cache_timeout and channel: # ✅ Return if valid
            return channel
    
    try: # 📟 Fetch channel object
        channel = await fetch_get_channel(guild, int(channel_id))
    except Exception as e: # 🔴 Log failures
        logging.error(f"Error fetching channel {channel_id} in guild {guild.id}: {e}")
        channel = None
    
    _channel_cache[cache_key] = (channel, now) # 📥 Update cache
    return channel


async def update_channel(bot, guild, channel_id, stat_config, placeholders): # 🔄 Update channel name
    # 🔄 Updating channel name...
    """Update channel name with statistics and caching"""
    try:
        channel = await get_cached_channel(bot, guild, channel_id) # 📺 Fetch channel
        if channel:
            format_string = stat_config["format"] # 📝 Get format string
            for key, value in placeholders.items(): # 🔁 Replace placeholders
                format_string = format_string.replace(f"{{{key}}}", str(value))

            if channel.name != format_string: # 🔄 Only update if different
                await channel.edit(name=format_string)
                logging.info(f"Updated channel {channel_id} in guild {guild.id}")
            else: # ⏭️ Skip redundant update
                logging.debug(
                    f"Skipped update for channel {channel_id} in guild {guild.id} - no changes needed"
                )
        else: # 🔴 Channel missing error
            logging.error(f"Channel {channel_id} not found in guild {guild.id}")
    except Exception as e: # ⚠️ Log update failure
        logging.error(
            f"Failed to update channel {channel_id} in guild {guild.id}: {e}", exc_info=True
        )


@tasks.loop(minutes=5, reconnect=True) # ⏰ Run every 5 mins
async def statistics_check(bot): # 📊 Running statistics check...
    """
    Statistics Check with caching and batch processing optimization.
    """
    initial_time = time.time() # ⏱️ Benchmark start
    
    semaphore = asyncio.Semaphore(3) # 🚦 Concurrency lock
    
    async def process_guild(guild_data): # 🛠️ Logic per guild
        async with semaphore: # 🛑 Limit simultaneous requests
            guild_id = guild_data["_id"] # 🆔 Fetch ID
            logging.info(f"Processing statistics for guild {guild_id}") # 📝 Log guild check
            
            try:
                guild = await get_cached_guild(bot, guild_id)
                if not guild:
                    logging.error(f"Guild {guild_id} not found")
                    return

                settings = await bot.settings.find_by_id(guild_id)
                if (
                    not settings
                    or "ERLC" not in settings
                    or "statistics" not in settings["ERLC"]
                ):
                    logging.debug(f"No statistics configuration for guild {guild_id}")
                    return

                statistics = settings["ERLC"]["statistics"]
                
                try:
                    players: list[Player] = await bot.prc_api.get_server_players(guild_id)
                    status: ServerStatus = await bot.prc_api.get_server_status(guild_id)
                    queue: int = await bot.prc_api.get_server_queue(guild_id, minimal=True)
                except prc_api.ResponseFailure as e:
                    logging.error(f"PRC ResponseFailure for guild {guild_id}: {e}")
                    return

                on_duty = await bot.shift_management.shifts.db.count_documents(
                    {"Guild": guild_id, "EndEpoch": 0}
                )
                moderators = len(
                    list(filter(lambda x: x.permission == "Server Moderator", players))
                )
                admins = len(
                    list(filter(lambda x: x.permission == "Server Administrator", players))
                )
                staff_ingame = len(list(filter(lambda x: x.permission != "Normal", players)))
                current_player = status.current_players
                join_code = status.join_key
                max_players = status.max_players

                placeholders = {
                    "onduty": on_duty,
                    "staff": staff_ingame,
                    "mods": moderators,
                    "admins": admins,
                    "players": current_player,
                    "join_code": join_code,
                    "max_players": max_players,
                    "queue": queue,
                }

                channel_tasks = [
                    update_channel(bot, guild, channel_id, stat_config, placeholders)
                    for channel_id, stat_config in statistics.items()
                ]
                await asyncio.gather(*channel_tasks, return_exceptions=True)
                
            except Exception as e:
                logging.error(f"Error processing guild {guild_id}: {e}", exc_info=True)
                return

    # Process guilds in batches
    guild_tasks = []
    async for guild_data in bot.settings.db.find(
        {"ERLC.statistics": {"$exists": True}}
    ):
        guild_tasks.append(process_guild(guild_data))
        
        # Process in batches of 5 to avoid overwhelming the system
        if len(guild_tasks) >= 5:
            await asyncio.gather(*guild_tasks, return_exceptions=True)
            guild_tasks = []
            await asyncio.sleep(1)  # Small delay between batches
    
    # Process remaining guilds
    if guild_tasks:
        await asyncio.gather(*guild_tasks, return_exceptions=True)

    execution_time = time.time() - initial_time
    logging.info(f"Statistics check completed in {execution_time:.2f} seconds")
