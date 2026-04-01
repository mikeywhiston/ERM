import discord # 📦 Import discord
import logging # 📦 Import logging

from decouple import config # 📦 Import config
from discord.ext import commands, tasks # 📦 Import commands and tasks
import time # 📦 Import time
import datetime # 📦 Import datetime
from utils.constants import BLANK_COLOR # 📦 Import BLANK_COLOR
import pytz # 📦 Import pytz


@tasks.loop(hours=1) # ⏰ Run every hour
async def check_infractions(bot):
    # ⚖️ Checking infractions for expiry...
    try:
        current_time = datetime.datetime.now(tz=pytz.UTC).timestamp() # 🕒 Get current timestamp
        initial_time = time.time() # ⏱️ Mark start time

        async for infraction in bot.db.infractions.find( # 🔍 Find temp roles
            {"temp_roles_expire_at": {"$exists": True}}
        ):
            if infraction["temp_roles_expire_at"] <= current_time: # ⌛ Check if expired
                try:
                    guild = bot.get_guild(infraction["guild_id"]) # 🏰 Get guild
                    if not guild: # ❓ Skip if no guild
                        continue

                    member = guild.get_member(infraction["user_id"]) # 👤 Get member
                    if not member: # ❓ Skip if no member
                        continue

                    if infraction.get("temp_roles_added"): # 🎒 Check added roles
                        roles_to_remove = [] # 🗑️ Roles to remove list
                        for role_id in infraction["temp_roles_added"]: # 📑 Iterate role IDs
                            role = guild.get_role(int(role_id)) # 🛡️ Get role object
                            if role: # ✅ Add if role exists
                                roles_to_remove.append(role)
                        if roles_to_remove: # ⚔️ Remove roles from member
                            await member.remove_roles(
                                *roles_to_remove,
                                reason="Temporary infraction role duration expired",
                            )

                    if infraction.get("temp_roles_removed"): # 🎒 Check removed roles
                        roles_to_add = [] # ➕ Roles to add list
                        for role_id in infraction["temp_roles_removed"]: # 📑 Iterate role IDs
                            role = guild.get_role(int(role_id)) # 🛡️ Get role object
                            if role: # ✅ Add if role exists
                                roles_to_add.append(role)
                        if roles_to_add: # ⚔️ Add roles back to member
                            await member.add_roles(
                                *roles_to_add,
                                reason="Temporary infraction role removal expired",
                            )

                    await bot.db.infractions.update_one( # 💾 Update database
                        {"_id": infraction["_id"]},
                        {
                            "$unset": {
                                "temp_roles_expire_at": "",
                                "temp_roles_added": "",
                                "temp_roles_removed": "",
                            }
                        },
                    )
                except Exception as e: # ⚠️ Handle errors
                    logging.error(
                        f"Error processing temporary roles for infraction {infraction['_id']}: {str(e)}"
                    )

        cached_settings = {} # 🗄️ Cache for guild settings
        async for infraction in bot.db.infractions.find( # 🔍 Find un-revoked infractions
            {"revoked": {"$ne": True}, "check_executed": {"$exists": False}}
        ):
            try:
                guild_id = infraction["guild_id"] # 🆔 Get guild ID
                guild = bot.get_guild(guild_id) # 🏰 Get guild
                if not guild: # ❓ Skip if no guild
                    continue

                if not cached_settings.get(guild_id): # 🌩️ Check cache
                    settings = await bot.settings.find_by_id(guild_id) # ⚙️ Fetch settings
                    if not settings or not settings.get("infractions", {}).get(
                        "infractions"
                    ):
                        continue
                    cached_settings[guild_id] = settings # 💾 Store in cache

                settings = cached_settings[guild_id] # ⚙️ Use cached settings
                infraction_type = next( # 🔍 Match infraction type
                    (
                        t
                        for t in settings["infractions"]["infractions"]
                        if t.get("name") == infraction["type"]
                    ),
                    None,
                )

                if (
                    not infraction_type
                    or not infraction_type.get("expiry", {}).get("enabled") # 🚫 Skip if expiry disabled
                    or not infraction_type.get("expiry", {}).get("duration") # 🚫 Skip if no duration
                ):
                    continue

                expiry_days = infraction_type["expiry"]["duration"] # 🗓️ Get expiry days
                expiry_seconds = expiry_days * 24 * 60 * 60 # ⏱️ Convert to seconds

                if infraction["timestamp"] <= current_time - expiry_seconds: # ⌛ Check if expired
                    member = guild.get_member(infraction["user_id"]) # 👤 Get member
                    if member: # ✅ If member exists
                        try:
                            embed = discord.Embed( # 📧 Create notification embed
                                title="Infraction Expired",
                                description=f"Your infraction in {guild.name} has expired.",
                                color=BLANK_COLOR,
                            )
                            embed.add_field( # 📝 Add detail field
                                name="Details",
                                value=(
                                    f"> **Type:** {infraction['type']}\n"
                                    f"> **Reason:** {infraction['reason']}\n"
                                    f"> **Expired At:** <t:{int(current_time)}:F>"
                                ),
                                inline=False,
                            )
                            await member.send(embed=embed) # 🗳️ Send DM to member
                        except discord.Forbidden: # 🚫 Handle DM blocked
                            logging.warning(
                                f"Could not send DM to {member.id} about expired infraction"
                            )

                        role_changes = infraction_type.get("role_changes", {}) # 🏷️ Get role changes

                        if role_changes.get("add", {}).get("roles"): # ➕ Temporary roles to remove
                            roles_to_remove = [] # 🗑️ Removal list
                            for role_id in role_changes["add"]["roles"]: # 📑 Loop IDs
                                role = guild.get_role( # 🛡️ Get role object
                                    int(role_id["$numberLong"])
                                    if isinstance(role_id, dict)
                                    else int(role_id)
                                )
                                if role: # ✅ Add if role exists
                                    roles_to_remove.append(role)
                            if roles_to_remove: # ⚔️ Remove roles from member
                                await member.remove_roles(
                                    *roles_to_remove, reason="Infraction expired"
                                )

                        if role_changes.get("remove", {}).get("roles"): # ➖ Restoring removed roles
                            roles_to_add = [] # ➕ Additive list
                            for role_id in role_changes["remove"]["roles"]: # 📑 Loop IDs
                                role = guild.get_role( # 🛡️ Get role object
                                    int(role_id["$numberLong"])
                                    if isinstance(role_id, dict)
                                    else int(role_id)
                                )
                                if role: # ✅ Add if role exists
                                    roles_to_add.append(role)
                            if roles_to_add: # ⚔️ Add roles back
                                await member.add_roles(
                                    *roles_to_add, reason="Infraction expired"
                                )

                        if infraction_type.get("remove_ingame_perms"): # 🏢 Check in-game perms
                            try:
                                await bot.prc_api.run_command( # 🎮 Execute mod command
                                    guild_id, f":mod {infraction['user_id']}"
                                )
                            except Exception as e: # 🔴 Log errors
                                logging.error(
                                    f"Failed to restore in-game permissions: {str(e)}"
                                )

                    await bot.db.infractions.update_one( # 💾 Revoke infraction in database
                        {"_id": infraction["_id"]},
                        {
                            "$set": {
                                "revoked": True,
                                "revoked_at": current_time,
                                "reason": infraction["reason"]
                                + " - Revoked by system since this infraction expired.",
                                "check_executed": True,
                            }
                        },
                    )

            except Exception as e: # ⚠️ Log iteration error
                logging.error(
                    f"Error processing infraction expiry for {infraction['_id']}: {str(e)}"
                )

        end_time = time.time() # ⏱️ Mark end time
        logging.warning( # 📝 Log task duration
            "Event check_infractions took {} seconds".format(
                str(end_time - initial_time)
            )
        )

    except Exception as e:
        logging.error(f"Error in check_infractions task: {str(e)}")
