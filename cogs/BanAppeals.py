import discord
from discord.ext import commands
from erm import is_management
from utils.constants import BLANK_COLOR, GREEN_COLOR, RED_COLOR
from utils.utils import log_command_usage


class BanAppealModal(discord.ui.Modal):
    def __init__(self, bot, questions):
        super().__init__(title="Ban Appeal")
        self.bot = bot
        for q in questions[:5]:
            self.add_item(discord.ui.TextInput(
                label=q[:45],
                style=discord.TextStyle.paragraph,
                required=True,
            ))

    async def on_submit(self, interaction: discord.Interaction):
        answers = [child.value for child in self.children]

        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        ban_appeals = sett.get("ban_appeals", {})
        review_channel_id = ban_appeals.get("review_channel")
        ping_role_id = ban_appeals.get("ping_role")

        if not review_channel_id:
            return await interaction.response.send_message(
                "Ban appeals are not fully configured.", ephemeral=True
            )

        review_channel = interaction.guild.get_channel(review_channel_id)
        if not review_channel:
            return await interaction.response.send_message(
                "Review channel not found.", ephemeral=True
            )

        questions = ban_appeals.get("modal_questions", [])

        # Try to resolve Roblox user from the first answer (username)
        roblox_username = answers[0] if answers else "Unknown"
        roblox_id = None
        roblox_avatar_url = None
        try:
            roblox_user = await self.bot.roblox.get_user_by_username(roblox_username, expand=False)
            if roblox_user:
                roblox_id = roblox_user.id
                roblox_avatar_url = (await roblox_user.thumbnails.get_headshot(size=(150, 150))).image_url
        except Exception:
            pass

        embed = discord.Embed(
            title="Ban Appeal",
            color=BLANK_COLOR,
            timestamp=discord.utils.utcnow(),
        )
        embed.set_author(
            name=str(interaction.user),
            icon_url=interaction.user.display_avatar.url,
        )
        if roblox_avatar_url:
            embed.set_thumbnail(url=roblox_avatar_url)

        # Add Roblox info field
        if roblox_id:
            embed.add_field(
                name="Roblox Account",
                value=f"[{roblox_username}](https://www.roblox.com/users/{roblox_id}/profile) (`{roblox_id}`)",
                inline=True,
            )
        else:
            embed.add_field(
                name="Roblox Account",
                value=f"{roblox_username} (could not resolve)",
                inline=True,
            )

        embed.add_field(
            name="Discord Account",
            value=f"{interaction.user.mention} (`{interaction.user.id}`)",
            inline=True,
        )

        # Add a separator
        embed.add_field(name="\u200b", value="\u200b", inline=False)

        # Add each question/answer
        for i, answer in enumerate(answers):
            if i == 0:
                continue  # Skip username, already shown above
            label = questions[i] if i < len(questions) else f"Question {i+1}"
            embed.add_field(name=label, value=answer, inline=False)

        embed.set_footer(text=f"Appeal from User ID: {interaction.user.id}")

        ping_content = f"<@&{ping_role_id}>" if ping_role_id else None
        await review_channel.send(
            content=ping_content,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True),
            view=AppealReviewView(
                self.bot,
                interaction.user.id,
                roblox_username,
                roblox_id,
            ),
        )
        await interaction.response.send_message(
            embed=discord.Embed(
                title="Appeal Submitted",
                description="Your ban appeal has been submitted and is pending review.",
                color=GREEN_COLOR,
            ),
            ephemeral=True,
        )


class AppealReviewView(discord.ui.View):
    def __init__(self, bot, appellant_id, roblox_username, roblox_id=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.appellant_id = appellant_id
        self.roblox_username = roblox_username
        self.roblox_id = roblox_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, custom_id="ban_appeal:accept")
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        embed = interaction.message.embeds[0]

        # Try to get roblox_id from embed if we don't have it (after restart)
        roblox_id = self.roblox_id
        roblox_username = self.roblox_username

        if not roblox_id or roblox_username == "Unknown":
            # Try to parse from embed fields
            for field in embed.fields:
                if field.name == "Roblox Account":
                    # Try to extract ID from the value like "username (`12345`)"
                    if "`" in field.value:
                        try:
                            roblox_id = int(field.value.split("`")[1])
                        except (ValueError, IndexError):
                            pass
                    # Extract username from value
                    if "[" in field.value:
                        roblox_username = field.value.split("[")[1].split("]")[0]
                    break

        # If still no roblox_id, try to look it up
        if not roblox_id and roblox_username != "Unknown":
            try:
                roblox_user = await self.bot.roblox.get_user_by_username(roblox_username, expand=False)
                if roblox_user:
                    roblox_id = roblox_user.id
            except Exception:
                pass

        # Try to get appellant_id from footer if we lost it (after restart)
        appellant_id = self.appellant_id
        if not appellant_id:
            try:
                footer_text = embed.footer.text or ""
                if "User ID:" in footer_text:
                    appellant_id = int(footer_text.split("User ID:")[1].strip())
            except (ValueError, IndexError):
                pass

        # Attempt unban via PRC API
        unban_success = False
        unban_attempted = False

        try:
            await self.bot.prc_api.get_server_status(interaction.guild.id)
            # Server is linked, try to unban
            if roblox_id:
                unban_attempted = True
                status = await self.bot.prc_api.unban_user(interaction.guild.id, roblox_id)
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
                    description=f"Your ban appeal in **{interaction.guild.name}** has been accepted.",
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

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red, custom_id="ban_appeal:deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Open a modal for the deny reason
        modal = discord.ui.Modal(title="Deny Ban Appeal")
        reason_input = discord.ui.TextInput(
            label="Reason for denial",
            style=discord.TextStyle.paragraph,
            placeholder="Enter the reason for denying this appeal...",
            required=True,
            max_length=1024,
        )
        modal.add_item(reason_input)

        async def on_deny_submit(modal_interaction: discord.Interaction):
            reason = reason_input.value

            embed = interaction.message.embeds[0]

            # Get appellant_id from footer if needed (after restart)
            appellant_id = self.appellant_id
            if not appellant_id:
                try:
                    footer_text = embed.footer.text or ""
                    if "User ID:" in footer_text:
                        appellant_id = int(footer_text.split("User ID:")[1].strip())
                except (ValueError, IndexError):
                    pass

            embed.color = RED_COLOR
            embed.add_field(
                name="Result",
                value=f"**Denied** by {modal_interaction.user.mention}\n**Reason:** {reason}",
                inline=False,
            )
            await interaction.message.edit(embed=embed, view=None)
            await modal_interaction.response.send_message("Appeal denied.", ephemeral=True)

            if appellant_id:
                try:
                    user = await self.bot.fetch_user(appellant_id)
                    await user.send(embed=discord.Embed(
                        title="Ban Appeal Denied",
                        description=(
                            f"Your ban appeal in **{modal_interaction.guild.name}** has been denied.\n\n"
                            f"**Reason:** {reason}"
                        ),
                        color=RED_COLOR,
                        timestamp=discord.utils.utcnow(),
                    ))
                except discord.HTTPException:
                    pass

        modal.on_submit = on_deny_submit
        await interaction.response.send_modal(modal)


class AppealPanelView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Submit Appeal", style=discord.ButtonStyle.primary, custom_id="ban_appeal:submit")
    async def submit_appeal(self, interaction: discord.Interaction, button: discord.ui.Button):
        sett = await self.bot.settings.find_by_id(interaction.guild.id)
        ba = sett.get("ban_appeals", {})
        questions = ba.get("modal_questions", [
            "What is your Roblox Username?",
            "Why were you banned?",
            "Why should you be unbanned?",
        ])
        modal = BanAppealModal(self.bot, questions)
        await interaction.response.send_modal(modal)


class BanAppeals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Register persistent views so buttons work after restart
        self.bot.add_view(AppealReviewView(bot, None, "Unknown", None))
        self.bot.add_view(AppealPanelView(bot))

    @commands.hybrid_group(
        name="ban_appeals",
        description="Ban appeal management.",
        extras={"category": "Ban Appeals"},
    )
    async def ban_appeals(self, ctx):
        pass

    @ban_appeals.command(
        name="panel",
        description="Send the ban appeal panel to the configured channel.",
    )
    @is_management()
    async def panel(self, ctx: commands.Context):
        await log_command_usage(self.bot, ctx.guild, ctx.author, "Ban Appeals Panel")

        sett = await self.bot.settings.find_by_id(ctx.guild.id)
        ba = sett.get("ban_appeals", {})

        if not ba.get("enabled"):
            return await ctx.send(embed=discord.Embed(
                title="Not Enabled",
                description="Ban appeals are not enabled. Use the setup command to enable them.",
                color=BLANK_COLOR,
            ))

        panel_channel_id = ba.get("panel_channel")
        if not panel_channel_id:
            return await ctx.send(embed=discord.Embed(
                title="Not Configured",
                description="No panel channel has been set.",
                color=BLANK_COLOR,
            ))

        panel_channel = ctx.guild.get_channel(panel_channel_id)
        if not panel_channel:
            return await ctx.send(embed=discord.Embed(
                title="Channel Not Found",
                description="The configured panel channel could not be found.",
                color=BLANK_COLOR,
            ))

        embed = discord.Embed(
            title=ba.get("embed_title", "Ban Appeal"),
            description=ba.get("embed_description", "Click the button below to submit a ban appeal."),
            color=ba.get("embed_color", BLANK_COLOR),
        )
        if ba.get("thumbnail_url"):
            embed.set_thumbnail(url=ba["thumbnail_url"])
        if ba.get("image_url"):
            embed.set_image(url=ba["image_url"])

        panel_view = AppealPanelView(self.bot)
        # Set custom button label from config
        button_label = ba.get("button_label", "Submit Appeal")
        panel_view.submit_appeal.label = button_label
        await panel_channel.send(embed=embed, view=panel_view)
        await ctx.send(embed=discord.Embed(
            title="Panel Sent",
            description=f"Ban appeal panel sent to {panel_channel.mention}.",
            color=GREEN_COLOR,
        ))


async def setup(bot):
    await bot.add_cog(BanAppeals(bot))
