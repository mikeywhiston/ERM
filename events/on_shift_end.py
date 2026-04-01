import asyncio # 🕒 Importing asyncio...
import datetime # 📅 Importing datetime...

import aiohttp # 🌐 Importing aiohttp...
import discord # 📦 Importing discord...
from bson import ObjectId # 🆔 Importing ObjectId...
from discord.ext import commands # 🛠️ Importing commands...
from datamodels.ShiftManagement import ShiftItem # 📄 Importing ShiftItem...
from utils.constants import BLANK_COLOR # 🎨 Importing BLANK_COLOR...
from utils.timestamp import td_format # ⏳ Importing td_format...
from decouple import config # ⚙️ Importing config...


class OnShiftEnd(commands.Cog): # 🏫 Defining OnShiftEnd cog...
    # ⚙️ Initializing cog...
    def __init__(self, bot: commands.Bot): # 🛠️ Initializing OnShiftEnd...
        self.bot = bot # 🤖 Setting bot instance...

    @commands.Cog.listener() # 👂 Registering listener...
    # ⏹️ Handling shift end event...
    async def on_shift_end(self, object_id: ObjectId): # ⚡ Handling on_shift_end...

        document = await self.bot.shift_management.shifts.find_by_id(object_id) # 🔍 Finding shift doc...
        if not document: # ❓ If doc missing...
            return # ⏹️ Returning...
        shift: ShiftItem = await self.bot.shift_management.fetch_shift(object_id) # 📥 Fetching shift object...

        url_var = config("BASE_API_URL") # 🌐 Getting Base API URL...
        panel_url_var = config("PANEL_API_URL") # 🌐 Getting Panel API URL...

        guild_id = document["Guild"] # 🏰 Extracting guild ID...
        
        # 🔄 Syncing end shift with APIs...
        async def sync_end_with_apis(): # 🔄 Defining sync helper...
            async with aiohttp.ClientSession() as session: # 🌐 Opening HTTP session...
                tasks = [] # 🆕 Initializing tasks list...

                if url_var not in ["", None]: # ❓ If base URL exists...
                    tasks.append( # ➕ Adding base sync task...
                        session.get(
                            f"{url_var}/Internal/SyncEndShift/{document['UserID']}/{guild_id}",
                            headers={"Authorization": config("INTERNAL_API_AUTH")},
                            raise_for_status=True,
                        )
                    )

                if panel_url_var not in ["", None]: # ❓ If panel URL exists...
                    tasks.append( # ➕ Adding panel sync task...
                        session.delete(
                            f"{panel_url_var}/{guild_id}/SyncEndShift?ID={document['_id']}",
                            headers={"X-Static-Token": config("PANEL_STATIC_AUTH")},
                            raise_for_status=True,
                        )
                    )

                if tasks: # ❓ If tasks created...
                    responses = await asyncio.gather(*tasks, return_exceptions=True) # 🏁 Executing tasks...
                    for response in responses: # ➰ Iterating responses...
                        if isinstance(response, Exception): # ❓ If error occurred...
                            self.logger.error( # 📢 Logging sync failure...
                                f"End shift API sync failed: {str(response)}"
                            )

        try: # 🛡️ Attempting sync...
            await sync_end_with_apis() # 🔄 Executing sync helper...
        except aiohttp.ClientError as e: # ⚠️ Handling client error...
            self.logger.error(f"Failed to sync shift end with APIs: {str(e)}") # 📢 Logging error...
        except Exception as e: # ⚠️ Handling unexpected error...
            self.logger.error(f"Unexpected error during end shift API sync: {str(e)}") # 📢 Logging error...

        guild: discord.Guild = self.bot.get_guild(shift.guild) # 🏰 Getting guild...
        if guild is None: # ❓ If guild not found...
            return # ⏹️ Returning...

        guild_settings = await self.bot.settings.find_by_id(guild.id) # ⚙️ Fetching settings...
        if not guild_settings: # ❓ If settings missing...
            return # ⏹️ Returning...

        shift_type = shift.type # 🏷️ Getting shift type...
        custom_shift_type = None # 🆕 Initializing custom type...
        if shift_type != "Default": # ❓ If not default...
            total_shift_types = guild_settings.get("shift_types", {"types": []}) # 📜 Fetching types list...
            for item in total_shift_types["types"]: # ➰ Iterating types...
                if item["name"] == shift_type: # ✨ Matching name...
                    custom_shift_type = item # 🎯 Setting custom type...

        assigned_roles = [] # 🆕 Initializing assigned roles...
        break_roles = [] # 🆕 Initializing break roles...
        if custom_shift_type is None: # ❓ If standard or not found...
            try: # 🛡️ Attempting fetch...
                channel = await guild.fetch_channel( # 📺 Fetching default channel...
                    guild_settings.get("shift_management").get("channel", 0)
                )
            except discord.HTTPException: # ⚠️ Handling error...
                channel = None # 🚫 No channel...
            nickname_prefix = guild_settings.get("shift_management").get( # 🏷️ Getting default prefix...
                "nickname_prefix", None
            )
            assigned_roles = guild_settings.get("shift_management").get("role", []) # 🎭 Getting default assigned roles...
            break_roles = guild_settings.get("shift_management").get("break_roles", []) # 🎭 Getting default break roles...
        else:
            try:
                channel = await guild.fetch_channel(custom_shift_type.get("channel", 0))
            except discord.HTTPException:
                try:
                    channel = await guild.fetch_channel(
                        guild_settings.get("shift_management").get("channel", 0)
                    )
                except discord.HTTPException:
                    channel = None
            nickname_prefix = custom_shift_type.get("nickname", None)
            assigned_roles = custom_shift_type.get("role", [])
            break_roles = custom_shift_type.get("break_roles", [])

        try:
            staff_member: discord.Member = await guild.fetch_member(shift.user_id)
        except discord.NotFound:
            return

        if not staff_member:
            return
        for role in assigned_roles or []:
            discord_role: discord.Role = guild.get_role(role)
            if discord_role is None:
                continue
            try:
                await staff_member.remove_roles(discord_role, atomic=True)
            except discord.HTTPException:
                pass

        for role in break_roles or []:
            discord_role: discord.Role = guild.get_role(role)
            if discord_role is None:
                continue
            try:
                await staff_member.remove_roles(discord_role, atomic=True)
            except discord.HTTPException:
                pass

        if nickname_prefix is not None:
            try:
                await staff_member.edit(
                    nick=f"{(staff_member.nick or staff_member.display_name).removeprefix(nickname_prefix)}"
                )
            except discord.HTTPException:
                pass

        moderation_counts = {}
        for entry in shift.moderations:
            entry = await self.bot.punishments.fetch_warning(str(entry))

            if entry.warning_type in moderation_counts:
                moderation_counts[entry.warning_type] += 1
            else:
                moderation_counts[entry.warning_type] = 1

        if channel is not None:
            await channel.send(
                embed=discord.Embed(title="Shift Ended", color=BLANK_COLOR)
                .add_field(
                    name="Shift Information",
                    value=(
                        f"> **Staff Member:** {staff_member.mention}\n"
                        f"> **Shift Type:** {shift_type}\n"
                    ),
                    inline=False,
                )
                .add_field(
                    name="Other Information",
                    value=(
                        f"> **Shift Start:** <t:{int(shift.start_epoch)}>\n"
                        f"> **Shift End:** <t:{int(shift.end_epoch)}>\n"
                        f"> **Shift Length:** {td_format(datetime.timedelta(seconds=shift.end_epoch - shift.start_epoch - (sum((br.end_epoch) - (br.start_epoch) for br in shift.breaks)) + (shift.added_time if shift.added_time > (86400 * 7) else 0) - (shift.removed_time if shift.removed_time > (86400 * 7) else 0)))}\n"
                        f"> **Nickname:** `{shift.nickname}`\n"
                    ),
                    inline=False,
                )
                .add_field(
                    name="Moderation Details:",
                    value=(
                        "\n".join(
                            [
                                f"> **{moderation_type.capitalize()}s:** {count}"
                                for moderation_type, count in moderation_counts.items()
                            ]
                        )
                        if moderation_counts
                        else "> No Moderations Found"
                    ),
                    inline=False,
                )
                .set_author(
                    name=guild.name, icon_url=guild.icon.url if guild.icon else ""
                )
                .set_thumbnail(url=staff_member.display_avatar.url)
            )
        shift_reports_enabled = True
        async for document in self.bot.consent.db.find({"_id": staff_member.id}):
            shift_reports_enabled = (
                document.get("shift_reports")
                if document.get("shift_reports") is not None
                else True
            )
        if shift_reports_enabled:
            embed = (
                discord.Embed(title="Shift Report", color=BLANK_COLOR)
                .add_field(
                    name="Shift Information",
                    value=(
                        f"> **Shift Type:** {shift_type}\n"
                        f"> **Shift Start:** <t:{int(shift.start_epoch)}>\n"
                        f"> **Shift End:** <t:{int(shift.end_epoch)}>\n"
                        f"> **Nickname:** `{shift.nickname}`\n"
                    ),
                    inline=False,
                )
                .add_field(
                    name="Total Moderations:",
                    value=(
                        "\n".join(
                            [
                                f"> **{moderation_type.capitalize()}s:** {count}"
                                for moderation_type, count in moderation_counts.items()
                            ]
                        )
                        if moderation_counts
                        else "> No Moderations Found"
                    ),
                    inline=False,
                )
                .add_field(
                    name="Elapsed Time",
                    value=f"> {td_format(datetime.timedelta(seconds=shift.end_epoch - shift.start_epoch - (sum((br.end_epoch) - (br.start_epoch) for br in shift.breaks)) + (shift.added_time if shift.added_time > (86400 * 7) else 0) - (shift.removed_time if shift.removed_time > (86400 * 7) else 0)))}",
                    inline=False,
                )
                .set_thumbnail(url=staff_member.display_avatar.url)
            )
            await staff_member.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(OnShiftEnd(bot))
