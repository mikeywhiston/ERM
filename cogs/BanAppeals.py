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
            if isinstance(q, dict):
                style = discord.TextStyle.short if q.get("style") == "short" else discord.TextStyle.paragraph
                self.add_item(discord.ui.TextInput(
                    label=q.get("label", "Question")[:45],
                    placeholder=q.get("placeholder", "")[:100],
                    style=style,
                    required=q.get("required", True),
                ))
            else:
                # Backwards compatibility with plain string questions
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
        ping_role_ids = ban_appeals.get("ping_roles", [])

        if not review_channel_id:
            return await interaction.response.send_message(
                "No review channel is currently set. Ban Appeals not fully configured.", ephemeral=True
            )

        review_channel = interaction.guild.get_channel(review_channel_id)
        if not review_channel:
            try:
                review_channel = await interaction.guild.fetch_channel(review_channel_id)
            except discord.HTTPException:
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
            q = questions[i] if i < len(questions) else None
            label = q.get("label", f"Question {i+1}") if isinstance(q, dict) else (q or f"Question {i+1}")
            embed.add_field(name=label, value=answer, inline=False)

        embed.set_footer(text=f"Appeal from User ID: {interaction.user.id}")

        ping_content = " ".join(f"<@&{rid}>" for rid in ping_role_ids) if ping_role_ids else None
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
            for field in embed.fields:
                if field.name == "Roblox Account":
                    if "`" in field.value:
                        try:
                            roblox_id = int(field.value.split("`")[1])
                        except (ValueError, IndexError):
                            pass
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

        # Get appellant_id from footer if needed (after restart)
        appellant_id = self.appellant_id
        if not appellant_id:
            try:
                footer_text = embed.footer.text or ""
                if "User ID:" in footer_text:
                    appellant_id = int(footer_text.split("User ID:")[1].strip())
            except (ValueError, IndexError):
                pass

        self.bot.dispatch(
            "appeal_accept",
            interaction.guild,
            interaction,
            appellant_id,
            roblox_username,
            roblox_id,
            embed,
        )

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
        name="appeals",
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
