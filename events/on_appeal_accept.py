import discord
import logging
from discord.ext import commands

from utils.constants import GREEN_COLOR


class OnAppealAccept(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_appeal_accept(
        self,
        guild: discord.Guild,
        interaction: discord.Interaction,
        appellant_id: int,
        roblox_username: str,
        roblox_id: int,
        embed: discord.Embed,
    ):
        # Attempt unban via PRC API
        unban_success = False
        unban_attempted = False

        try:
            await self.bot.prc_api.get_server_status(guild.id)
            # Server is linked, try to unban
            if roblox_id:
                unban_attempted = True
                status = await self.bot.prc_api.unban_user(guild.id, roblox_id)
                if status == 200:
                    unban_success = True
        except Exception:
            pass

        # Update embed
        embed.color = GREEN_COLOR

        if unban_attempted and unban_success:
            status_value = (
                f"**Accepted** by {interaction.user.mention}\n"
                f"Player `{roblox_username}` has been automatically unbanned."
            )
        elif unban_attempted and not unban_success:
            status_value = (
                f"**Accepted** by {interaction.user.mention}\n"
                f"⚠️ Automatic unban failed. Please unban `{roblox_username}` manually."
            )
        elif not roblox_id:
            status_value = (
                f"**Accepted** by {interaction.user.mention}\n"
                f"⚠️ Could not resolve Roblox account. Please unban `{roblox_username}` manually."
            )
        else:
            status_value = (
                f"**Accepted** by {interaction.user.mention}\n"
                f"⚠️ No ER:LC server linked. Please unban `{roblox_username}` manually."
            )

        embed.add_field(name="Result", value=status_value, inline=False)
        await interaction.message.edit(embed=embed, view=None)
        await interaction.followup.send("Appeal accepted.", ephemeral=True)

        # DM the appellant
        if appellant_id:
            try:
                user = await self.bot.fetch_user(appellant_id)
                dm_embed = discord.Embed(
                    title="Ban Appeal Accepted",
                    description=f"Your ban appeal in **{guild.name}** has been accepted.",
                    color=GREEN_COLOR,
                    timestamp=discord.utils.utcnow(),
                )
                if unban_success:
                    dm_embed.description += "\nYou have been automatically unbanned."
                else:
                    dm_embed.description += "\nPlease wait for staff to manually process your unban."
                await user.send(embed=dm_embed)
            except discord.HTTPException:
                pass


async def setup(bot):
    await bot.add_cog(OnAppealAccept(bot))
