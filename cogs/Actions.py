import discord # 🟦 Discord API
from discord.ext import commands # 📦 Command framework
import asyncio # 🕒 Async operations
import datetime # 📅 Date/time
import pytz # 🌍 Timezones
from erm import is_management, is_staff, is_admin # 🛡️ Permissions
from utils.advanced import FakeMessage # 🎭 Fake msg simulation
from utils.constants import BLANK_COLOR, GREEN_COLOR # 🎨 UI colors
from menus import ManageActions, CounterButton, ViewVotersButton # 📑 UI components
from discord import app_commands # 🏷️ Slash commands
from utils.autocompletes import action_autocomplete # 🔍 Autocomplete
from utils.paginators import CustomPage, SelectPagination # 📏 Pagination
from utils.utils import get_prefix, interpret_content, interpret_embed, log_command_usage # 🛠️ Utility functions


class Actions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        # 🏗️ Initialize the Actions cog...
        self.bot: commands.Bot = bot # 🤖 Bot instance

    @commands.hybrid_group(
        name="actions", description="Manage your ERM Actions easily." # 📂 Group command
    )
    async def actions(self, ctx: commands.Context):
        # 📂 Base actions group command...
        pass # 🛑 Root group

    @actions.command(name="manage", description="Manage your ERM Actions easily.") # ⚙️ Manage subcmd
    @is_admin() # 🛡️ Admin only
    async def actions_manage(self, ctx: commands.Context):
        # 🛠️ Manage server-wide actions...
        await log_command_usage(self.bot, ctx.guild, ctx.author, f"Actions Manage") # 📝 Log
        actions = [i async for i in self.bot.db.actions.find({"Guild": ctx.guild.id})] # 🔍 Fetch actions

        embeds = [] # 📑 Embed list
        current_embed = discord.Embed(title="Actions", color=BLANK_COLOR).set_author( # 📄 Initial embed
            name=ctx.guild.name, icon_url=ctx.guild.icon # 🏠 Server icon
        )

        for item in actions: # 🔄 Iterate actions
            if len(current_embed.fields) >= 5: # 📏 Field limit
                embeds.append(current_embed) # 📥 Save current
                current_embed = discord.Embed( # 🆕 Start new
                    title="Actions (cont.)", color=BLANK_COLOR # 📄 Overflow title
                )

            current_embed.add_field(
                name=item["ActionName"], # 🏷️ Name
                value=(
                    f"> **Name:** {item['ActionName']}\n" # 📝 Name
                    f"> **ID:** `{item['ActionID']}`\n" # 🆔 ID
                    f"> **Triggered:** {item['Triggers']}" # 📈 Usage
                ),
                inline=False, # 📏 Wide
            )

        if len(current_embed.fields) == 0: # ❓ Empty check
            current_embed.add_field(
                name="No Actions", # 📭 None found
                value="> There are no actions in this server.", # 📝 Text
                inline=False, # 📏 Wide
            )

        embeds.append(current_embed) # 📥 Add final

        view = ManageActions(self.bot, ctx.author.id) # 🔘 Management UI
        if len(embeds) > 9: # 📏 Large list
            paginator = SelectPagination( # 📏 Create paginator
                self.bot, ctx.author.id, [CustomPage(
                    embeds=embeds[i], # 📄 Page embed
                    view=view, # 🔘 UI
                    identifier=i # 🆔 Index
                ) for i in range(len(embeds))], timeout=60 # ⌛ Timeout
            )
            await ctx.send(embeds=embeds[0].embeds, view=paginator.get_current_view()) # 📤 Send paginated
        else: # 📏 Small list
            await ctx.send(embeds=embeds, view=view) # 📤 Send directly
        timeout = await view.wait() # ⏳ Interaction
        if timeout: # ⌛ Timed out
            return # ↩️ Exit

    @actions.command(name="execute", description="Execute an ERM Action in your server") # 🚀 Execute subcmd
    @is_staff() # 🛡️ Staff only
    @app_commands.autocomplete(action=action_autocomplete) # 🔍 Autocomplete
    async def action_execute(self, ctx: commands.Context, *, action: str):
        # 🚀 Manually execute an action...
        verbose = False # 📢 Verbosity flag
        dnr = False # 🛡️ Do not run flag
        if "--verbose" in action: # 🔍 Check flag
            action = action.replace(" --verbose", "") # 🧹 Clean input
            verbose = True # ✅ Set verbose
        try:
            dnr = getattr(ctx, "dnr")  # prevent privilege bypassing! no black hats # 🛡️ Security check
        except Exception as _: # ❌ Error
            dnr = False # 🚫 Default false

        ctx.verbose = verbose # 📢 Attach flag

        actions = [
            i async for i in self.bot.actions.db.find({"Guild": ctx.guild.id}) # 🔍 Fetch guild actions
        ] or []
        action_obj = None
        for item in actions:
            if item["ActionName"] == action:
                action_obj = item
                break
        if not action_obj and not dnr:
            return await ctx.send(
                embed=discord.Embed(
                    title="Invalid Action Name",
                    description="The name you provided does not correspond with an action on this server. Run `/actions manage` for details.",
                    color=BLANK_COLOR,
                )
            )

        if action_obj.get("AccessRoles"):
            if (
                not any(
                    [discord.utils.get(ctx.guild.roles, id=i) in ctx.author.roles]
                    for i in action_obj.get("AccessRoles")
                )
                and not dnr
            ):
                return await ctx.send(
                    embed=discord.Embed(
                        title="Access Denied",
                        description="You do not hold the roles required to use this action. Contact your Server Administrator for details.",
                        color=BLANK_COLOR,
                    )
                )
        #   actions = [
        #     'Execute Custom Command',
        #     'Pause Reminder',
        #     'Force All Staff Off Duty',
        #     'Send ER:LC Command',
        #     'Send ER:LC Message',
        #     'Send ER:LC Hint',
        #     'Delay'
        # ]

        funcs = [
            self.execute_custom_command,
            self.pause_reminder,
            self.force_off_duty,
            self.send_erlc_command,
            self.send_erlc_message,
            self.send_erlc_hint,
            self.delay,
            self.add_role,
            self.remove_role,
            self.execute_erm_command
        ]

        if not dnr:
            msg = await ctx.send(
                embed=discord.Embed(
                    title=f"{self.bot.emoji_controller.get_emoji('success')} Running Action",
                    description=f"**(0/{len(action_obj['Integrations'])})** I am currently running your action!",
                    color=GREEN_COLOR,
                )
            )

        chosen_funcs = []
        for item in action_obj["Integrations"]:
            chosen_funcs.append(
                [funcs[item["IntegrationID"]], item["ExtraInformation"]]
            )

        returns = []
        if dnr:
            chosen_funcs = list(
                filter(
                    lambda x: x not in [self.add_role, self.remove_role], chosen_funcs
                )
            )

        for func, param in chosen_funcs:
            if param is None:
                returns.append(await func(self.bot, ctx.guild.id, ctx))
            else:
                returns.append(await func(self.bot, ctx.guild.id, ctx, param))
            if not dnr:
                await msg.edit(
                    embed=discord.Embed(
                        title=f"{self.bot.emoji_controller.get_emoji('success')} Running Action",
                        description=f"**({len(list(filter(lambda x: x == 0, returns)))}/{len(action_obj['Integrations'])})** I am currently running your action!{' `{}`'.format(returns) if verbose else ''}",
                        color=GREEN_COLOR,
                    )
                )

    @staticmethod
    async def add_role(bot: commands.Bot, guild_id: int, context, role_id: int):
        # ➕ Add role integration for actions...
        try:
            guild = await bot.fetch_guild(guild_id)
            role = guild.get_role(role_id)
        except discord.HTTPException:
            return 1

        if not role:
            return 1

        try:
            await context.author.add_roles(role)
        except discord.HTTPException:
            return 1

    @staticmethod
    asyn# ➖ Remove role integration for actions...
        c def remove_role(bot: commands.Bot, guild_id: int, context, role_id: int):
        try:
            guild = await bot.fetch_guild(guild_id)
            role = guild.get_role(role_id)
        except discord.HTTPException:
            return 1

        if not role:
            return 1

        try:
            await context.author.remove_roles(role)
        except discord.HTTPException:
            return 1

    @staticmethod
    async def execute_custom_command(
        # 📟 Execute custom command action...
        bot, guild_id: int, context, custom_command_name: str
    ):
        Data = await bot.custom_commands.find_by_id(guild_id)
        guild = context.guild
        if Data is None:
            return 1

        is_command = False
        selected = None
        if "commands" in Data.keys():
            if isinstance(Data["commands"], list):
                for cmd in Data["commands"]:
                    if cmd["name"].lower().replace(
                        " ", ""
                    ) == custom_command_name.lower().replace(" ", ""):
                        is_command = True
                        selected = cmd

        if not is_command:
            return 1

        channel = None
        if not channel:
            if selected.get("channel") is None:
                channel = context.channel
            else:
                channel = (
                    discord.utils.get(guild.text_channels, id=selected["channel"])
                    if discord.utils.get(guild.text_channels, id=selected["channel"])
                    is not None
                    else context.channel
                )
        embeds = []
        for embed in selected["message"]["embeds"]:
            embeds.append(
                await interpret_embed(bot, context, channel, embed, selected["id"])
            )

        view = discord.ui.View()
        for item in selected.get("buttons", []):
            if item["label"] == "0" and "row" in item:
                counter_button = CounterButton(row=item["row"])
                view_voters_button = ViewVotersButton(
                    row=item["row"], counter_button=counter_button
                )
                view.add_item(counter_button)
                view.add_item(view_voters_button)
            else:
                view.add_item(
                    discord.ui.Button(
                        label=item["label"],
                        url=item["url"],
                        row=item["row"],
                        style=discord.ButtonStyle.url,
                    )
                )

        if (
            selected["message"]["content"] in [None, ""]
            and len(selected["message"]["embeds"]) == 0
        ):
            return 1

        msg = await channel.send(
            await interpret_content(
                bot, context, channel, selected["message"]["content"], selected["id"]
            ),
            embeds=embeds,
            view=view,
            allowed_mentions=discord.AllowedMentions(
                everyone=True, users=True, roles=True, replied_user=True
            ),
        )

        # Fetch ICS entry
        doc = await bot.ics.find_by_id(selected["id"]) or {}
        if doc in [None, {}]:
            return 0  # This is still successful, just means it doesn't use ICS
        doc["associated_messages"] = (
            [(channel.id, msg.id)]
            if not doc.get("associated_messages")
            else doc["associated_messages"] + [(channel.id, msg.id)]
        )
        await bot.ics.update_by_id(doc)
        return 0
# ⏸️ Pause reminder action...
        
    @staticmethod
    async def pause_reminder(bot, guild_id: int, context, reminder_name: str):
        reminder_data = await bot.reminders.find_by_id(guild_id) or []

        for index, item in enumerate(reminder_data["reminders"]):
            if item["name"] == reminder_name:
                if item.get("paused") is True:
                    item["paused"] = False
                    reminder_data["reminders"][index] = item
                    await bot.reminders.upsert(reminder_data)
                    return 0
                else:
                    item["paused"] = True
                    reminder_data["reminders"][index] = item
                    await bot.reminders.upsert(reminder_data)
                    return 0

        return 1
# 🛑 Force staff off duty action...
        
    @staticmethod
    async def force_off_duty(bot, guild_id: int, context):
        docs = [
            i
            async for i in bot.shift_management.shifts.db.find(
                {"Guild": guild_id, "EndEpoch": 0}
            )
        ]
        for item in docs:
            id = item["_id"]
            await bot.shift_management.shifts.db.update_one(
                {"_id": id},
                {
                    "$set": {
                        "EndEpoch": int(datetime.datetime.now(tz=pytz.UTC).timestamp())
                    }
                },
            )
            bot.dispatch("shift_end", id)
            if context.verbose:
                await context.send(item)
        # 🎮 Send ER:LC command via API...
        return 0

    @staticmethod
    async def send_erlc_command(bot, guild_id: int, context, command: str):
        if command[0] != ":":
            command = ":" + command

        command_response = await bot.prc_api.run_command(guild_id, f"{command}")
        if command_response[0] == 200:
            return 0

        if command_response[0] != 429:
            return 1

        wait_time = command_response[1]["retry_after"]
        await asyncio.sleep(wait_time + 1)
        command_response = await bot.prc_api.run_command(guild_id, f"{command}")
        if command_response[0] == 200:
            return 0

        if command_response[0] != 429:
        # 💬 Send ER:LC message via API...
            return 1

    @staticmethod
    async def send_erlc_message(bot, guild_id: int, context, message: str):
        if message[:3] == ":m ":
            message = message[3:]
        elif message[:2] == "m ":
            message = message[2:]

        command_response = await bot.prc_api.run_command(guild_id, f":m {message}")
        if command_response[0] == 200:
            return 0

        if command_response[0] != 429:
            return 1

        wait_time = command_response[1]["retry_after"]
        await asyncio.sleep(wait_time + 1)
        command_response = await bot.prc_api.run_command(guild_id, f":m {message}")
        if command_response[0] == 200:
            return 0

        # ⚙️ Execute internal ERM command...
        if command_response[0] != 429:
            return 1
        
    @staticmethod
    async def execute_erm_command(bot, guild_id: int, context, command: str):
        guild: discord.Guild = bot.get_guild(guild_id) or await bot.fetch_guild(guild_id)
        message = FakeMessage(
            content=bot.user.mention + " " + command,
            author=context.author,
            channel=await context.author.create_dm() if context.author else guild.system_channel or guild.text_channels[0],
            state=bot._connection
        )
        message.guild = guild
        try:
            await bot.process_commands(message)
        # 💡 Send ER:LC hint via API...
        except:
            return 1
        return 0

    @staticmethod
    async def send_erlc_hint(bot, guild_id: int, context, hint: str):
        if hint[:3] == ":h ":
            hint = hint[3:]

        command_response = await bot.prc_api.run_command(guild_id, f":h {hint}")
        if command_response[0] == 200:
            return 0

        if command_response[0] != 429:
            return 1

        wait_time = command_response[1]["retry_after"]
        await asyncio.sleep(wait_time + 1)
        command_response = await bot.prc_api.run_command(guild_id, f":h {hint}")
        if command_response[0] == 200:
            return 0
 ⏳ Delay integration for actions...
        #
        if command_response[0] != 429:
            return 1

    @staticmethod
    async def delay(bot, guild_id, context, timer: int):
        ## FOR THIS EXAMPLE, WE DO NOT NEED BOT AND GUILD ID
        try:
    # 🔩 Register Actions cog...
            await asyncio.sleep(int(timer))
        except:
            return 1
        return 0


async def setup(bot: commands.Bot):
    await bot.add_cog(Actions(bot))
