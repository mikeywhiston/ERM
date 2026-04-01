import datetime # 📅 Importing datetime...
import logging # 📝 Importing logging...
import discord # 📦 Importing discord...
from discord.ext import commands # 🛠️ Importing commands...
from utils.constants import BLANK_COLOR # 🎨 Importing BLANK_COLOR...

logger = logging.getLogger(__name__) # 🕵️ Setting up logger...


class OnInfractionCreate(commands.Cog): # 🏫 Defining OnInfractionCreate cog...
    # ⚙️ Initializing cog...
    def __init__(self, bot): # 🛠️ Initializing OnInfractionCreate...
        self.bot = bot # 🤖 Setting bot instance...

    # 🔄 Replacing variables...
    def replace_variables(self, data, variables): # 🔧 Defining replacement method...
        if isinstance(data, str): # ❓ If data is a string...
            result = data # 📥 Taking string...
            for key, value in variables.items(): # ➰ Iterating variables...
                result = result.replace(key, value) # 🔄 Replacing keys with values...
            return result # 📤 Returning result...
        elif isinstance(data, dict): # ❓ If data is a dictionary...
            result = {} # 🆕 Creating new dict...
            for key, value in data.items(): # ➰ Iterating items...
                if key == "color" and isinstance(value, (int, float)): # 🎨 Handling color key...
                    result[key] = int(value) # 🔢 Converting to int...
                elif isinstance(value, (dict, list)): # ❓ If nested structure...
                    result[key] = self.replace_variables(value, variables) # 🔄 Recursing...
                elif isinstance(value, str): # ❓ If value is string...
                    result[key] = self.replace_variables(value, variables) # 🔄 Replacing in string...
                else: # ✨ For other types...
                    result[key] = value # 📥 Keeping value...
            return result # 📤 Returning dict...
        elif isinstance(data, list): # ❓ If data is a list...
            return [self.replace_variables(item, variables) for item in data] # ➰ Mapping over list...
        return data # 📤 Returning original data...

    @commands.Cog.listener() # 👂 Registering listener...
    # 📝 Handling infraction create event...
    async def on_infraction_create(self, infraction_doc): # ⚡ Handling on_infraction_create...
        try: # 🛡️ Attempting execution...
            guild = self.bot.get_guild(infraction_doc["guild_id"]) # 🏰 Getting guild...
            if not guild: # ❓ If guild not found...
                return # ⏹️ Returning...

            member = guild.get_member(infraction_doc["user_id"]) # 👥 Getting member...
            if not member: # ❓ If member not in cache...
                try: # 🛡️ Attempting fetch...
                    member = await guild.fetch_member(infraction_doc["user_id"]) # 👥 Fetching member...
                except: # ⚠️ Handling fetch error...
                    return # ⏹️ Returning...

            settings = await self.bot.settings.find_by_id(guild.id) # ⚙️ Fetching settings...
            if not settings or "infractions" not in settings: # ❓ If settings missing...
                return # ⏹️ Returning...

            infraction_config = next( # 🔍 Finding config for type...
                (
                    inf
                    for inf in settings["infractions"]["infractions"]
                    if inf["name"] == infraction_doc["type"]
                ),
                None,
            )
            if not infraction_config: # ❓ If config not found...
                return # ⏹️ Returning...

            # Set up variables for replacements
            issuer = None # 👤 Initializing issuer...
            if issuer_id := infraction_doc.get("issuer_id"): # ❓ If issuer ID exists...
                try: # 🛡️ Attempting fetch...
                    issuer = guild.get_member(issuer_id) or await guild.fetch_member( # 👥 Fetching issuer...
                        issuer_id
                    )
                except: # ⚠️ Handling error...
                    pass # 💨 Continuing...

            variables = { # 📊 Defining replacement variables...
                "{user}": member.mention, # 👤 Mention...
                "{user.name}": member.name, # 🏷️ Name...
                "{user.id}": str(member.id), # 🆔 ID...
                "{user.tag}": str(member), # 🏷️ Tag...
                "{guild}": guild.name, # 🏰 Guild name...
                "{guild.id}": str(guild.id), # 🏰 Guild ID...
                "{guild.icon}": str(guild.icon.url) if guild.icon else "", # 🖼️ Icon URL...
                "{reason}": infraction_doc["reason"], # 📝 Reason...
                "{type}": infraction_doc["type"], # 🏷️ Type...
                "{issuer}": f"<@{infraction_doc.get('issuer_id', '0')}>", # 👤 Issuer mention...
                "{issuer.id}": str(infraction_doc.get("issuer_id", "0")), # 📋 Issuer ID...
                "{issuer.name}": issuer.name if issuer else "Unknown", # 🏷️ Issuer name...
                "{timestamp}": f"<t:{int(datetime.datetime.now().timestamp())}:F>", # 🕒 Long format time...
                "{timestamp.short}": f"<t:{int(datetime.datetime.now().timestamp())}:f>", # 🕒 Short format time...
                "{timestamp.relative}": f"<t:{int(datetime.datetime.now().timestamp())}:R>", # 🕒 Relative time...
                "{escalated}": ( # 📈 Escalation status...
                    "Yes" if infraction_doc.get("escalated", False) else "No"
                ),
                "{count}": str( # 🔢 Total infractions...
                    await self.bot.db.infractions.count_documents(
                        {
                            "user_id": member.id,
                            "guild_id": guild.id,
                            "type": infraction_doc["type"],
                        }
                    )
                ),
                "{user.username}": infraction_doc.get("username", member.name),
                "{issuer.username}": infraction_doc.get("issuer_username", "Unknown"),
            }

            # Process role changes
            roles_added = []
            roles_removed = []

            if infraction_config.get("role_changes"):
                # Handle role additions
                if infraction_config["role_changes"].get("add"):
                    await self._process_role_add(
                        infraction_config["role_changes"]["add"],
                        guild,
                        member,
                        infraction_doc,
                        roles_added,
                    )

                if infraction_config["role_changes"].get("remove"):
                    await self._process_role_remove(
                        infraction_config["role_changes"]["remove"],
                        guild,
                        member,
                        infraction_doc,
                        roles_removed,
                    )

            if roles_added or roles_removed:
                await self._update_role_changes(
                    infraction_doc, roles_added, roles_removed
                )

            if infraction_config.get("notifications"):
                await self._process_notifications(
                    infraction_config["notifications"], guild, member, variables
                )

            await self._process_additional_actions(infraction_config, guild, member)

        except Exception as e:
            logger.error(f"Error processing infraction: {e}")

    async def _process_role_add(
        self, add_config, guild, member, infraction_doc, roles_added
    ):
        roles_to_add = []
        for role_id in add_config.get("roles", []):
            try:
                role = guild.get_role(int(role_id))
                if role and role not in member.roles:
                    roles_to_add.append(role)
                    roles_added.append(role.id)
            except Exception as e:
                logger.error(f"Failed to process add role {role_id}: {e}")

        if roles_to_add:
            try:
                await member.add_roles(
                    *roles_to_add, reason=f"Infraction {infraction_doc['type']}"
                )
                if add_config.get("temporary") and add_config.get("duration"):
                    infraction_doc["temp_roles_added"] = [r.id for r in roles_to_add]
                    infraction_doc["temp_roles_added_expiry"] = (
                        datetime.datetime.now().timestamp() + add_config["duration"]
                    )
            except Exception as e:
                logger.error(f"Failed to add roles: {e}")

    async def _process_role_remove(
        self, remove_config, guild, member, infraction_doc, roles_removed
    ):
        roles_to_remove = []
        for role_id in remove_config.get("roles", []):
            try:
                role = guild.get_role(int(role_id))
                if role and role in member.roles:
                    roles_to_remove.append(role)
                    roles_removed.append(role.id)
            except Exception as e:
                logger.error(f"Failed to process remove role {role_id}: {e}")

        if roles_to_remove:
            try:
                await member.remove_roles(
                    *roles_to_remove, reason=f"Infraction {infraction_doc['type']}"
                )
                if remove_config.get("temporary") and remove_config.get("duration"):
                    infraction_doc["temp_roles_removed"] = [
                        r.id for r in roles_to_remove
                    ]
                    infraction_doc["temp_roles_removed_expiry"] = (
                        datetime.datetime.now().timestamp() + remove_config["duration"]
                    )
            except Exception as e:
                logger.error(f"Failed to remove roles: {e}")

    async def _process_notifications(self, notifications, guild, member, variables):
        if notifications.get("dm", {}).get("enabled"):
            dm_config = notifications["dm"]
            content = self.replace_variables(dm_config.get("content", ""), variables)
            if dm_config.get("embed"):
                try:
                    embed = discord.Embed.from_dict(
                        self.replace_variables(dm_config["embed"], variables)
                    )
                    await member.send(content=content or None, embed=embed)
                except Exception as e:
                    logger.error(f"Failed to send DM notification: {e}")

        if notifications.get("public", {}).get("enabled"):
            public_config = notifications["public"]
            content = self.replace_variables(
                public_config.get("content", ""), variables
            )
            if public_config.get("embed"):
                try:
                    embed = discord.Embed.from_dict(
                        self.replace_variables(public_config["embed"], variables)
                    )
                    if channel_id := public_config.get("channel_id"):
                        if channel := guild.get_channel(int(channel_id)):
                            await channel.send(content=content or None, embed=embed)
                except Exception as e:
                    logger.error(f"Failed to send public notification: {e}")

    async def _process_additional_actions(self, config, guild, member):
        if config.get("remove_ingame_perms", False):
            try:
                roblox_info = await self.bot.bloxlink.find_roblox(member.id)
                if roblox_info and "robloxID" in roblox_info:
                    roblox_id = roblox_info["robloxID"]
                    await self.bot.prc_api.run_command(guild.id, f":unmod {roblox_id}")
                    await self.bot.prc_api.run_command(
                        guild.id, f":unadmin {roblox_id}"
                    )
            except Exception as e:
                logger.error(f"Failed to remove in-game permissions: {e}")

        if config.get("end_shift", False):
            try:
                current_shift = await self.bot.shift_management.get_current_shift(
                    member, guild.id
                )
                if current_shift:
                    await self.bot.shift_management.end_shift(
                        current_shift["_id"], guild.id
                    )
                    self.bot.dispatch("shift_end", current_shift["_id"])
            except Exception as e:
                logger.error(f"Failed to end shift: {e}")

    async def _update_role_changes(self, infraction_doc, roles_added, roles_removed):
        if roles_added or roles_removed:
            update_data = {"roles_modified": True}
            if roles_added:
                update_data["roles_added"] = roles_added
            if roles_removed:
                update_data["roles_removed"] = roles_removed

            try:
                await self.bot.db.infractions.update_one(
                    {"_id": infraction_doc["_id"]}, {"$set": update_data}
                )
            except Exception as e:
                logger.error(
                    f"Failed to update infraction document with role changes: {e}"
                )


async def setup(bot):
    await bot.add_cog(OnInfractionCreate(bot))
