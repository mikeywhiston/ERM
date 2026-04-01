import discord # 🎮 Import discord
from discord.ext import commands # 🛡️ Import discord commands
import aiohttp # 🌐 Asynchronous HTTP requests


class Bloxlink:
    # 🔗 Bloxlink API integration
    def __init__(self, bot: commands.Bot, key: str): # 🏗️ Initialize Bloxlink handler
        self.api_key = key # 🔑 API authorization key
        self.session = aiohttp.ClientSession() # 🚪 Start HTTP session
        bot.external_http_sessions.append(self.session) # 🔗 Link session to bot
        self.bot = bot # 🤖 Bot instance reference

    # 📡 Send internal HTTP request
    async def _send_request(self, method, url, params=None, body=None): # 📤 Low-level request handler
        async with self.session.request(
            method, url, params=params, headers={"Authorization": self.api_key} # 📬 Send request with auth
        ) as resp:
            return (resp, await resp.json()) # 📥 Return response and JSON data

    # 🔍 Find Roblox ID from Discord ID
    async def find_roblox(self, user_id: int): # 🔄 Lookup Roblox user
        doc = await self.bot.oauth2_users.db.find_one({"discord_id": user_id}) # 🗄️ Check local DB first
        if doc: # ✅ Found in local DB
            return {"robloxID": doc["roblox_id"]} # 📤 Return mapped ID

        response, resp_json = await self._send_request(
            "GET", f"https://api.blox.link/v4/public/discord-to-roblox/{user_id}" # 📡 Query Bloxlink API
        )

        if resp_json.get("error"): # ❌ Error in response
            return {} # 🚫 Return empty
        else:
            return resp_json # ✅ Return API result

    # ℹ️ Get Roblox user information
    async def get_roblox_info(self, user_id: int): # 🔍 Fetch profile details
        if not user_id: # ❓ Validate ID presence
            return {} # 🚫 Return empty

        async with aiohttp.ClientSession() as session: # 🚪 Open ephemeral session
            async with session.get(
                "https://users.roblox.com/v1/users/{}".format(user_id) # 📡 Roblox API call
            ) as resp:
                return await resp.json() # 📥 Return user info
