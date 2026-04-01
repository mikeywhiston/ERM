import asyncio
import logging
import time

import discord
from decouple import config
from discord.ext import tasks

from utils import prc_api
from utils.prc_api import Player, ServerStatus
from utils.utils import fetch_get_channel

_guild_cache = {}
_channel_cache = {}
_cache_timeout = 300

async def get_cached_guild(bot, guild_id):
    """Get guild with caching"""
    # 🏰 Getting guild from cache...
    cache_key = f"guild_{guild_id}"
    now = time.time()
    
    if cache_key in _guild_cache:
        guild, timestamp = _guild_cache[cache_key]
        if now - timestamp < _cache_timeout and guild:
            return guild
    
    try:
        guild = await bot.fetch_guild(guild_id)
    except discord.errors.NotFound:
        guild = None
    except Exception as e:
        logging.error(f"Error fetching guild {guild_id}: {e}")
        guild = None
    
    _guild_cache[cache_key] = (guild, now)
    return guild

async def get_cached_channel(bot, guild, channel_id):
    """Get channel with caching"""
    # 📺 Getting channel from cache...
    cache_key = f"channel_{guild.id}_{channel_id}"
    now = time.time()
    
    if cache_key in _channel_cache:
        channel, timestamp = _channel_cache[cache_key]
        if now - timestamp < _cache_timeout and channel:
            return channel
    
    try:
        channel = await fetch_get_channel(guild, int(channel_id))
    except Exception as e:
        logging.error(f"Error fetching channel {channel_id} in guild {guild.id}: {e}")
        channel = None
    
    _channel_cache[cache_key] = (channel, now)
    return channel


async def update_channel(bot, guild, channel_id, stat_config, placeholders):
    # 🔄 Updating channel name...
    """Update channel name with statistics and caching"""
    try:
        channel = await get_cached_channel(bot, guild, channel_id)
        if channel:
            format_string = stat_config["format"]
            for key, value in placeholders.items():
                format_string = format_string.replace(f"{{{key}}}", str(value))

            if channel.name != format_string:
                await channel.edit(name=format_string)
                logging.info(f"Updated channel {channel_id} in guild {guild.id}")
            else:
                logging.debug(
                    f"Skipped update for channel {channel_id} in guild {guild.id} - no changes needed"
                )
        else:
            logging.error(f"Channel {channel_id} not found in guild {guild.id}")
    except Exception as e:
        logging.error(
            f"Failed to update channel {channel_id} in guild {guild.id}: {e}", exc_info=True
        )


@tasks.loop(minutes=5, reconnect=True)
async def statistics_check(bot):
    """
    # 📊 Running statistics check...
    Statistics Check with caching and batch processing optimization.
    """
    initial_time = time.time()
    
    semaphore = asyncio.Semaphore(3)
    
    async def process_guild(guild_data):
        async with semaphore:
            guild_id = guild_data["_id"]
            logging.info(f"Processing statistics for guild {guild_id}")
            
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
