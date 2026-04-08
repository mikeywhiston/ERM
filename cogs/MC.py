import asyncio
import datetime
import json
import re
import discord
import roblox
from discord.ext import commands
from utils.autocompletes import erlc_group_autocomplete, erlc_players_autocomplete
from roblox.thumbnails import AvatarThumbnailType 

import logging
from typing import List
from erm import admin_check, is_staff, is_management, management_predicate
from utils.paginators import CustomPage, SelectPagination
from menus import CustomModal, ReloadView, RefreshConfirmation, RiskyUsersMenu, CustomExecutionButton
import copy
from utils.constants import *
from utils.prc_api import (
    Player,
    ServerStatus,
    KillLog,
    JoinLeaveLog,
    CommandLog,
    ResponseFailure,
)
import utils.prc_api as prc_api
from utils.utils import get_discord_by_roblox, get_roblox_by_username, log_command_usage, secure_logging, staff_check
from discord import app_commands
import typing


class MC(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @staticmethod
    def is_mc_server_linked():
        async def predicate(ctx: commands.Context):
            guild_id = ctx.guild.id

            try:
                await ctx.bot.mc_api.get_server_status(guild_id)
            except prc_api.ResponseFailure as exc:
                error = prc_api.ServerLinkNotFound(platform="mc")
                try:
                    error.code = exc.json_data.get("code") or exc.status_code
                except json.JSONDecodeError:
                    pass
                raise error

            return True

        return commands.check(predicate)

    async def secure_logging(
        self,
        guild_id,
        author_id,
        interpret_type: typing.Literal["Message", "Hint", "Command"],
        command_string: str,
        attempted: bool = False,
    ):
        await secure_logging(
            self.bot, guild_id, author_id, interpret_type, command_string, attempted
        )

    @commands.hybrid_group(name="mc")
    async def mc(self, ctx: commands.Context):
        pass

    @mc.command(name="link", description="Link your Maple County server with ERM!")
    @is_management()
    async def mc_link(self, ctx: commands.Context, *, server_name: str):
        # get the linked roblox user
        roblox_id = 0
        oauth2_user = (
            await self.bot.oauth2_users.db.find_one({"discord_id": ctx.author.id}) or {}
        )
        if not oauth2_user.get("roblox_id"):
            # go to fallback
            roblox_user = await self.bot.bloxlink.find_roblox(ctx.author.id)
            if not roblox_user.get("robloxID"):
                return await ctx.send(
                    embed=discord.Embed(
                        title="Not Linked",
                        description="You are not linked to any ROBLOX account.",
                        color=BLANK_COLOR,
                    )
                )
            roblox_id = roblox_user["robloxID"]
        else:
            roblox_id = oauth2_user["roblox_id"]

        try:
            server_token = await self.bot.mc_api.authorize(
                roblox_id, server_name, ctx.guild.id
            )
        except prc_api.ResponseFailure:  # yes, this is correct.
            return await ctx.send(
                embed=discord.Embed(
                    title="Server Not Found",
                    description="We could not find a server you own under the server name provided. Make sure you are linked with ERM by running `/link` in any server.",
                    color=BLANK_COLOR,
                )
            )

        await ctx.send(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Server Linked",
                description=f"Your server has been linked with the name `{server_name}`.",
                color=GREEN_COLOR,
            )
        )

    @mc.command(
        name="info",
        description="Get information about the current players in your Maple County server.",
    )
    @is_mc_server_linked()
    async def mc_info(self, ctx: commands.Context):
        guild_id = ctx.guild.id

        async def operate_and_reload_serverinfo(
            msg: discord.Message | None, guild_id: str
        ):
            guild_id = int(guild_id)
            status: ServerStatus = await self.bot.mc_api.get_server_status(guild_id)
            players: list[Player] = await self.bot.mc_api.get_server_players(guild_id)
            client = roblox.Client()

            embed1 = discord.Embed(title=f"{status.name}", color=BLANK_COLOR)
            embed1.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
            embed1.add_field(
                name="Basic Info",
                value=(
                    f"> **Join Code:** [{status.join_key}](https://www.roblox.com/games/start?placeId=8416011646&launchData=psjoincode%3D{status.join_key}&deep_link_value=roblox%3A%2F%2FplaceId%3D8416011646)\n"
                    f"> **Current Players:** {status.current_players}/{status.max_players}\n"
                ),
                inline=False,
            )
            embed1.add_field(
                name="Server Ownership",
                value=(
                    f"> **Owner:** [{(await client.get_user(status.owner_id)).name}](https://roblox.com/users/{status.owner_id}/profile)\n"
                    f"> **Co-Owners:** {f', '.join([f'[{user.name}](https://roblox.com/users/{user.id}/profile)' for user in await client.get_users(status.co_owner_ids, expand=False)])}"
                ),
                inline=False,
            )

            embed1.add_field(
                name="Staff Statistics",
                value=(
                    f"> **Moderators:** {len(list(filter(lambda x: x.permission == 'Server Moderator', players)))}\n"
                    f"> **Administrators:** {len(list(filter(lambda x: x.permission == 'Server Administrator', players)))}\n"
                    f"> **Staff In-Game:** {len(list(filter(lambda x: x.permission != 'Normal', players)))}\n"
                    f"> **Staff Clocked In:** {await self.bot.shift_management.shifts.db.count_documents({'Guild': guild_id, 'EndEpoch': 0})}"
                ),
                inline=False,
            )

            if msg is None:
                view = ReloadView(
                    self.bot,
                    ctx.author.id,
                    operate_and_reload_serverinfo,
                    [None, guild_id],
                )
                msg = await ctx.send(embed=embed1, view=view)
                view.message = msg
                view.callback_args[0] = msg
            else:
                await msg.edit(embed=embed1)

        await operate_and_reload_serverinfo(None, guild_id)

    @mc.command(name="logs", description="See the Command Logs of your server.")
    @is_staff()
    @is_mc_server_linked()
    async def mc_logs(self, ctx: commands.Context):
        guild_id = ctx.guild.id

        async def operate_and_reload_commandlogs(msg, guild_id: str):
            guild_id = int(guild_id)
            # status: ServerStatus = await self.bot.prc_api.get_server_status(guild_id)
            command_logs: list[CommandLog] = await self.bot.mc_api.fetch_server_logs(
                guild_id
            )
            embed = discord.Embed(
                color=BLANK_COLOR, title="Command Logs", description=""
            )

            sorted_logs = sorted(
                command_logs, key=lambda log: log.timestamp, reverse=True
            )
            for log in sorted_logs:
                if len(embed.description) > 3800:
                    break
                embed.description += f"> [{log.username}](https://roblox.com/users/{log.user_id}/profile) ran the command `{log.command}` • <t:{int(log.timestamp)}:R>\n"

            if embed.description in ["", "\n"]:
                embed.description = "> No player logs found."

            embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

            if msg is None:
                view = ReloadView(
                    self.bot,
                    ctx.author.id,
                    operate_and_reload_commandlogs,
                    [None, guild_id],
                )
                msg = await ctx.send(embed=embed, view=view)
                view.message = msg
                view.callback_args[0] = msg
            else:
                await msg.edit(embed=embed)

        await operate_and_reload_commandlogs(None, guild_id)

    @mc.command(name="bans", description="Filter the bans of your server.")
    @is_staff()
    @is_mc_server_linked()
    async def mc_bans(
        self,
        ctx: commands.Context,
        username: typing.Optional[str],
        user_id: typing.Optional[int],
    ):
        guild_id = ctx.guild.id
        # status: ServerStatus = await self.bot.prc_api.get_server_status(guild_id)
        try:
            bans: list[prc_api.BanItem] = await self.bot.mc_api.fetch_bans(guild_id)
        except prc_api.ResponseFailure:
            return await ctx.send(
                embed=discord.Embed(
                    title="MC API Error",
                    description="There were no bans, or your API key is incorrect.",
                    color=BLANK_COLOR,
                )
            )
        embed = discord.Embed(color=BLANK_COLOR, title="Bans", description="")
        status = username or user_id

        if not username and user_id:
            username = "[PLACEHOLDER]"

        if not user_id and username:
            user_id = "99999"
        old_embed = copy.copy(embed)
        embeds = [embed]
        for log in bans:
            if str(username or "") in str(log.username).lower() or str(
                user_id or ""
            ) in str(log.user_id):
                embed = embeds[-1]
                if len(embed.description) > 3800:
                    new = copy.copy(old_embed)
                    embeds.append(new)
                embeds[
                    -1
                ].description += f"> [{log.username}:{log.user_id}](https://roblox.com/users/{log.user_id}/profile)\n"

        if embeds[0].description in ["", "\n"]:
            embeds[0].description = (
                "> This ban was not found."
                if status
                else "> Bans were not found in your server."
            )

        embeds[0].set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)

        if len(embeds) > 1:
            pages = [
                CustomPage(embeds=[embeds[i]], identifier=str(i + 1))
                for i in range(0, len(embeds) - 1)
            ]
            paginator = SelectPagination(self.bot, ctx.author.id, pages)
            await ctx.send(embed=embeds[0], view=paginator.get_current_view())
            return
        else:
            await ctx.send(embed=embed)

    @mc.command(name="players", description="See all players in the server.")
    @is_mc_server_linked()
    async def mc_players(
        self, ctx: commands.Context, filter: typing.Optional[str] = None
    ):
        guild_id = int(ctx.guild.id)
        players: list[Player] = await self.bot.mc_api.get_server_players(guild_id)
        embed2 = discord.Embed(
            title=f"Server Players [{len(players)}]", color=BLANK_COLOR, description=""
        )
        actual_players = []
        key_maps = {}
        staff = []
        for item in players:
            if item.permission == "Normal":
                actual_players.append(item)
            else:
                staff.append(item)

        if filter not in [None, ""]:
            actual_players_copy = []
            for item in actual_players:
                if item.username.lower().startswith(filter.lower()):
                    actual_players_copy.append(item)
            actual_players = actual_players_copy
            staff_copy = []
            for item in staff:
                if item.username.lower().startswith(filter.lower()):
                    staff_copy.append(item)
            staff = staff_copy

        embed2.description += f"**Server Staff [{len(staff)}]**\n" + (
            ", ".join(
                [
                    f"[{plr.username}](https://roblox.com/users/{plr.id}/profile)"
                    for plr in staff
                ]
            )
            or "> No players in this category."
        )

        embed2.description += f"\n\n**Online Players [{len(actual_players)}]**\n" + (
            ", ".join(
                [
                    f"[{plr.username}](https://roblox.com/users/{plr.id}/profile)"
                    for plr in actual_players
                ]
            )
            or "> No players in this category."
        )

        embed2.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon)
        if len(embed2.description) > 3999:
            embed2.description = ""
            embed2.description += f"**Server Staff [{len(staff)}]**\n" + ", ".join(
                [f"{plr.username}" for plr in staff]
            )

            embed2.description += (
                f"\n\n**Online Players [{len(actual_players)}]**\n"
                + ", ".join([f"{plr.username}" for plr in actual_players])
            )

        await ctx.send(embed=embed2)

async def setup(bot):
    await bot.add_cog(MC(bot))