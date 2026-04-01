import os # 📂 Operating system interface
import asyncio # ⏱️ Asynchronous operations
import nest_asyncio # 🪺 Nested event loops support

nest_asyncio.apply()  # dangerous! # ⚠️ Apply nest_asyncio patch

default_emojis = { # 🖼️ Default emoji ID mapping
    "check": 1163142000271429662, # ✅ Checkmark
    "xmark": 1166139967920164915, # ❌ X-mark
    "success": 1163149118366040106, # 🎉 Success icon
    "error": 1164666124496019637, # 🚫 Error icon
    "WarningIcon": 1035258528149033090, # ⚠️ Warning icon
    "loa": 1169799727143977090, # 📅 LOA icon
    "log": 1163524830319104171, # 📋 Log icon
    "shift": 1169801400545452033, # 👕 Shift icon
    "Clock": 1035308064305332224, # 🕒 Clock icon
    "ShiftStarted": 1178033763477889175, # ▶️ Shift start
    "ShiftBreak": 1178034531702411375, # ⏸️ Shift break
    "ShiftEnded": 1178035088655646880, # ⏹️ Shift end
    "arrow": 1169695690784518154, # ➡️ Arrow icon
    "l_arrow": 1169754353326903407, # ⬅️ Left arrow
    "security": 1169804198741823538, # 🛡️ Security icon
}


class EmojiController:
    # 🎨 Controller for application emojis
    def __init__(self, bot): # 🏗️ Initialize controller
        self.environment = bot.environment # 🌐 Bot environment
        self.bot = bot # 🤖 Bot instance
        self.emojis = {} # 🗄️ Emoji cache

    # 📥 Fetch and create missing emojis
    async def prefetch_emojis(self): # 🔄 Load application emojis

        application_emojis = await self.bot.fetch_application_emojis() # 📡 Fetch from Discord
        for item in os.listdir("assets/emojis"): # 📂 Scan assets folder
            if item.endswith(".png"): # 🖼️ Check for PNG images
                if item.replace(".png", "") not in [i.name for i in application_emojis]: # ❓ Missing on Discord
                    emoji_name = item.replace(".png", "") # 🏷️ Clean name
                    image_data = open(f"assets/emojis/{item}", "rb").read() # 📖 Read image bytes
                    await self.bot.create_application_emoji( # 📤 Upload to Discord
                        name=emoji_name, image=image_data
                    )

        new_application_emojis = await self.bot.fetch_application_emojis() # 📡 Re-fetch updated list
        for emoji in new_application_emojis: # 🔁 Iterate and cache
            self.emojis[emoji.name] = emoji.id # 🆔 Store ID by name

    # 🖼️ Get emoji string by name
    def get_emoji(self, emoji_name): # 🔍 Resolve emoji to string
        if not self.emojis: # ❓ Cache empty
            asyncio.run(self.prefetch_emojis()) # 🔄 Run prefetch

        return "<:{}:{}>".format(emoji_name, self.emojis[emoji_name]) # 📤 Return Discord format
