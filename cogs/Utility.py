import datetime
import logging
import aiohttp
import os
from decouple import config

import discord
from discord import app_commands
from discord.app_commands import AppCommandGroup
from discord.ext import commands
import pytz

from menus import LinkView, CustomSelectMenu, MultiPaginatorMenu, APIKeyConfirmation
from utils.constants import BLANK_COLOR, GREEN_COLOR
from utils.timestamp import td_format
from utils.utils import invis_embed, failure_embed, require_settings, time_converter
from erm import is_staff, is_management


class Utility(commands.Cog):
    # ⚙️ Cog initialization
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_group(
        name="import",
        description="Internal Use Command - import data from the recent outage.",
        extras={"category": "Utility"},
    )
    @is_staff()
    # 📥 Import command group
    async def import_group(self, ctx: commands.Context):
        pass

    @import_group.command(
        name="punishments",
        description="Import punishments from the outage.",
        extras={"category": "Utility"},
    )
    @commands.cooldown(1, 300, commands.BucketType.guild)
    @is_management()
    # 🔨 Import punishments
    async def import_punishments(self, ctx: commands.Context, channel: discord.TextChannel=None, time_frame: str=None):
        if channel is None:
            channel = ctx.channel

        after = None
        if time_frame is None:
            after = datetime.datetime.fromtimestamp(1754516493)
        else:
            after = datetime.datetime.fromtimestamp(datetime.datetime.now(tz=pytz.UTC).timestamp() - time_converter(time_frame))

        msg = await ctx.send(
            embed=discord.Embed(
                title="Punishments Import",
                description="> **Channel:** {}\n> **After:** <t:{}:R>\n> **Imported:** 0".format(channel.mention, int(after.timestamp())),
                color=BLANK_COLOR,
            ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        )
        success = 0
        async for message in channel.history(limit=None, after=after):
            embeds = message.embeds
            if len(embeds) == 0:
                continue
            if "ERM" not in message.author.name:
                continue

            embed = embeds[0]
            embed_title = embed.title.lower() if embed.title else ""
            if embed_title != "punishment issued":
                continue

            fields = embed.fields
            moderator_field = fields[0]
            violator_field = fields[1]

            punishment = {}
            punishment["Moderator"] = ""
            punishment["ModeratorID"] = int(moderator_field.value.split("<@")[1].split(">")[0])
            punishment["Snowflake"] = int(moderator_field.value.split("`")[1].split("`")[0])
            punishment["Reason"] = moderator_field.value.split("Reason:** ")[1].split("\n")[0]
            punishment["Epoch"] = int(moderator_field.value.split("<t:")[1].split(">")[0])
            punishment["Username"] = violator_field.value.split("Username:** ")[1].split("\n")[0]
            punishment["UserID"] = int(violator_field.value.split("`")[1].split("`")[0])
            punishment["Guild"] = ctx.guild.id
            punishment["Type"] = violator_field.value.split("Type:** ")[1].split("\n")[0]

            if punishment["Type"] == "Temporary Ban":
                try:
                    punishment["UntilEpoch"] = int(violator_field.value.split("Until:** <t:")[1].split(">")[0])
                except:
                    punishment["UntilEpoch"] = punishment["Epoch"]

            if await self.bot.punishments.db.find_one({"Snowflake": punishment["Snowflake"]}):
                continue

            await self.bot.punishments.db.insert_one(punishment)
            success += 1
            logging.info(f"Imported punishment: {punishment}")
            if success % 100 == 0:
                await msg.edit(
                    embed=discord.Embed(
                        title="Punishments Import",
                        description="> **Channel:** {}\n> **After:** <t:{}:R>\n> **Imported:** `{}`".format(channel.mention, 1754516493, success),
                        color=BLANK_COLOR,
                    ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                )

        await msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Import Complete",
                description="Successfully imported **{}** punishments.".format(success),
                color=GREEN_COLOR,
            )
        )

    @import_group.command(
        name="shifts",
        description="Import shifts from the outage.",
        extras={"category": "Utility"},
    # 🕒 Import shifts
    )
    @commands.cooldown(1, 300, commands.BucketType.guild)
    @is_management()
    async def import_shifts(self, ctx: commands.Context, channel: discord.TextChannel=None, time_frame: str=None):
        if channel is None:
            channel = ctx.channel

        after = None
        if time_frame is None:
            after = datetime.datetime.fromtimestamp(1754516493)
        else:
            after = datetime.datetime.fromtimestamp(datetime.datetime.now(tz=pytz.UTC).timestamp() - time_converter(time_frame))
        
        msg = await ctx.send(
            embed=discord.Embed(
                title="Shifts Import",
                description="> **Channel:** {}\n> **After:** <t:{}:R>\n> **Imported:** 0".format(channel.mention, int(after.timestamp())),
                color=BLANK_COLOR,
            ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        )

        success = 0
        async for message in channel.history(limit=None, after=after):
            embeds = message.embeds
            if len(embeds) == 0:
                continue
            if "ERM" not in message.author.name:
                continue

            embed = embeds[0]
            embed_title = embed.title.lower() if embed.title else ""
            if embed_title != "shift ended":
                continue

            fields = embed.fields
            shift_field = fields[0]
            other_field = fields[1]

            shift = {}
            shift["UserID"] = int(shift_field.value.split("<@")[1].split(">")[0])
            shift["Username"] = other_field.value.split("Nickname:** ")[1].split("\n")[0]
            shift["Nickname"] = shift["Username"]
            shift["StartEpoch"] = int(other_field.value.split("<t:")[1].split(">")[0])
            shift["Guild"] = ctx.guild.id
            shift["AddedTime"] = 0
            shift["RemovedTime"] = 0
            shift["Type"] = shift_field.value.split("Type:** ")[1].split("\n")[0]
            shift["EndEpoch"] = int(other_field.value.split("<t:")[2].split(">")[0])
            shift["Breaks"] = []

            await self.bot.shift_management.shifts.db.insert_one(shift)
            success += 1

            logging.info(f"Imported shift: {shift}")
            if success % 100 == 0:
                await msg.edit(
                    embed=discord.Embed(
                        title="Shifts Import",
                        description="> **Channel:** {}\n> **After:** <t:{}:R>\n> **Imported:** `{}`".format(channel.mention, 1754516493, success),
                        color=BLANK_COLOR,
                    ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                )

        await msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Import Complete",
                description="Successfully imported **{}** shifts.".format(success),
                color=GREEN_COLOR,
            )
        )

    @import_group.command(
        name="loas",
        description="Import LOAs from the outage.",
        extras={"category": "Utility"},
    )
    @commands.cooldown(1, 300, commands.BucketType.guild)
    # 📅 Import LOAs
    @is_management()
    async def import_loas(self, ctx: commands.Context, channel: discord.TextChannel=None, time_frame: str=None):
        if channel is None:
            channel = ctx.channel

        after = None
        if time_frame is None:
            after = datetime.datetime.fromtimestamp(1754516493)
        else:
            after = datetime.datetime.fromtimestamp(datetime.datetime.now(tz=pytz.UTC).timestamp() - time_converter(time_frame))
        
        msg = await ctx.send(
            embed=discord.Embed(
                title="LOAs Import",
                description="> **Channel:** {}\n> **After:** <t:{}:R>\n> **Imported:** 0".format(channel.mention, int(after.timestamp())),
                color=BLANK_COLOR,
            ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
        )

        success = 0
        async for message in channel.history(limit=None, after=after):
            embeds = message.embeds
            if len(embeds) == 0:
                continue
            if "ERM" not in message.author.name:
                continue

            embed = embeds[0]
            embed_title = embed.title.lower() if embed.title else ""
            if "loa accepted" not in embed_title and "loa request" not in embed_title and "loa denied" not in embed_title:
                continue

            fields = embed.fields
            staff_field = fields[0]
            request_field = fields[1]

            loa = {}
            loa["message_id"] = message.id
            loa["user_id"] = int(staff_field.value.split("<@")[1].split(">")[0])
            loa["guild_id"] = ctx.guild.id
            loa["type"] = request_field.value.split("Type:** ")[1].split("\n")[0]
            loa["reason"] = request_field.value.split("Reason:** ")[1].split("\n")[0]
            loa["expiry"] = int(request_field.value.split("Ends At:** <t:")[1].split(">")[0])
            loa["expired"] = True if loa["expiry"] < int(datetime.datetime.now(tz=pytz.UTC).timestamp()) else False
            loa["voided"] = False
            loa["denied"] = True if "denied" in embed_title else False
            loa["accepted"] = True if "accepted" in embed_title else False
            loa["_id"] = "{}_{}_{}_{}".format(loa["user_id"], loa["guild_id"], request_field.value.split("Starts At:** <t:")[1].split(">")[0], loa["expiry"])

            if await self.bot.loas.db.find_one({"_id": loa["_id"]}):
                await self.bot.loas.db.update_one({"_id": loa["_id"]}, {"$set": {"voided": loa["voided"], "denied": loa["denied"], "accepted": loa["accepted"], "expired": loa["expired"]}})

            await self.bot.loas.db.insert_one(loa)
            success += 1

            logging.info(f"Imported LOA: {loa}")
            if success % 100 == 0:
                await msg.edit(
                    embed=discord.Embed(
                        title="LOAs Import",
                        description="> **Channel:** {}\n> **After:** <t:{}:R>\n> **Imported:** {}".format(channel.mention, int(after.timestamp()), success),
                        color=BLANK_COLOR,
                    ).set_author(name=ctx.guild.name, icon_url=ctx.guild.icon.url if ctx.guild.icon else None)
                )
        await msg.edit(
            embed=discord.Embed(
                title=f"{self.bot.emoji_controller.get_emoji('success')} Import Complete",
                description="Successfully imported **{}** LOAs.".format(success),
                color=GREEN_COLOR,
            )
        )


    @commands.hybrid_command(
        name="staff_sync",
        description="Internal Use Command, used for connection staff privileged individuals to their Roblox counterparts.",
        extras={"category": "Utility"},
        hidden=True,
        with_app_command=False,
    )
    @commands.has_role(988055417907200010)
    # 🔄 Sync staff accounts
    async def staff_sync(self, ctx: commands.Context, discord_id: int, roblox_id: int):
        from bson import ObjectId
        from datamodels.StaffConnections import StaffConnection

        await self.bot.staff_connections.insert_connection(
            StaffConnection(
                roblox_id=roblox_id, discord_id=discord_id, document_id=ObjectId()
            )
        )
        roblox_user = await self.bot.roblox.get_user(roblox_id)
        await ctx.send(
            embed=discord.Embed(
                title="Staff Sync",
                description=f"Successfully synced <@{discord_id}> to {roblox_user.name}",
                color=BLANK_COLOR,
            )
        )

    @commands.hybrid_command(
        name="ping",
        description="Shows information of the bot, such as uptime and latency",
        extras={"category": "Utility"},
    # 🏓 Ping command
    )
    async def ping(self, ctx):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(
            title="Bot Status",
            color=BLANK_COLOR,
        )

        if ctx.guild is not None:
            embed.set_author(
                name=ctx.guild.name,
                icon_url=ctx.guild.icon,
            )
        else:
            embed.set_author(
                name=ctx.author.name,
                icon_url=ctx.author.display_avatar.url,
            )

        data = await self.bot.db.command("ping")

        status: str | None = None

        if list(data.keys())[0] == "ok":
            status = "Connected"
        else:
            status = "Not Connected"

        embed.add_field(
            name="Information",
            value=(
                f"> **Latency:** `{latency}ms`\n"
                f"> **Uptime:** <t:{int(self.bot.start_time)}:R>\n"
                f"> **Database Connection:** {status}\n"
                f"> **Shards:** `{self.bot.shard_count-1 if isinstance(self.bot, commands.AutoShardedBot) else 0}`\n"
            ),
            inline=False,
        )

        embed.set_footer(
            text=f"Shard {ctx.guild.shard_id if ctx.guild and isinstance(self.bot, commands.AutoShardedBot) else 0}/{self.bot.shard_count-1 if isinstance(self.bot, commands.AutoShardedBot) else 0}"
        )
        embed.timestamp = datetime.datetime.utcnow()
        embed.set_thumbnail(url=ctx.guild.icon)
        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="modpanel",
        aliases=["panel"],
        description="Get the link to this server's mod panel.",
        extras={"category": "Website"},
    )
    @is_staff()
    # 🛡️ Link to mod panel
    @require_settings()
    async def mod_panel(self, ctx: commands.Context):
        guild_icon = ctx.guild.icon.url if ctx.guild.icon else None

        await ctx.send(
            embed=discord.Embed(
                color=BLANK_COLOR,
                description="Visit your server's Moderation Panel using the button below.",
            ).set_author(name=ctx.guild.name, icon_url=guild_icon),
            view=LinkView(
                label="Mod Panel", url=f"https://ermbot.xyz/{ctx.guild.id}/panel"
            ),
        )

    @commands.hybrid_command(
        name="dashboard",
        aliases=["dash", "applications"],
        description="Get the link to manage your server through the dashboard.",
        extras={"category": "Website"},
    # 📊 Link to dashboard
    )
    @is_management()
    async def dashboard(self, ctx: commands.Context):
        guild_icon = ctx.guild.icon.url if ctx.guild.icon else None

        await ctx.send(
            embed=discord.Embed(
                color=BLANK_COLOR,
                description="Visit your server's Dashboard using the button below.",
            ).set_author(name=ctx.guild.name, icon_url=guild_icon),
            view=LinkView(
                label="Dashboard", url=f"https://ermbot.xyz/{ctx.guild.id}/dashboard"
            ),
        )

    @commands.hybrid_command(
        name="support",
        aliases=["support-server"],
        description="Information about the ERM Support Server",
    # 🆘 Link to support server
        extras={"category": "Utility"},
    )
    async def support_server(self, ctx):
        # using an embed
        # [**Support Server**](https://discord.gg/5pMmJEYazQ)

        await ctx.reply(
            embed=discord.Embed(
                title="ERM Support",
                description="You can join the ERM Systems Discord server using the button below.",
                color=BLANK_COLOR,
            ),
            view=LinkView(label="Support Server", url="https://discord.gg/FAC629TzBy"),
        )

    @commands.hybrid_command(
        name="about",
        aliases=["info"],
        description="Information about ERM",
        extras={"category": "Utility"},
    )
    async def about(self, ctx):
        # using an embed
        # [**Support Server**](https://discord.gg/5pMmJEYazQ)
        embed = discord.Embed(
            title="About ERM",
            color=BLANK_COLOR,
            description="ERM is the all-in-one approach to game moderation logging, shift logging and more.",
        )

        embed.add_field(
            name=f"Bot Information",
            value=(
                "> **Website:** [View Website](https://ermbot.xyz)\n"
                "> **Support:** [Join Server](https://discord.gg/FAC629TzBy)\n"
                f"> **Invite:** [Invite Bot](https://discord.com/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands)\n"
                "> **Documentation:** [View Documentation](https://docs.ermbot.xyz)\n"
                "> **Desktop:** [Download ERM Desktop](https://ermbot.xyz/download)"
            ),
            inline=False,
        )
        embed.set_author(
            name=self.bot.user.name,
            icon_url=self.bot.user.display_avatar.url,
        )
        await ctx.reply(embed=embed)

    @commands.hybrid_group(name="api")
    async def api(self, ctx):
        pass

    @commands.guild_only()
    @api.command(
        name="generate",
        description="Generate an API key for your server",
        extras={"category": "Utility"},
    )
    @is_management()
    @require_settings()
    async def api_generate(self, ctx: commands.Context):
        view = APIKeyConfirmation(ctx.author.id)
        msg = await ctx.send(
            embed=discord.Embed(
                title="Generate API Key",
                description="Are you sure you want to generate an API key? This will invalidate any existing keys.",
                color=BLANK_COLOR,
            ),
            view=view,
            ephemeral=isinstance(ctx.interaction, discord.Interaction),
        )

        await view.wait()
        if not view.value:
            return

        api_url = f"{config('OPENERM_API_URL')}/api/v1/auth/token"
        auth_token = config("OPENERM_AUTH_TOKEN")
        full_url = f"{api_url}?guild_id={ctx.guild.id}&auth_token={auth_token}"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(full_url) as response:

                    response_text = await response.text()

                    if response.status == 200:
                        api_key = response_text

                        if isinstance(ctx.interaction, discord.Interaction):
                            await ctx.send(
                                embed=discord.Embed(
                                    title="API Key Generated",
                                    description="Here is your API key. Please save it somewhere safe - we won't show it again.",
                                    color=BLANK_COLOR,
                                ).add_field(name="API Key", value=f"```{api_key}```"),
                                ephemeral=True,
                            )
                        else:
                            await ctx.author.send(
                                embed=discord.Embed(
                                    title="API Key Generated",
                                    description="Here is your API key. Please save it somewhere safe - we won't show it again.",
                                    color=BLANK_COLOR,
                                ).add_field(name="API Key", value=f"```{api_key}```")
                            )
                            await msg.edit(
                                embed=discord.Embed(
                                    title=f"{self.bot.emoji_controller.get_emoji('success')} API Key Generated",
                                    description="I have successfully generated an API key and sent it to your DMs!",
                                    color=GREEN_COLOR,
                                ),
                                view=None,
                            )
                    else:
                        error_msg = f"API returned non-200 status: {response.status}"
                        logging.error(error_msg)
                        await ctx.send(
                            embed=discord.Embed(
                                title="Error",
                                description="Failed to generate API key. Please try again later.",
                                color=BLANK_COLOR,
                            ),
                            ephemeral=isinstance(ctx.interaction, discord.Interaction),
                        )
            except aiohttp.ClientError as e:
                error_msg = f"API request failed: {str(e)}"
                logging.error(error_msg)
                await ctx.send(
                    embed=discord.Embed(
                        title="Error",
                        description="Failed to connect to API. Please try again later.",
                        color=BLANK_COLOR,
                    ),
                    ephemeral=isinstance(ctx.interaction, discord.Interaction),
                )


async def setup(bot):
    await bot.add_cog(Utility(bot))
