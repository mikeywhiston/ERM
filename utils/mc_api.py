import asyncio # ⏱️ Asynchronous operations
import typing # 📝 Type hinting
import aiohttp # 🌐 Asynchronous HTTP client
from datamodels.ServerKeys import ServerKey # 🔑 Server key model
from utils.prc_api import ResponseFailure, ServerStatus, Player, CommandLog, BanItem # 🛡️ API data/error models


class MCApiClient:
    # 🍁 Client for interacting with the Maple County API
    def __init__(self, bot, base_url: str, api_key: str): # 🏗️ Initialize client
        self.bot = bot # 🤖 Bot instance
        self.session = aiohttp.ClientSession() # 🚪 Start HTTP session
        self.api_key = api_key # 🔑 Static API key
        self.base_url = base_url # 🔗 API base URL

        bot.external_http_sessions.append(self.session) # 🔗 Track session for cleanup

    # 🔑 Get server key for a specific guild
    async def get_server_key(self, guild_id: int) -> ServerKey: # 🔍 Fetch key from bot storage
        return await self.bot.mc_keys.get_server_key(guild_id) # 📥 Return key model

    # 📡 Send internal API request to Maple County
    async def _send_api_request(
        self,
        method: typing.Literal["GET", "POST"], # 📥 HTTP method
        endpoint: str, # 📍 API endpoint
        guild_id: int, # 🏰 Target guild
        data: dict | None = None, # 📤 Request payload
        key: str | None = None, # 🔑 Optional override key
    ):
        if not key: # ❓ No override key provided
            internal_server_object = await self.get_server_key(guild_id) # 🔍 Fetch from DB
            internal_server_key = (
                internal_server_object if internal_server_object is not None else None
            )
            if internal_server_key is None: # 🚫 No key found
                return 401, {} # 🔇 Return unauthorized
            else:
                internal_server_key = internal_server_key.key # 🆔 Get actual key string
        else:
            internal_server_key = key # 🆔 Use provided key

        async with self.session.request( # 📡 Dispatch request
            method,
            url=f"{self.base_url}{endpoint}", # 🔗 Construct URL
            headers={
                "X-Static-Token": self.api_key, # 🛡️ Static auth header
                "Authorization": internal_server_key, # 🔑 Dynamic auth header
                "User-Agent": "ERM Bot (version 4)", # 🤖 Bot UA
            },
            json=data or {}, # 📤 Send JSON body
        ) as response:
            if response.status == 429: # 🛑 Rate limited
                retry_after = int((await response.json()).get("retry_after", 5)) # ⏳ Extract wait time
                await asyncio.sleep(retry_after) # 💤 Wait
                return await self._send_api_request( # 🔄 Retry request
                    method=method,
                    endpoint=endpoint,
                    guild_id=guild_id,
                    data=data,
                    key=key,
                )
            if response.status == 502: # ⚠️ Bad Gateway
                return await self._send_api_request( # 🔄 Immediate retry
                    method=method,
                    endpoint=endpoint,
                    guild_id=guild_id,
                    data=data,
                    key=key,
                )
            return response.status, ( # 📤 Return status and JSON
                await response.json() if response.content_type != "text/html" else {}
            )

    # 🌐 Get server status information
    async def get_server_status(self, guild_id: int): # 🔍 Fetch server details
        status_code, response_json = await self._send_api_request( # 📡 Call API
            "GET", "/Server", guild_id
        )
        if status_code == 200: # ✅ Success
            return ServerStatus( # 📦 Map to model
                name=response_json["Name"], # 🏷️ Server name
                owner_id=response_json["OwnerId"], # 👑 Owner ID
                co_owner_ids=response_json["CoOwnerIds"], # 🤝 Co-owner IDs
                current_players=response_json["CurrentPlayers"], # 👥 Player count
                max_players=response_json["MaxPlayers"], # 📶 Capacity
                join_key=response_json["JoinKey"], # 🔑 Secret join key
                # account_verified_request=response_json['AccVerifiedReq'] == 'Enabled',
                # team_balance=response_json['TeamBalance']
            )
        else: # ❌ Failure
            raise ResponseFailure(status_code=status_code, json_data=response_json) # 💥 Raise error

    # 🧪 Send test request to verify server key
    async def send_test_request(self, server_key: str) -> int | ServerStatus: # 🧪 Validation
        code, response_json = await self._send_api_request( # 📡 Test call
            "GET", "/Server", 0, None, server_key
        )
        return ( # 📤 Return code
            code
            if code != 200
            else ServerStatus(
                name=response_json["Name"],
                owner_id=response_json["OwnerId"],
                co_owner_ids=response_json["CoOwnerIds"],
                current_players=response_json["CurrentPlayers"],
                max_players=response_json["MaxPlayers"],
                join_key=response_json["JoinKey"],
                # account_verified_request=response_json['AccVerifiedReq'] == 'Enabled', - noah forgot to implement this!
                # team_balance=response_json['TeamBalance']
            )
        )

    # 👥 Get list of players in the server
    async def get_server_players(self, guild_id: int) -> list:
        status_code, response_json = await self._send_api_request(
            "GET", "/Server/Players", guild_id
        )
        if status_code == 200:
            new_list = []
            for item in response_json:
                # print(item)
                new_list.append(
                    Player(
                        username=item["Player"].split(":")[0],
                        id=item["Player"].split(":")[1],
                        permission=item["Permission"],
                        callsign=item.get("Callsign"),
                        team=item["Team"],
                    )
                )
            return new_list
        else:
            raise ResponseFailure(status_code=status_code, json_data=response_json)

    async def authorize(self, roblox_id: int, server_name: str, guild_id: int):
        status_code, response_json = await self._send_api_request(
            "POST",
            "/Server/Auth",
            0,
            {"RobloxId": roblox_id, "ServerName": server_name, "GuildId": guild_id},
            key="__PRE_AUTHORIZATION",
        )

        if status_code == 200:
            return response_json["token"]
        else:
            raise ResponseFailure(status_code=status_code, json_data=response_json)

    async def fetch_server_logs(self, guild_id: int):
        status_code, response_json = await self._send_api_request(
            "GET", "/Server/Commands", guild_id
        )
        if status_code == 200:
            return [
                CommandLog(
                    username=(
                        log_item["Player"].split(":")[0]
                        if ":" in log_item["Player"]
                        else log_item["Player"]
                    ),
                    user_id=(
                        log_item["Player"].split(":")[1]
                        if ":" in log_item["Player"]
                        else 0
                    ),
                    timestamp=log_item["Timestamp"],
                    is_automated=log_item["Player"] == "Remote Server",
                    command=log_item["Command"],
                )
                for log_item in response_json
            ]
        else:
            raise ResponseFailure(status_code=status_code, json_data=response_json)

    async def fetch_bans(self, guild_id: int):
        status_code, response_json = await self._send_api_request(
            "GET", "/Server/Bans", guild_id
        )

        if status_code == 200:
            if response_json == []:
                return []
            return [
                BanItem(user_id=int(user_id), username=username)
                for user_id, username in response_json.items()
            ]
        else:
            raise ResponseFailure(status_code=status_code, json_data=response_json)
