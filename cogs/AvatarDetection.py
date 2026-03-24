import asyncio
import logging
import time

import aiohttp
import discord
import roblox
from decouple import config
from discord.ext import commands

from utils.constants import BLANK_COLOR, GREEN_COLOR
from utils.utils import fetch_get_channel


class AvatarDetection(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


async def run_avatar_check(bot, settings, guild_id: int, log) -> None:
    avatar_cfg = settings.get("ERLC", {}).get("avatar_check", {})

    if not avatar_cfg.get("enabled"):
        return
    if not avatar_cfg.get("channel"):
        return

    api_url = config("AVATAR_CHECK_URL", default="").rstrip("/")
    if not api_url:
        logging.error("[avatar-check] AVATAR_CHECK_URL not set in .env")
        return

    # Skip anyone with a PRC staff permission above Normal
    try:
        server_players = await bot.prc_api.get_server_players(guild_id)
        for player in server_players:
            if player.username.lower() == log.username.lower():
                if player.permission != "Normal" and player.permission is not None:
                    logging.info(
                        f"[avatar-check] Skipping {log.username} — "
                        f"staff permission: {player.permission}"
                    )
                    return
                break
    except Exception as e:
        logging.warning(
            f"[avatar-check] Could not fetch server players for guild {guild_id}, "
            f"skipping {log.username}: {e}"
        )
        return

    # Fetch full-body avatar thumbnail
    try:
        roblox_user = await bot.roblox.get_user(int(log.user_id))
        thumbnails = await bot.roblox.thumbnails.get_user_avatar_thumbnails(
            [roblox_user],
            type=roblox.thumbnails.AvatarThumbnailType.full_body,
        )
        avatar_url = thumbnails[0].image_url if thumbnails else None
    except Exception as e:
        logging.error(f"[avatar-check] Could not fetch avatar for {log.username}: {e}")
        return

    if not avatar_url:
        logging.warning(f"[avatar-check] No avatar URL for {log.username}, skipping.")
        return

    payload = {
        "guild_id": str(guild_id),
        "user_id": str(log.user_id),
        "username": log.username,
        "avatar_url": avatar_url,
        "prompt": avatar_cfg.get("prompt", ""),
        "allowed_prompt": avatar_cfg.get("allowed_prompt", ""),
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{api_url}/api/avatar-check",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=20),
            ) as resp:
                if resp.status == 404:
                    logging.error("[avatar-check] API 404 — check AVATAR_CHECK_URL in .env")
                    return
                if resp.status != 200:
                    logging.error(
                        f"[avatar-check] API returned {resp.status} for {log.username}"
                    )
                    return
                data = await resp.json()
    except asyncio.TimeoutError:
        logging.warning(
            f"[avatar-check] Timed out for {log.username} in guild {guild_id}"
        )
        return
    except Exception as e:
        logging.error(f"[avatar-check] Request error for {log.username}: {e}")
        return

    # Verify the response is for the right player to prevent cross-server mistakes
    if (
        str(data.get("guild_id")) != str(guild_id)
        or str(data.get("user_id")) != str(log.user_id)
        or data.get("username") != log.username
    ):
        logging.error(
            f"[avatar-check] Identity mismatch for guild {guild_id} — "
            f"expected {log.username}, got {data.get('username')}. Skipping."
        )
        return

    passed = data.get("pass", True)
    reason = data.get("reason", "Unrealistic avatar detected")
    auto_kick = avatar_cfg.get("auto_kick", True)
    action = "none" if passed else ("kicked" if auto_kick else "warned")

    # Save log to MongoDB so the website can display it
    try:
        await bot.avatar_check_logs.db.insert_one({
            "guild_id": guild_id,
            "username": log.username,
            "user_id": int(log.user_id),
            "passed": passed,
            "reason": reason,
            "action": action,
            "avatar_url": avatar_url,
            "timestamp": int(time.time()),
        })
    except Exception as e:
        logging.error(f"[avatar-check] Failed to save log for {log.username}: {e}")

    if passed:
        logging.info(f"[avatar-check] {log.username} passed in guild {guild_id}")
        return

    logging.info(
        f"[avatar-check] {log.username} FAILED in guild {guild_id}: {reason}"
    )

    # PM message differs depending on whether they will be kicked or just warned
    if auto_kick:
        pm_message = avatar_cfg.get(
            "pm_message",
            "Your avatar does not meet this server's standards. Please change it and rejoin.",
        )
    else:
        pm_message = avatar_cfg.get(
            "pm_message",
            "Your avatar does not meet this server's standards. Please change it or you may be removed.",
        )

    try:
        await bot.prc_api.run_command(
            guild_id, f":pm {log.username} {pm_message}"
        )
    except Exception as e:
        logging.warning(f"[avatar-check] PM failed for {log.username}: {e}")

    if auto_kick:
        try:
            await asyncio.sleep(1.5)
            await bot.prc_api.run_command(guild_id, f":kick {log.username}")
            logging.info(
                f"[avatar-check] Kicked {log.username} from guild {guild_id}"
            )
        except Exception as e:
            logging.error(f"[avatar-check] Kick failed for {log.username}: {e}")
    else:
        logging.info(
            f"[avatar-check] Warning sent to {log.username} in guild {guild_id} — auto-kick disabled"
        )

    # Send alert embed to the configured Discord channel
    channel_id = avatar_cfg.get("channel")
    if not channel_id:
        return

    try:
        guild = bot.get_guild(guild_id) or await bot.fetch_guild(guild_id)
        channel = await fetch_get_channel(guild, channel_id)
        if not channel:
            return

        mentions = " ".join(
            f"<@&{role_id}>"
            for role_id in avatar_cfg.get("mentioned_roles", [])
        )

        status_label = "Kicked" if auto_kick else "Warned — this server has auto-kick disabled so the player could not be kicked"

        embed = (
            discord.Embed(
                title="Avatar Detection",
                description=(
                    "A player has been flagged for having an avatar that does not meet this server's standards."
                ),
                color=BLANK_COLOR,
            )
            .add_field(
                name="Player",
                value=(
                    f"> **Username:** [{log.username}]"
                    f"(https://roblox.com/users/{log.user_id}/profile)\n"
                    f"> **User ID:** `{log.user_id}`"
                ),
                inline=True,
            )
            .add_field(
                name="Action Taken",
                value=(
                    f"> **Status:** {status_label}\n"
                    f"> **Reason:** {reason}"
                ),
                inline=True,
            )
            .set_thumbnail(url=avatar_url)
            .set_author(
                name=guild.name,
                icon_url=guild.icon.url if guild.icon else "",
            )
            .set_footer(text="Avatar Detection • Automatically actioned")
        )

        from menus import AvatarDetectionView
        view = AvatarDetectionView(bot, log.username, guild_id)

        await channel.send(
            content=mentions or None,
            embed=embed,
            view=view,
            allowed_mentions=discord.AllowedMentions.all(),
        )
    except Exception as e:
        logging.error(
            f"[avatar-check] Failed to send alert for {log.username}: {e}"
        )


async def setup(bot):
    await bot.add_cog(AvatarDetection(bot))
