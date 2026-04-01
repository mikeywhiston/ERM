import datetime # 📅 Import datetime
import asyncio # 🔄 Import asyncio
from collections import defaultdict # 🗄️ Import defaultdict

import discord # 📦 Import discord
from decouple import config # ⚙️ Import config
from discord.ext import commands, tasks # 🚀 Import commands, tasks

from utils.constants import RED_COLOR, BLANK_COLOR # 🎨 Import colors

_member_cache = defaultdict(dict) # 🗄️ In-memory member cache
_member_cache_timeout = 300 # ⏲️ Cache timeout in seconds


def _evict_member_cache(): # 🧹 Function to clear stale cache
    # 🧹 Evicting stale member cache...
    now = datetime.datetime.now().timestamp() # 🕒 Current time
    empty_guilds = [] # 🗑️ List for guilds to remove
    for guild_id, members in _member_cache.items(): # 📑 Iterate cached guilds
        stale = [uid for uid, (_, t) in members.items() if now - t >= _member_cache_timeout] # 🔍 Find stale entries
        for uid in stale: # ❌ Delete stale users
            del members[uid]
        if not members: # 🏷️ Mark empty guilds
            empty_guilds.append(guild_id)
    for guild_id in empty_guilds: # 🧼 Remove empty guilds from cache
        del _member_cache[guild_id]


async def get_cached_member(guild, user_id): # 👤 Get member with caching
    """Get member with caching to reduce API calls"""
    # 👤 Fetching or getting cached member...
    now = datetime.datetime.now().timestamp() # 🕒 Current time

    if user_id in _member_cache[guild.id]: # 💾 Check if in cache
        member_obj, cached_time = _member_cache[guild.id][user_id]
        if now - cached_time < _member_cache_timeout: # ✅ Return if fresh
            return member_obj

    member = guild.get_member(user_id) # 🔍 Get from guild memory
    if not member: # 🌐 Fetch if not found
        try:
            member = await guild.fetch_member(user_id)
        except discord.HTTPException: # 🔴 Handle fetch error
            member = None

    _member_cache[guild.id][user_id] = (member, now) # 📥 Update cache
    return member


@tasks.loop(minutes=1, reconnect=True) # ⏰ Run every minute
async def check_loa(bot): # 🗓️ Checking LOA status for members...
    _evict_member_cache() # 🧼 Cleanup cache
    try: # 🛡️ Start processing
        guild_loas = defaultdict(list) # 📚 Group LOAs by guild

        async for loaObject in bot.loas.db.find( # 🔍 Find expired LOAs
            {"expired": False, "expiry": {"$lt": datetime.datetime.now().timestamp()}}
        ):
            guild_loas[loaObject["guild_id"]].append(loaObject) # 📥 Add to guild group

        for guild_id, loas in guild_loas.items(): # 📑 Iterate guilds
            try:
                guild = bot.get_guild(guild_id) # 🏰 Get guild object
                if not guild: # ❓ Skip if missing
                    continue

                settings = await bot.settings.find_by_id(guild.id) # ⚙️ Get settings
                if not settings: # ❓ Skip if no settings
                    continue

                roles = [None] # 🎫 Default role list
                if "loa_role" in settings.get("staff_management", {}): # 📂 Check role config
                    try:
                        loa_role_config = settings["staff_management"]["loa_role"]
                        if isinstance(loa_role_config, int): # 🔢 Single role ID
                            role = guild.get_role(loa_role_config)
                            roles = [role] if role else [None]
                        elif isinstance(loa_role_config, list): # 📑 Multiple role IDs
                            roles = [
                                guild.get_role(role_id) for role_id in loa_role_config
                            ]
                            roles = [r for r in roles if r is not None] # ✅ Filter valid
                    except KeyError: # ⚠️ Handle missing keys
                        pass

                batch_size = 5 # 📦 Process in batches
                for i in range(0, len(loas), batch_size): # 🔁 Loop through batches
                    batch = loas[i : i + batch_size]
                    await asyncio.gather( # ⚡ Process LOAs concurrently
                        *[
                            process_loa(bot, guild, loa, settings, roles)
                            for loa in batch
                        ],
                        return_exceptions=True, # 🛡️ Don't crash on batch error
                    )

                    if i + batch_size < len(loas): # 💤 Sleep between batches
                        await asyncio.sleep(1)

            except Exception as e:
                print(f"Error processing guild {guild_id}: {e}")

    except ValueError:
        pass


async def process_loa(bot, guild, loaObject, settings, roles):
    """Process individual LOA expiration"""
    # 📝 Processing individual LOA...
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
        print(f"Error processing LOA {loaObject.get('_id')}: {e}")
