from copy import copy # 📋 Shallow copy utility

import discord # 🎮 Discord library
from discord.ext import commands # 🛡️ Discord extensions
import reactionmenu # 📑 Reaction-based menus
import typing # 📝 Type hinting

from erm import Bot # 🤖 Bot model
from menus import CustomSelectMenu # 🖱️ Custom selection
from utils.constants import blank_color # 🎨 Theme color
import asyncio # ⏱️ Async support
import nest_asyncio # 🪺 Nested loops


class CustomPage:
    embeds: list[discord.Embed] # 🖼️ Embed list
    view: typing.Optional[discord.ui.View] # 👁️ Optional view
    identifier: typing.Optional[str] # 🆔 Page ID

    # 📄 Data model for a custom pagination page
    def __init__(self, **kwargs): # 🏗️ Initialize page
        for key, value in kwargs.items(): # 🔁 Iterate properties
            setattr(self, key, value) # 🏷️ Set attributes


class SelectPagination(discord.ui.View):
    # 📑 View for select-based pagination
    def __init__(
        self,
        bot: Bot, # 🤖 Bot instance
        user_id: int, # 👤 Authorized user
        pages: list[CustomPage], # 📄 List of pages
        start_at=0, # 🔢 Starting index
        edit_method=None, # 🛠️ Optional edit handler
    ):
        super().__init__(timeout=None) # 🏗️ Init base view
        # we don't need this for the pagination, only the emojis :sob:
        self.bot = bot # 🤖 Bot reference
        names_to_emojis = {"1": "l_arrow", "2": "arrow"} # 🖼️ Button mapping
        for button in self.children: # 🔁 Iterate buttons
            if isinstance(button, discord.ui.Button): # ❓ Is a button
                if button.emoji is not None: # ❓ Has emoji
                    button.emoji = discord.PartialEmoji.from_str( # 🖼️ Update emoji
                        bot.emoji_controller.get_emoji(names_to_emojis[button.label])
                    )
                    button.label = "" # 🧹 Clear text label

        self.pages = pages # 📁 Store pages
        self.user_id = user_id # 👤 Store user
        self.current_index = start_at # 🔢 Current location
        self.view = self # 👁️ View reference
        self.preset_children = copy(self.children) # 📋 Baseline UI
        self.page_children = [] # 📁 Dynamic components
        self.edit_method = edit_method # 🛠️ Store handler

        starting_page = self.pages[self.current_index] # 📄 Get initial page
        if starting_page.identifier: # ❓ Has ID
            for item in self.children: # 🔁 Iterate UI
                if item.label == "TEMP": # 🔍 Match placeholder
                    item.label = starting_page.identifier # 🏷️ Set ID

    # 👁️ Get the view for the current page
    def get_current_view(self) -> discord.ui.View: # 🔍 UI resolver
        current_page = self.pages[self.current_index] # 📄 Actual page
        new_page = self.pages[self.current_index] # 📄 Target (same here)
        new_index = self.current_index # 🔢 Current index

        view = self.view # 👁️ View handle
        self.current_index = new_index # 📝 Force index update

        page_view = getattr(new_page, "view", None) # 🔍 Extract inner view
        for i in view.children: # 🔁 Update labels
            if i.label == current_page.identifier: # ❓ Match current
                i.label = new_page.identifier # 🏷️ Set new
        if page_view: # ✅ Dynamic view exists
            # checks = [i.row in [None, 0] for i in page_view.children]
            # Remove all non-native components
            for child in view.children: # 🔁 Clean UI
                if child not in self.preset_children: # ❓ Is dynamic
                    view.children.remove(child) # 🗑️ Remove it

            self.page_children = [] # 🧹 Reset dynamic list
            # if any(checks):
            #     for index, child in enumerate(page_view.children):
            #         if child.row is None:
            #             child.row = 1
            #         else:
            #             child.row += 1
            #         page_view.children[index] = child
            #         self.page_children.append(child)
            # else:
            for index, child in enumerate(page_view.children): # 🔁 Re-add dynamic
                self.page_children.append(child) # 📝 Add to list

            for item in self.page_children: # 🔁 Final setup
                # Sanity check validations
                if getattr(item, "default", None) is not None: # ❓ Has default
                    if item.default > len(item.options): # 🛡️ Bounds check
                        item.default = 0 # 🩹 Correction
                        # print(f'INVALID ::: {item}')
                elif getattr(item, "default_values", None) is not None:
                    if len(item.default_values) > item.max_values:
                        item.default_values = []
                        # print(f'INVALID ::: {item}')
                else:
                    # print(item)
                    # print(f'Somewhat valid ::: {item}')
                    pass
                view.add_item(item)
        return view

    # 🔄 Internal pagination logic
    async def _paginate(
        self,
        interaction: discord.Interaction,
        increment_index: int,
        mode: typing.Literal["set", "increment"],
    ):
        current_page = self.pages[self.current_index]

        if mode == "set":
            new_index = increment_index
            new_page = self.pages[new_index]
        else:
            new_index = self.current_index + increment_index
            if new_index >= len(self.pages):
                new_index = 0
            new_page = self.pages[new_index]

        view = self.view
        self.current_index = new_index

        page_view = getattr(new_page, "view", None)
        for i in view.children:
            if getattr(i, "label", None):
                if i.label == current_page.identifier:
                    i.label = new_page.identifier

        if page_view:
            # Clear the items added by the previous page
            for item in self.page_children:
                view.remove_item(item)
            self.page_children.clear()

            # Add the items from the new page
            for item in page_view.children:
                if getattr(item, "default", None) is not None:
                    if item.default > len(item.options):
                        item.default = 0
                elif getattr(item, "default_values", None) is not None:
                    if len(item.default_values) > item.max_values:
                        item.default_values = []
                else:
                    # print(item)
                    pass
                view.add_item(item)
                self.page_children.append(item)

        if self.edit_method:
            await self.edit_method(embeds=new_page.embeds, view=view)
        else:
            await interaction.message.edit(embeds=new_page.embeds, view=view)

    # ⬅️ Back button handler
    @discord.ui.button(label="1", emoji="<:l_arrow:1169754353326903407>", row=4)
    async def back_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )
        await interaction.response.defer()
        await self._paginate(interaction, -1, "increment")

    # 🔢 Jump to page button handler
    @discord.ui.button(label="TEMP", row=4)
    async def set_current_page(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )
        await interaction.response.defer(ephemeral=True, thinking=True)

        msg = await interaction.followup.send(
            embed=discord.Embed(
                title="Change Pages",
                description="What page would you like to change to?",
                color=blank_color,
            ),
            view=(
                view := CustomSelectMenu(
                    self.user_id,
                    [
                        discord.SelectOption(label=page.identifier, value=str(index))
                        for index, page in enumerate(self.pages)
                    ],
                )
            ),
        )

        await view.wait()
        index = int(view.value or "1000")
        await msg.delete()
        if index != 1000:
            await self._paginate(interaction, index, "set")

    # ➡️ Next button handler
    @discord.ui.button(label="2", emoji="<:arrow:1169695690784518154>", row=4)
    async def next_button(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.user.id != self.user_id:
            return await interaction.response.send_message(
                embed=discord.Embed(
                    title="Not Permitted",
                    description="You are not permitted to interact with these buttons.",
                    color=blank_color,
                ),
                ephemeral=True,
            )
        await interaction.response.defer()
        await self._paginate(interaction, 1, "increment")
