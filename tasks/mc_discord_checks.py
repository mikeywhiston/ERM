import re
import time
import discord
from discord.ext import tasks
import logging
import asyncio
from collections import defaultdict
import datetime
import pytz

from utils.constants import BLANK_COLOR


_guild_cache = {}
_member_search_cache = defaultdict(dict)
_cache_timeout = 300

async def get_cached_member_by_username(bot, guild, username):
    """Get member by username with caching"""
    now = time.time()
    cache_key = f"{guild.id}_{username.lower()}"

    if cache_key in _member_search_cache[guild.id]:
        member_obj, cached_time = _member_search_cache[guild.id][cache_key]
        if now - cached_time < _cache_timeout:
            return member_obj

    member = await bot.accounts.roblox_to_discord(guild, username)

    _member_search_cache[guild.id][cache_key] = (member, now)
    return member

async def get_cached_guild(bot, guild_id):
    """Get guild with caching"""
    now = time.time()
    cache_key = f"guild_{guild_id}"

    if cache_key in _guild_cache:
        guild_obj, cached_time = _guild_cache[cache_key]
        if now - cached_time < _cache_timeout and guild_obj:
            return guild_obj

    guild = bot.get_guild(guild_id)
    if not guild:
        try:
            guild = await bot.fetch_guild(guild_id)
        except discord.HTTPException:
            guild = None

    _guild_cache[cache_key] = (guild, now)
    return guild


async def get_cached_channel(bot, channel_id):
    """Get channel with caching"""
    now = time.time()
    cache_key = f"channel_{channel_id}"

    if cache_key in _guild_cache:
        channel_obj, cached_time = _guild_cache[cache_key]
        if now - cached_time < _cache_timeout and channel_obj:
            return channel_obj

    channel = bot.get_channel(channel_id)
    if not channel:
        try:
            channel = await bot.fetch_channel(channel_id)
        except discord.HTTPException:
            channel = None

    _guild_cache[cache_key] = (channel, now)
    return channel


@tasks.loop(minutes=10, reconnect=True)
async def mc_discord_checks(bot):
    """
    Automated Discord Checks for MC Servers.
    """
    initial_time = time.time()

    base = {"MC.discord_checks.enabled": True}
    pipeline = [
        {"$match": base},
        {
            "$lookup": {
                "from": "mc_keys",
                "localField": "_id",
                "foreignField": "_id",
                "as": "server_key",
            }
        },
        {"$match": {"server_key": {"$ne": []}}},
    ]
    
    semaphore = asyncio.Semaphore(3)
    async def process_guild(items):
        async with semaphore:
            guild_id = items["_id"]
            logging.info(f"Processing guild ID: {guild_id}")

            try:
                settings = items["MC"].get("discord_checks", {})
                if not settings:
                    return

                if not settings.get("enabled", False):
                    return
                
                channel_id = settings.get("channel_id", 0)
                channel = None
                if channel_id != 0:
                    channel = await get_cached_channel(bot, channel_id)
                    if not channel:
                        logging.error(f"Channel {channel_id} not found in guild {guild_id}.")
                        return
                    
                guild = await get_cached_guild(bot, guild_id)
                if not guild:
                    return

                try:
                    players = await bot.mc_api.get_server_players(guild_id)
                    if not players:
                        logging.info(f"No players found in guild {guild_id}")
                        return

                except Exception as e:
                    logging.error(f"Failed to fetch server data for guild {guild_id}: {e}")
                    return
                
                not_in_discord = []
                for player in players:
                    member = await get_cached_member_by_username(bot, guild, player.username)
                    if not member:
                        not_in_discord.append(player)
                
                if not_in_discord:
                    await handle_discord_check_batch(bot, guild, not_in_discord, channel)
            
            except Exception as e:
                logging.error(f"Error processing guild {guild_id}: {e}", exc_info=True)
                return

    guild_tasks = []
    async for items in await bot.settings.db.aggregate(pipeline):
        guild_tasks.append(process_guild(items))

        if len(guild_tasks) >= 5:
            await asyncio.gather(*guild_tasks, return_exceptions=True)
            guild_tasks = []
            await asyncio.sleep(2)

    if guild_tasks:
        await asyncio.gather(*guild_tasks, return_exceptions=True)
    
    execution_time = time.time() - initial_time
    logging.info(f"MC Discord Checks completed in {execution_time:.2f} seconds")


async def handle_discord_check_batch(bot, guild, players_not_in_discord, alert_channel):
    """Handle batch of players not in Discord"""
    if not players_not_in_discord:
        return
    
    try:
        if alert_channel:
            await send_batch_warning_embed(players_not_in_discord, alert_channel)

    except Exception as e:
        logging.error(f"Error in handle_discord_check_batch: {e}")


async def send_batch_warning_embed(players, alert_channel):
    """Send warning embed for multiple players"""
    try:
        player_list = []
        for player in players:
            player_list.append(f"[{player.username}](https://roblox.com/users/{player.id}/profile)")
        
        embed = discord.Embed(
            title="Maple County Discord Check Alert",
            description=f"""
            > The following players are currently in the server but not in the Discord server:
            
            {chr(10).join([f"> • {player}" for player in player_list])}
            """,
            color=BLANK_COLOR,
            timestamp=datetime.datetime.now(tz=pytz.UTC),
        )

        await alert_channel.send(embed=embed)
    except discord.HTTPException as e:
        logging.error(f"Failed to send batch embed: {e}")
    except Exception as e:
        logging.error(f"Error in send_batch_warning_embed: {e}", exc_info=True)