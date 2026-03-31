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

async def get_cached_member_by_username(guild, username):
    """Get member by username with caching"""
    now = time.time()
    cache_key = f"{guild.id}_{username.lower()}"

    if cache_key in _member_search_cache[guild.id]:
        member_obj, cached_time = _member_search_cache[guild.id][cache_key]
        if now - cached_time < _cache_timeout:
            return member_obj

    member = None
    members = await guild.query_members(query=username, limit=1)
    if members:
        member = members[0] if members else None

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

async def handle_callsign_check(guild, callsign, settings, member):
    """Handle callsign check for a member"""
    if not callsign or not member:
        return False

    try:
        callsign_settings = settings.get("ERLC", {}).get("callsign_check", {})
        if not isinstance(callsign_settings, dict):
            logging.error("callsign_check is not a dictionary in settings['ERLC']")
            return True

        if not callsign_settings.get("enabled", False):
            return True

        for prefix_key, role_id in callsign_settings.items():
            if prefix_key == "enabled":
                continue

            if not prefix_key.startswith("prefix_"):
                continue

            prefix = prefix_key.replace("prefix_", "")

            if re.match(rf"^{re.escape(prefix)}", callsign, re.IGNORECASE):
                try:
                    role_id = int(role_id)
                    required_role = guild.get_role(role_id)

                    if not required_role:
                        logging.warning(f"Role {role_id} not found in guild {guild.id}")
                        continue

                    if required_role not in member.roles:
                        logging.info(f"Member {member.display_name} ({member.id}) missing role {required_role.name} for callsign {callsign}")
                        return False
                    return True

                except (ValueError, TypeError):
                    logging.error(f"Invalid role ID {role_id} for prefix {prefix} in guild {guild.id}")
                    continue

        return True

    except Exception as e:
        logging.error(f"Error in handle_callsign_check: {e}", exc_info=True)
        return True

async def process_discord_checks(bot, items, guild_id):
    """
    This function will process Discord checks for PRC servers.
    """
    try:
        settings = items["ERLC"].get("discord_checks", {})
        if not settings:
            return

        if not settings.get("enabled", False):
            return
        
        message = settings.get("message", "Please join the Private Server Communication channel.")
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
            players = await bot.prc_api.get_server_players(guild_id)
            if not players:
                logging.info(f"No players found in guild {guild_id}")
                return

        except Exception as e:
            logging.error(f"Failed to fetch server data for guild {guild_id}: {e}")
            return
        
        not_in_discord = []
        callsign_violations = []
        
        for player in players:
            member = await get_cached_member_by_username(guild, player.username)
            if not member:
                not_in_discord.append(player)
            #======WILL BE IMPLEMENTED IN NEXT UPDATE======
            # else:
            #     callsign_valid = await handle_callsign_check(guild, player.callsign, items, member)
            #     if not callsign_valid:
            #         callsign_violations.append(player)
        try:
            kick_after = settings.get("kick_after", 0)
        except Exception as e:
            logging.error(f"Error getting kick_after setting for guild {guild_id}: {e}")
            kick_after = 0

        if not_in_discord:
            await handle_discord_check_batch(bot, guild, not_in_discord, channel, message, kick_after)
        
        if callsign_violations:
            if not settings.get("callsign_check", {}).get("enabled", False):
                logging.info(f"Callsign check is disabled for guild {guild_id}. Skipping callsign violations.")
                return
            callsign_alert_channel_id = settings.get("callsign_check", {}).get("channel_id", 0)
            callsign_channel = None
            if callsign_alert_channel_id != 0:
                callsign_channel = await get_cached_channel(bot, callsign_alert_channel_id)
                if not callsign_channel:
                    logging.error(f"Callsign alert channel {callsign_alert_channel_id} not found in guild {guild_id}.")
                    return
            await handle_callsign_violations_batch(bot, guild, callsign_violations, callsign_channel)

    except Exception as e:
        logging.error(f"Error processing guild {guild_id}: {e}", exc_info=True)
        return

@tasks.loop(minutes=10, reconnect=True)
async def prc_automations(bot):
    """
    Automated Discord Checks for PRC Servers.
    """
    initial_time = time.time()

    base = {"ERLC": {"$exists": True, "$ne": None}}
    pipeline = [
        {"$match": base},
        {
            "$lookup": {
                "from": "server_keys",
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
            logging.info(f"Processing guild ID: {guild_id} | PRC Automations: Discord Checks & Callsign Checks")
            await process_discord_checks(bot, items, guild_id)

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
    logging.info(f"PRC Automations completed in {execution_time:.2f} seconds.")


async def handle_discord_check_batch(bot, guild, players_not_in_discord, alert_channel, alert_message, kick_after=0):
    """Handle batch of players not in Discord"""
    if not players_not_in_discord:
        return
    
    try:
        usernames = [player.username for player in players_not_in_discord]
        command = f":pm {','.join(usernames)} {alert_message}"

        await bot.prc_api.run_command(guild.id, command)

        if not hasattr(bot, 'discord_check_counter'):
            bot.discord_check_counter = {}
        
        players_to_kick = []
        for player in players_not_in_discord:
            key = f"{guild.id}_{player.username}"
            if key not in bot.discord_check_counter:
                bot.discord_check_counter[key] = 1
            else:
                bot.discord_check_counter[key] += 1

            if bot.discord_check_counter[key] >= kick_after and kick_after > 0:
                players_to_kick.append(player)
                bot.discord_check_counter.pop(key)

        if players_to_kick and alert_channel is not None:
            await send_batch_warning_embed(players_to_kick, alert_channel)

    except Exception as e:
        logging.error(f"Error in handle_discord_check_batch: {e}")


async def send_batch_warning_embed(players, alert_channel):
    """Send warning embed for multiple players"""
    try:
        player_list = []
        for player in players:
            player_list.append(f"[{player.username}](https://roblox.com/users/{player.id}/profile)")
        
        embed = discord.Embed(
            title="Discord Check Warning",
            description=f"""
            > The following players have been kicked from the server for not joining the Discord server after multiple warnings:
            
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


async def handle_callsign_violations_batch(bot, guild, players_with_violations, alert_channel):
    """Handle batch of players with callsign violations"""
    if not players_with_violations:
        return
    
    try:
        usernames = [player.username for player in players_with_violations]
        violation_message = "Your callsign does not match your assigned role. Please update your callsign or contact staff."
        command = f":pm {','.join(usernames)} {violation_message}"

        await bot.prc_api.run_command(guild.id, command)
    
        if alert_channel is not None:
            await send_callsign_violation_embed(players_with_violations, alert_channel)
            
        logging.info(f"Processed {len(players_with_violations)} callsign violations in guild {guild.id}")

    except Exception as e:
        logging.error(f"Error in handle_callsign_violations_batch: {e}")


async def send_callsign_violation_embed(players, alert_channel):
    """Send callsign violation embed for multiple players"""
    try:
        player_list = []
        for player in players:
            player_list.append(f"[{player.username}](https://roblox.com/users/{player.id}/profile) - Callsign: `{player.callsign}`")
        
        embed = discord.Embed(
            title="Callsign Violation Warning",
            description=f"""
            > The following players have callsigns that don't match their assigned roles:
            
            {chr(10).join([f"> • {player}" for player in player_list])}
            """,
            color=0xFFA500,
        )

        await alert_channel.send(embed=embed)
    except discord.HTTPException as e:
        logging.error(f"Failed to send callsign violation embed: {e}")
    except Exception as e:
        logging.error(f"Error in send_callsign_violation_embed: {e}", exc_info=True)