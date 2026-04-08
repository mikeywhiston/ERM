import datetime
import re
import time
import discord
import pytz
from decouple import config
from discord.ext import commands, tasks
import logging
import asyncio
import roblox
from collections import defaultdict

from utils.constants import RED_COLOR, BLANK_COLOR
from utils.prc_api import Player
from utils import prc_api
from utils.utils import is_whitelisted, run_command

_guild_cache = {}
_member_search_cache = defaultdict(dict)
_cache_timeout = 300


def _evict_caches():
    now = time.time()
    stale_keys = [k for k, (_, t) in _guild_cache.items() if now - t >= _cache_timeout]
    for k in stale_keys:
        del _guild_cache[k]

    empty_guilds = []
    for guild_id, members in _member_search_cache.items():
        stale = [k for k, (_, t) in members.items() if now - t >= _cache_timeout]
        for k in stale:
            del members[k]
        if not members:
            empty_guilds.append(guild_id)
    for guild_id in empty_guilds:
        del _member_search_cache[guild_id]


@tasks.loop(minutes=10, reconnect=True)
async def check_whitelisted_car(bot):
    _evict_caches()
    initial_time = time.time()
    logging.info("Starting check_whitelisted_car task")

    base = {"ERLC.vehicle_restrictions.enabled": True}
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
            logging.info(f"Processing guild ID: {guild_id}")

            try:
                settings = items["ERLC"].get("vehicle_restrictions", {})
                if not settings:
                    return

                whitelisted_vehicle_roles = settings.get("roles", [])
                alert_channel_id = settings.get("channel")
                whitelisted_vehicles = settings.get("cars", [])
                alert_message = settings.get(
                    "message", "You do not have the required role to use this vehicle."
                )

                if (
                    not whitelisted_vehicle_roles
                    or not alert_channel_id
                    or not whitelisted_vehicles
                ):
                    return

                guild = await get_cached_guild(bot, guild_id)
                if not guild:
                    return

                alert_channel = await get_cached_channel(bot, alert_channel_id)
                if not alert_channel:
                    return

                exotic_roles = await get_cached_roles(guild, whitelisted_vehicle_roles)
                if not exotic_roles:
                    return

                try:
                    players, vehicles = await asyncio.gather(
                        bot.prc_api.get_server_players(guild_id),
                        bot.prc_api.get_server_vehicles(guild_id),
                        return_exceptions=True,
                    )

                    if isinstance(players, Exception) or isinstance(vehicles, Exception):
                        logging.error(f"Failed to fetch server data for guild {guild_id}")
                        return

                except Exception as e:
                    logging.error(f"Failed to fetch server data for guild {guild_id}: {e}")
                    return

                player_lookup = {p.username: p for p in players}

                batch_size = 5
                for i in range(0, len(vehicles), batch_size):
                    batch = vehicles[i : i + batch_size]
                    await asyncio.gather(
                        *[
                            process_vehicle(
                                bot,
                                guild,
                                player_lookup,
                                vehicle,
                                whitelisted_vehicles,
                                exotic_roles,
                                alert_channel,
                                alert_message,
                            )
                            for vehicle in batch
                        ],
                        return_exceptions=True,
                    )

                    if i + batch_size < len(vehicles):
                        await asyncio.sleep(1)

            except discord.errors.NotFound:
                logging.error(f"Guild or channel not found: {guild_id}")
                return
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

    end_time = time.time()
    logging.info(
        f"Event check_whitelisted_car completed in {end_time - initial_time:.2f} seconds"
    )


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


async def get_cached_roles(guild, role_ids):
    """Get roles with caching"""
    exotic_roles = []
    if isinstance(role_ids, int):
        role = guild.get_role(role_ids)
        if role:
            exotic_roles = [role]
    elif isinstance(role_ids, list):
        exotic_roles = [r for r_id in role_ids if (r := guild.get_role(r_id))]

    return exotic_roles


async def process_vehicle(
    bot, guild, player_lookup, vehicle, whitelisted_vehicles, exotic_roles, alert_channel, alert_message
):
    """Process individual vehicle check"""
    try:
        player = player_lookup.get(vehicle.username)
        if not player:
            return

        def normalize_vehicle_name(name):
            name = name.lower().strip()
            year = None
            year_match = re.search(r"\b(19|20)\d{2}\b", name)
            if year_match:
                year = year_match.group(0)
                name = name.replace(year, "").strip()
            name = " ".join(name.split())
            return name, year

        vehicle_name, vehicle_year = normalize_vehicle_name(vehicle.vehicle)
        is_whitelisted = False

        for wv in whitelisted_vehicles:
            whitelist_name, whitelist_year = normalize_vehicle_name(str(wv))
            if vehicle_name == whitelist_name and (
                not vehicle_year
                or not whitelist_year
                or vehicle_year == whitelist_year
            ):
                is_whitelisted = True
                break

        if not is_whitelisted:
            return

        member = await get_cached_member_by_username(bot, guild, player.username, [i.id for i in exotic_roles])

        if member:
            if not any(role in member.roles for role in exotic_roles):
                await run_command(bot, guild.id, player.username, alert_message)
                await handle_pm_counter(bot, player, guild, alert_channel)
        else:
            await handle_non_member(bot, player, guild, alert_channel, alert_message)

    except Exception as e:
        logging.error(f"Error processing vehicle for {vehicle.username}: {e}")


async def get_cached_member_by_username(bot, guild, username, exotic_roles):
    """Get member by username with caching"""
    now = time.time()
    cache_key = f"{guild.id}_{username.lower()}"

    if cache_key in _member_search_cache[guild.id]:
        member_obj, cached_time = _member_search_cache[guild.id][cache_key]
        if now - cached_time < _cache_timeout:
            return member_obj

    member = await bot.accounts.roblox_to_discord(guild, username, roles=exotic_roles)

    _member_search_cache[guild.id][cache_key] = (member, now)
    return member


async def handle_pm_counter(bot, player, guild, alert_channel):
    if player.username not in bot.pm_counter:
        bot.pm_counter[player.username] = 1
    else:
        bot.pm_counter[player.username] += 1

    if bot.pm_counter[player.username] >= 4:
        await send_warning_embed(bot, player, guild, alert_channel)
        bot.pm_counter.pop(player.username)


async def handle_non_member(bot, player, guild, alert_channel, alert_message):
    await run_command(bot, guild.id, player.username, alert_message)
    await handle_pm_counter(bot, player, guild, alert_channel)


async def send_warning_embed(bot, player, guild, alert_channel):
    try:
        user = await bot.roblox.get_user(int(player.id))
        avatar = await bot.roblox.thumbnails.get_user_avatar_thumbnails(
            [user], type=roblox.thumbnails.AvatarThumbnailType.headshot
        )
        avatar_url = avatar[0].image_url if avatar else None

        embed = discord.Embed(
            title="Whitelisted Vehicle Warning",
            description=f"""
            > I've PM'd [{player.username}](https://roblox.com/users/{player.id}/profile) three times that they are in a whitelisted vehicle without the required role.
            """,
            color=BLANK_COLOR,
            timestamp=datetime.datetime.now(tz=pytz.UTC),
        )

        if avatar_url:
            embed.set_thumbnail(url=avatar_url)

        await alert_channel.send(embed=embed)
    except discord.HTTPException as e:
        logging.error(f"Failed to send embed for {player.username}: {e}")
    except Exception as e:
        logging.error(
            f"Error in send_warning_embed for {player.username}: {e}", exc_info=True
        )
