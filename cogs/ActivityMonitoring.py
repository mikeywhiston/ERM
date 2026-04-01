import datetime # 📅 Date and time management

import discord # 🤖 Discord API wrapper
import pytz # 🌍 Timezone handling
from discord import app_commands # 🛠️ Application commands
from discord.ext import commands # 📦 Command extensions
import typing # 📑 Type hinting
from menus import CustomExecutionButton # 🔘 Custom buttons
from utils.constants import BLANK_COLOR, GREEN_COLOR, RED_COLOR # 🎨 Color constants
from erm import is_management # 👮 Management check
from utils.paginators import SelectPagination, CustomPage # 📄 Pagination tools
from utils.timestamp import td_format # ⏱️ Time formatting
from utils.utils import (
    require_settings, # ⚙️ Settings requirement
    time_converter, # 🔄 Time conversion
    get_elapsed_time, # 🕒 Calculating elapsed time
    generalised_interaction_check_failure, # ❌ Error handling for interactions
)


class ActivityMonitoring(commands.Cog): # 📈 Cog for monitoring activity
    # ⚙️ Cog initialization
    def __init__(self, bot: commands.Bot): # 🤖 Constructor
        self.bot = bot # 💾 Store bot instance

    @commands.hybrid_group( # 👨‍👩‍👧‍👦 Define a hybrid group
        name="activity", # 🏷️ Group name
        description="Monitor activity across an entire Staff Team effectively.", # 📝 Description
        extras={"category": "Activity Management"}, # 🗄️ Metadata category
    )
    # 📊 Activity command group
    async def activity(self, ctx: commands.Context): # 📁 Main activity command
        pass # ⏭️ Placeholder

    @commands.guild_only() # 🏠 Server only
    @activity.command( # 🆕 Subcommand
        name="show", # 🏷️ Subcommand name
        description="Show newest activity monitoring report across a time period.", # 📝 Description
        extras={"category": "Activity Management"}, # 🗄️ Metadata category
    )
    @is_management() # 👮 Management only
    @require_settings() # ⚙️ Requires server settings
    # 📉 Show activity report
    async def activity_show( # 📊 Show activity data
        self,
        ctx: commands.Context, # 💬 Command context
        duration: str, # ⏱️ Time period
        selected_role: typing.Optional[discord.Role], # 🎭 Optional role filter
    ):

        settings = await self.bot.settings.find_by_id(ctx.guild.id) # 🔍 Fetch guild settings
        if not settings.get("shift_management").get("enabled"): # 🚫 Check if shifts enabled
            return await ctx.send( # 📣 Send error message
                embed=discord.Embed(
                    title="Not Enabled", # ❌ Error title
                    description="Shift Logging is not enabled on this server.", # 📝 Error description
                    color=BLANK_COLOR, # ⚪ Color
                )
            )

        try:
            actual_conversion = time_converter(duration) # 🔄 Convert duration string
        except ValueError: # ⚠️ Invalid format
            return await ctx.send( # 📣 Send error message
                embed=discord.Embed(
                    title="Invalid Time", # ❌ Error title
                    description="This time format is not accepted by ERM. Please seek the documentation for details", # 📝 Error description
                    color=BLANK_COLOR, # ⚪ Color
                )
            )

        timestamp_pre = ( # 🕒 Calculate start timestamp
            datetime.datetime.now(tz=pytz.UTC).timestamp() - actual_conversion
        )
        timestamp_now = datetime.datetime.now(tz=pytz.UTC).timestamp() # 🕒 Current timestamp

        all_staff = {} # 👥 Staff data storage
        specified_quota_roles = settings.get("shift_management", {}).get( # 🎭 Get quota roles
            "role_quotas", []
        )

        async for shift_document in self.bot.shift_management.shifts.db.find( # 🔍 Query shift DB
            {
                "Guild": ctx.guild.id, # 🆔 Guild filter
                "StartEpoch": {"$gt": timestamp_pre}, # 📅 Since start time
                "EndEpoch": {"$lt": timestamp_now}, # 📅 Until now
            }
        ):

            shift_time = get_elapsed_time(shift_document) # ⏱️ Get duration
            if shift_time > 100_000_000: # 🚫 Sanity check
                continue # ⏭️ Skip invalid
            if shift_document["UserID"] not in all_staff.keys(): # 🆕 New staff member
                try:
                    member = await ctx.guild.fetch_member(shift_document["UserID"]) # 👤 Fetch member
                except discord.NotFound: # ❌ Member left
                    continue # ⏭️ Skip
                if not member: # 🚫 No member found
                    continue # ⏭️ Skip
                roles = member.roles # 🎭 Get roles
                if selected_role is not None:
                    if selected_role not in roles:
                        continue
                sorted_roles = sorted(member.roles, key=lambda x: x.position)
                selected_quota = 0
                for role in sorted_roles:
                    # print(role)
                    # print(specified_quota_roles)
                    if role.id in [t["role"] for t in specified_quota_roles]:
                        found_item = [
                            t for t in specified_quota_roles if t["role"] == role.id
                        ][0]
                        selected_quota = found_item["quota"]

                if selected_quota == 0:
                    selected_quota = settings.get("shift_management").get("quota", 0)
                all_staff[shift_document["UserID"]] = [shift_time, selected_quota]
            else:
                all_staff[shift_document["UserID"]][0] += shift_time

        if selected_role is not None:
            for item in selected_role.members:
                if item.id not in all_staff.keys():
                    all_staff[item.id] = [
                        0,
                        settings.get("shift_management").get("quota", 0),
                    ]


        sorted_all_staff = sorted(all_staff.items(), key=lambda x: x[1], reverse=True)
        # print(sorted_all_staff)
        sorted_staff = dict(
            zip(
                [item[0] for item in sorted_all_staff],
                [item[1] for item in sorted_all_staff],
            )
        )
        # print(sorted_staff)
        leaderboard_string = ""
        loa_string = ""

        for index, (user_id, (seconds, quota)) in enumerate(sorted_staff.items()):
            if not quota:
                quota = 0
            leaderboard_string += f"**{index+1}.** <@{user_id}> • {td_format(datetime.timedelta(seconds=seconds))} {self.bot.emoji_controller.get_emoji('success') if seconds > quota else self.bot.emoji_controller.get_emoji('xmark')}\n"
            if index == len(sorted_staff) - 1:
                break
        else:
            return await ctx.send(
                embed=discord.Embed(
                    title="No Data",
                    description="There is no data to show for this period.",
                    color=BLANK_COLOR,
                )
            )
        embeds = []
        embed = discord.Embed(title=f"Activity Report ({duration})", color=BLANK_COLOR)
        embed.description = f"**Leaderboard**\n"
        embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        embeds.append(embed)
        for item in leaderboard_string.split("\n"):
            if len(embeds[-1].description.splitlines()) > 9:
                embed = discord.Embed(
                    title=f"Activity Report ({duration})", color=BLANK_COLOR
                )
                embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                embeds.append(embed)
                embeds[-1].description = f"**Leaderboard**\n"
            embeds[-1].description += f"{item}\n"

        actual_loas = []
        async for loa_item in self.bot.loas.db.find({"guild_id": ctx.guild.id}):
            starting_epoch = loa_item["_id"].split("_")[2]
            if int(starting_epoch) >= timestamp_pre and loa_item.get("accepted", True):
                loa_item["start_epoch"] = int(starting_epoch)
                actual_loas.append(loa_item)

        async def interaction_callback(interaction: discord.Interaction, _):
            # 🖱️ Interaction callback for activity report
            if interaction.user.id != ctx.author.id:
                return await generalised_interaction_check_failure(interaction.response)

            # 🛠️ Setup embed for activity notices
            def setup_embed() -> discord.Embed:
                embed = discord.Embed(title="Activity Notices", color=BLANK_COLOR)
                embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
                return embed

            embeds = []
            for item in actual_loas:
                if len(embeds) == 0:
                    embeds.append(setup_embed())

                if len(embeds[-1].fields) > 4:
                    embeds.append(setup_embed())

                find_shift_staff = all_staff.get(item["user_id"])

                if find_shift_staff:
                    embeds[-1].add_field(
                        name=f"{item['type']}",
                        value=(
                            f"> **Staff:** <@{item['user_id']}>\n"
                            f"> **Reason:** {item['reason']}\n"
                            f"> **Shift Time:** {td_format(datetime.timedelta(seconds=find_shift_staff[0]))} {self.bot.emoji_controller.get_emoji('success') if seconds > find_shift_staff[1] else self.bot.emoji_controller.get_emoji('xmark')}\n"
                            f"> **Started At:** <t:{int(item['start_epoch'])}>\n"
                            f"> **Ended At:** <t:{int(item['expiry'])}>"
                        ),
                        inline=False,
                    )
                else:
                    embeds[-1].add_field(
                        name=f"{item['type']}",
                        value=(
                            f"> **Staff:** <@{item['user_id']}>\n"
                            f"> **Reason:** {item['reason']}\n"
                            f"> **Shift Time:** {td_format(datetime.timedelta(seconds=0))} {self.bot.emoji_controller.get_emoji('success') if seconds > 0 else self.bot.emoji_controller.get_emoji('xmark')}\n"
                            f"> **Started At:** <t:{int(item['start_epoch'])}>\n"
                            f"> **Ended At:** <t:{int(item['expiry'])}>"
                        ),
                        inline=False,
                    )
            pages = [
                CustomPage(embeds=[embed], identifier=str(index + 1))
                for index, embed in enumerate(embeds)
            ]
            paginator = SelectPagination(self.bot, ctx.author.id, pages=pages)
            await interaction.response.send_message(
                embed=embeds[0], view=paginator, ephemeral=True
            )

        button = CustomExecutionButton(
            ctx.author.id,
            "View LOAs",
            style=discord.ButtonStyle.secondary,
            func=interaction_callback,
        )
        extra_view = discord.ui.View()
        if len(actual_loas) != 0:
            extra_view.add_item(button)

        view = SelectPagination(
            self.bot,
            ctx.author.id,
            [
                CustomPage(embeds=[embed], view=extra_view, identifier=str(index + 1))
                for index, embed in enumerate(embeds)
            ],
        )

        await ctx.send(
            embed=embeds[0],
            view=view.get_current_view() if len(embeds) > 1 else extra_view,
        )


# 🛠️ Cog setup
async def setup(bot):
    await bot.add_cog(ActivityMonitoring(bot))
