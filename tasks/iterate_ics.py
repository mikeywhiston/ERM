import discord # 📦 Import discord
from decouple import config # ⚙️ Import config
from discord.ext import commands, tasks # 🚀 Import commands, tasks

from utils import prc_api # 🔌 Import prc_api
from utils.prc_api import ServerStatus, Player # 👤 Import ServerStatus, Player
from utils.utils import interpret_content, interpret_embed # 🛠️ Import formatters


@tasks.loop(minutes=15, reconnect=True) # ⏰ Run every 15 mins
async def iterate_ics(bot): # 📦 Updating Integration Command Storage...
    # This will aim to constantly update the Integration Command Storage
    # and the relevant storage data.

    async for item in bot.ics.db.find({} if bot.environment in ["PRODUCTION", "ALPHA", "DEVELOPMENT"] else {"guild": config("CUSTOM_GUILD_ID")}): # 🔍 Fetch ICS items
        guild = bot.get_guild(item["guild"]) # 🏰 Get guild object

        if not guild: # 🏢 Fetch if not in memory
            try:
                guild = await bot.fetch_guild(item["guild"])
            except discord.HTTPException: # 🔴 Skip if fetch fails
                continue

        selected = None # 🎯 Target command
        custom_command_data = await bot.custom_commands.find_by_id(item["guild"]) or {} # ⚙️ Get custom cmds
        for command in custom_command_data.get("commands", []): # 🔍 Find matching command
            if command["id"] == item["_id"]:
                selected = command

        if not selected: # ❓ Skip if command not found
            continue

        try:
            status: ServerStatus = await bot.prc_api.get_server_status(guild.id) # 🏥 Get server status
        except prc_api.ResponseFailure: # 🔴 Handle API failure
            status = None

        if not isinstance(status, ServerStatus): # 🚫 Skip if invalid key/status
            continue  # Invalid key

        try:
            queue: int = await bot.prc_api.get_server_queue(guild.id, minimal=True) # 🚶 Get queue count
            players: list[Player] = await bot.prc_api.get_server_players(guild.id) # 👥 Get player list
        except prc_api.ResponseFailure: # ⚠️ Skip if player fetch fails
            continue  # fuck knows why

        mods: int = len( # 🛡️ Count moderators
            list(filter(lambda x: x.permission == "Server Moderator", players))
        )
        admins: int = len( # 👑 Count admins
            list(filter(lambda x: x.permission == "Server Administrator", players))
        )
        total_staff: int = len( # 💼 Count all staff
            list(filter(lambda x: x.permission != "Normal", players))
        )
        onduty: int = len( # 👮 Count on-duty staff
            [
                i
                async for i in bot.shift_management.shifts.db.find(
                    {"Guild": guild.id, "EndEpoch": 0}
                )
            ]
        )

        new_data = { # 📊 Compile new stats
            "join_code": status.join_key,
            "players": status.current_players,
            "max_players": status.max_players,
            "queue": queue,
            "staff": total_staff,
            "admins": admins,
            "mods": mods,
            "onduty": onduty,
        }
        # print(json.dumps(new_data, indent=4))

        if new_data != item["data"]: # 🔄 Check for data changes
            # Updated data
            for arr in item["associated_messages"]: # 📧 Update linked messages
                channel, message_id = arr[0], arr[1]
                
                channel = guild.get_channel(channel) # 📺 Get channel
                message = await channel.fetch_message(message_id) # 📩 Get message
                if channel and not message: # 🕵️ Re-fetch message if needed
                    try:
                        message = await channel.fetch_message(message_id)
                    except discord.NotFound: # ❓ Skip if deleted
                        continue
                    except discord.HTTPException: # 🛡️ Handle fetching errors
                        continue

                if not message or not channel: # 🚫 Skip if components missing
                    continue

                await message.edit( # 📝 Update Discord message
                    content=await interpret_content(
                        bot,
                        await bot.get_context(message),
                        channel,
                        selected["message"]["content"],
                        item["_id"],
                    ),
                    embeds=(
                        [
                            (
                                await interpret_embed(
                                    bot,
                                    await bot.get_context(message),
                                    channel,
                                    embed,
                                    item["_id"],
                                )
                            )
                            for embed in selected["message"]["embeds"]
                        ]
                        if selected["message"]["embeds"] is not None
                        else []
                    ),
                )
