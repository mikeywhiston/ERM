import discord # 🟦 Discord API
from discord.ext import commands # 📦 Command framework

from menus import YesNoMenu, AccountLinkingMenu # 📑 Import menus
from utils.constants import BLANK_COLOR, GREEN_COLOR # 🎨 UI colors
import asyncio # 🕒 Async operations
import time # ⏱️ Time tracking


class OAuth2(commands.Cog):
    # ⚙️ Cog initialization
    def __init__(self, bot):
        self.bot = bot # 🤖 Bot instance

    @commands.hybrid_command(
        name="link", # 🏷️ Command name
        description="Link your Roblox account with ERM.", # 📝 Description
        extras={"ephemeral": True}, # 🔒 Private response
    )
    # 🔗 Link Roblox account
    async def link_roblox(self, ctx: commands.Context):
        msg = None # ✉️ Message placeholder
        linked_account = await self.bot.oauth2_users.db.find_one(
            {"discord_id": ctx.author.id} # 🔍 Lookup user
        )
        if linked_account: # ❓ Already linked
            user = await self.bot.roblox.get_user(linked_account["roblox_id"]) # 👤 Get Roblox user
            msg = await ctx.send(
                embed=discord.Embed(
                    title="Already Linked", # 📢 Embed title
                    description=f"You have already linked your account with `{user.name}`. Are you sure you would like to relink?", # 💬 Confirmation
                    color=BLANK_COLOR, # 🎨 Color
                ),
                view=(view := YesNoMenu(ctx.author.id)), # 🔘 Choice buttons
            )
            timeout = await view.wait() # ⏳ Wait for response
            if timeout or not view.value: # 🚫 Cancelled or timed out
                await msg.edit(
                    embed=discord.Embed(
                        title="Cancelled", # ❌ Cancel title
                        description="This action was cancelled by the user.", # 📝 Cancel text
                        color=BLANK_COLOR, # 🎨 Color
                    ),
                    view=None, # 🧹 Remove buttons
                )
                return # ↩️ Exit
        timestamp = time.time() # ⏰ Start time
        verification_message = {
            "embed": discord.Embed(
                title="Verify with ERM", # 🛡️ Verification title
                description="**To link your account with ERM, click the button below.**\nIf you encounter an error, please contact ERM Support by running `/support`.", # 📥 Instructions
                color=BLANK_COLOR, # 🎨 Color
            ),
            "view": AccountLinkingMenu(self.bot, ctx.author, ctx.interaction), # 🔘 Link button
        }

        await self.bot.pending_oauth2.db.insert_one({"discord_id": ctx.author.id}) # 💾 Track pending

        if msg is None: # 🆕 New message
            await ctx.send(**verification_message) # 📤 Send
        else: # 🔄 Update existing
            await msg.edit(**verification_message) # 📝 Edit

        attempts = 0 # 🔢 Attempt counter
        while await asyncio.sleep(3): # 🔄 Poll loop
            if attempts > 60: # 🛑 Limit attempts
                break # 🚪 Exit loop
            if not linked_account: # ✨ New link
                if await self.bot.oauth2_users.db.find_one(
                    {"discord_id": ctx.author.id} # 🔍 Check DB
                ):
                    await msg.edit(
                        embed=discord.Embed(
                            title=f"{self.bot.emoji_controller.get_emoji('success')} Linked", # ✅ Success
                            description="Your Roblox account has been successfully linked to ERM.", # 🎉 Success msg
                            color=GREEN_COLOR, # 🟢 Green
                        )
                    )
                    break # 🎉 Done
            else: # 🔄 Relink check
                if item := await self.bot.oauth2_users.db.find_one(
                    {"discord_id": ctx.author.id} # 🔍 Check DB
                ):
                    if item.get("last_updated", 0) > timestamp: # 📅 Time check
                        await msg.edit(
                            embed=discord.Embed(
                                title=f"{self.bot.emoji_controller.get_emoji('success')} Linked", # ✅ Success
                                description="Your Roblox account has been successfully linked to ERM.", # 🎉 Success msg
                                color=GREEN_COLOR, # 🟢 Green
                            )
                        )
                        break # 🎉 Done
                else:
                    linked_account = None # 🧹 Clear state
# 🛠️ Cog setup


async def setup(bot):
    await bot.add_cog(OAuth2(bot)) # 🔌 Add cog to bot
