import discord # 🟦 Discord API
import jishaku # 🐱 Jishaku tool
from discord.ext import commands # 📦 Command framework
from jishaku.codeblocks import codeblock_converter, Codeblock # 📝 Code parsing
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES # ⚙️ Standard cogs
from jishaku.features.baseclass import Feature # 🏗️ Base class

OWNER = 1394817794427846737 # 👑 Master owner
LOGGING_CHANNEL = 1084950208842039326 # 📺 Log channel


class CustomDebugCog(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    """
    Custom Jishaku Cog for command logging
    """

    @Feature.Command(parent="jsk", name="creator") # 👑 Creator command
    async def jsk_creator(self, ctx: commands.Context):
        # 👑 Display the bot creator...
        try: # 🔍 Try fetch
            owner = await ctx.guild.fetch_member(OWNER) # 👤 Get owner
        except discord.NotFound: # ❌ Missing
            owner = None # 🚫 Set null

        if owner is None: # ❓ Not found
            return await ctx.send(
                f"The creator of {self.bot.user.mention} is <@{OWNER}>" # 📢 Global mention
            )

        embed = discord.Embed(
            title=f"{owner.name}#{owner.discriminator}", color=0x2A2D31 # 📄 Rich embed
        )
        embed.add_field(
            name=f"Owner of {self.bot.user.name}", # 👑 Ownership
            value=f"{owner.mention}", # 👤 Mention
            inline=False, # 📏 Wide
        )
        embed.add_field(name="ID", value=f"{owner.id}", inline=False) # 🆔 User ID
        embed.set_footer(
            text=f"{owner.name}#{owner.discriminator} is the owner of {self.bot.user.name}", # 📑 Footer label
            icon_url=ctx.guild.icon, # 🏠 Server icon
        )
        embed.set_thumbnail(url=owner.display_avatar.url) # 🖼️ Avatar
        await ctx.send(embed=embed) # 📤 Send response

    # async def cog_before_invoke(self, ctx: commands.Context):
    #     try:
    #         channel: discord.TextChannel = await self.bot.fetch_channel(LOGGING_CHANNEL)
    #     except (discord.NotFound, discord.Forbidden):
    #         pass
    #     else:
    #         selected_webhook = None
    #         try:
    #             for webhook in await channel.webhooks():
    #                 if webhook.name == f"{ctx.author.name}#{ctx.author.discriminator}":
    #                     selected_webhook = webhook
    #         except discord.Forbidden:
    #             return
    #
    #         if not selected_webhook:
    #             selected_webhook = await channel.create_webhook(
    #                 name=f"{ctx.author.name}#{ctx.author.discriminator}",
    #                 avatar=(await ctx.author.display_avatar.read()),
    #                 reason="Logs",
    #             )
    #
    #         embed = discord.Embed()
    #         if "`" in ctx.message.content:
    #             codeblock = codeblock_converter(
    #                 ctx.message.content[ctx.message.content.index("`") - 1 :]
    #             )
    #         else:
    #             codeblock = None
    #         if codeblock is not None:
    #             if ctx.guild:
    #                 embed.description = f"```\n{ctx.message.content[:ctx.message.content.index('`')-1]}```\n{codeblock.content}\n\n```\nServer Name: {ctx.guild.name}\nChannel Name: {ctx.channel.name}\nMember Count: {ctx.guild.member_count}\nOwner: {f'{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}'}```"
    #             else:
    #                 embed.description = f"```\n{ctx.message.content[:ctx.message.content.index('`') - 1]}```\n{codeblock.content}"
    #         else:
    #             if ctx.guild:
    #                 embed.description = f"```\n{ctx.message.content}```\n\n```\nServer Name: {ctx.guild.name}\nChannel Name: {ctx.channel.name}\nMember Count: {ctx.guild.member_count}\nOwner: {f'{ctx.guild.owner.name}#{ctx.guild.owner.discriminator}'}```"
    #             else:
    #                 embed.description = f"```\n{ctx.message.content}```"
    #         embed.title = "Jishaku Logging"
    #         embed.set_author(
    #             name=f"{ctx.author.name}#{ctx.author.discriminator}",
    #             icon_url=ctx.author.display_avatar.url,
    #         )
    #         embed.set_footer(text="️️©️ ERM Systems - Jishaku Logging Systems")
    #         try:
    #             await selected_webhook.send(embed=embed)
    #         except ValueError:
    #             await selected_webhook.delete()
    #             selected_webhook = await channel.create_webhook(
    #                 name=f"{ctx.author.name}#{ctx.author.discriminator}",
    #                 avatar=(await ctx.author.display_avatar.read()),
    #                 reason="Logs",
    #             )
    #             await selected_webhook.send(embed=embed)


async def setup(bot):
    # 🔩 Register Custom Jishaku cog...
    await bot.add_cog(CustomDebugCog(bot=bot))
