import datetime
import asyncio
from collections import defaultdict

import discord
from decouple import config
from discord.ext import commands, tasks

from utils.constants import RED_COLOR, BLANK_COLOR

_member_cache = defaultdict(dict)
_member_cache_timeout = 300


def _evict_member_cache():
    now = datetime.datetime.now().timestamp()
    empty_guilds = []
    for guild_id, members in _member_cache.items():
        stale = [uid for uid, (_, t) in members.items() if now - t >= _member_cache_timeout]
        for uid in stale:
            del members[uid]
        if not members:
            empty_guilds.append(guild_id)
    for guild_id in empty_guilds:
        del _member_cache[guild_id]


async def get_cached_member(guild, user_id):
    """Get member with caching to reduce API calls"""
    now = datetime.datetime.now().timestamp()

    if user_id in _member_cache[guild.id]:
        member_obj, cached_time = _member_cache[guild.id][user_id]
        if now - cached_time < _member_cache_timeout:
            return member_obj

    member = guild.get_member(user_id)
    if not member:
        try:
            member = await guild.fetch_member(user_id)
        except discord.HTTPException:
            member = None

    _member_cache[guild.id][user_id] = (member, now)
    return member


@tasks.loop(minutes=1, reconnect=True)
async def check_loa(bot):
    _evict_member_cache()
    try:
        guild_loas = defaultdict(list)

        async for loaObject in bot.loas.db.find(
            {"expired": False, "expiry": {"$lt": datetime.datetime.now().timestamp()}}
        ):
            guild_loas[loaObject["guild_id"]].append(loaObject)

        for guild_id, loas in guild_loas.items():
            try:
                guild = bot.get_guild(guild_id)
                if not guild:
                    continue

                settings = await bot.settings.find_by_id(guild.id)
                if not settings:
                    continue

                roles = [None]
                if "loa_role" in settings.get("staff_management", {}):
                    try:
                        loa_role_config = settings["staff_management"]["loa_role"]
                        if isinstance(loa_role_config, int):
                            role = guild.get_role(loa_role_config)
                            roles = [role] if role else [None]
                        elif isinstance(loa_role_config, list):
                            roles = [
                                guild.get_role(role_id) for role_id in loa_role_config
                            ]
                            roles = [r for r in roles if r is not None]
                    except KeyError:
                        pass

                batch_size = 5
                for i in range(0, len(loas), batch_size):
                    batch = loas[i : i + batch_size]
                    await asyncio.gather(
                        *[
                            process_loa(bot, guild, loa, settings, roles)
                            for loa in batch
                        ],
                        return_exceptions=True,
                    )

                    if i + batch_size < len(loas):
                        await asyncio.sleep(1)

            except Exception as e:
                logging.warning(f"Error processing guild {guild_id}: {e}")

    except ValueError:
        pass


async def process_loa(bot, guild, loaObject, settings, roles):
    """Process individual LOA expiration"""
    try:
        if not loaObject["accepted"]:
            return

        loaObject["expired"] = True
        await bot.loas.update_by_id(loaObject)

        member = await get_cached_member(guild, loaObject["user_id"])
        if not member:
            return

        docs = bot.loas.db.find(
            {
                "user_id": loaObject["user_id"],
                "guild_id": loaObject["guild_id"],
                "accepted": True,
                "expired": False,
                "denied": False,
                "type": loaObject["type"],
            }
        )

        should_remove_roles = True
        async for doc in docs:
            if doc != loaObject:
                should_remove_roles = False
                break

        role_removed = None
        if should_remove_roles:
            for role in roles:
                if role and role in member.roles:
                    try:
                        await member.remove_roles(role, reason="LOA Expired", atomic=True)
                    except discord.HTTPException:
                        role_removed = "**Alert:** ⚠️ Failed to remove LOA role due to discord issues.\nContact your Management to manually remove the role!"

        try:
            embed = discord.Embed(
                title=f"{loaObject['type']} Expired",
                description=f"Your {loaObject['type']} has expired in **{guild.name}**\n{role_removed if role_removed else ''}.",
                color=BLANK_COLOR,
            )
            await member.send(embed=embed)
        except discord.Forbidden:
            pass

    except Exception as e:
        logging.warning(f"Error processing LOA {loaObject.get('_id')}: {e}")
