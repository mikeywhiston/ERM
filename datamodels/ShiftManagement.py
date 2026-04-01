import datetime  # 📅 Time handling
import asyncio  # 🔀 Async concurrency
import logging  # 📜 System logging
from typing import Optional  # 🧬 Optional type hint

import aiohttp  # 🌐 HTTP requests
from bson import ObjectId  # 🆔 MongoDB Object IDs
from discord.ext import commands  # 🛠️ Command extensions
import discord  # 🤖 Discord library
from utils.mongo import Document  # 🗄️ Database base class
from decouple import config  # 🔑 Configuration variables

from utils.basedataclass import BaseDataClass  # 🏗️ Base data class


class BreakItem(BaseDataClass):  # ☕ Represents a break
    start_epoch: int  # 🕒 Break start time
    end_epoch: int  # ⏹️ Break end time


class ShiftItem:  # ⌛ Represents a full shift
    id: str  # 🆔 Shift identifier
    username: str  # 👤 Member username
    nickname: str  # 🏷️ Member nickname
    user_id: int  # 🔢 Discord ID
    type: str  # 📋 Shift type
    start_epoch: int  # 🕒 Start time
    breaks: list  # ☕ List of breaks
    guild: int  # 🏰 Guild identifier
    moderations: list  # 👮 Moderation actions
    end_epoch: int  # ⏹️ End time
    added_time: int  # ➕ Manually added time
    removed_time: int  # ➖ Manually removed time

    def __init__(self, **kwargs):  # 🔨 Initialize shift object
        # 📦 Data model helper: Initialize ShiftItem with keyword arguments
        for key, value in kwargs.items():  # 🔄 Iterate arguments
            setattr(self, key, value)  # 🖇️ Set attribute


class ShiftManagement:  # ⌛ Manages shifts in DB
    def __init__(self, connection, current_shifts):  # 🔨 Setup manager
        # ⌛ Data model helper: Initialize ShiftManagement with DB connection
        self.shifts = Document(connection, current_shifts)  # 📚 DB document
        self.logger = logging.getLogger(__name__)  # 📜 Error logger

    async def fetch_shift(self, object_id: ObjectId) -> Optional[ShiftItem]:  # 🔍 Find a shift
        # ⌛ Data model helper: Fetch a shift by its unique ID
        shift = await self.shifts.find_by_id(object_id)  # 📡 Query DB
        if not shift:  # ❓ Check if found
            return None  # 🚫 Not found
        return ShiftItem(  # ✨ Create shift item
            id=shift["_id"],  # 🆔 ID
            username=shift["Username"],  # 👤 User
            nickname=shift["Nickname"],  # 🏷️ Nick
            user_id=shift["UserID"],  # 🔢 UserID
            type=shift["Type"],  # 📋 Type
            start_epoch=shift["StartEpoch"],  # 🕒 Start
            breaks=[  # ☕ Parse breaks
                BreakItem(start_epoch=item["StartEpoch"], end_epoch=item["EndEpoch"])
                for item in shift["Breaks"]
            ],
            guild=shift["Guild"],  # 🏰 Guild
            moderations=shift["Moderations"],  # 👮 Mods
            end_epoch=shift["EndEpoch"],  # ⏹️ End
            added_time=shift["AddedTime"],  # ➕ Added
            removed_time=shift["RemovedTime"],  # ➖ Removed
        )

    async def add_shift_by_user(  # 🆕 Start new shift
        self,
        member: discord.Member,
        shift_type: str,
        breaks: list,
        guild: int,
        timestamp: int = 0,
    ) -> ObjectId:
        """
        Adds a shift for the specified user to the database and syncs with external APIs.
        """
        # ⌛ Data model helper: Start a new shift for a user and sync across systems
        data = {  # 📦 Prepare data
            "_id": ObjectId(),  # 🆔 New ID
            "Username": member.name,  # 👤 Name
            "Nickname": member.display_name,  # 🏷️ Display
            "UserID": member.id,  # 🔢 ID
            "Type": shift_type,  # 📋 Type
            "StartEpoch": (  # 🕒 Timestamp
                datetime.datetime.now().timestamp()
                if timestamp in [0, None]
                else timestamp
            ),
            "Breaks": breaks,  # ☕ Breaks
            "Guild": guild,  # 🏰 Guild
            "Moderations": [],  # 👮 Mods
            "AddedTime": 0,  # ➕ 0
            "RemovedTime": 0,  # ➖ 0
            "EndEpoch": 0,  # ⏹️ 0
        }

        await self.shifts.db.insert_one(data)  # 📡 Save to DB

        url_var = config("BASE_API_URL")  # 🔗 API URL
        panel_url_var = config("PANEL_API_URL")  # 🔗 Panel URL

        async def sync_with_apis():  # 🖇️ API Sync helper
            # ⌛ Data model helper: Internal helper to sync shift data with external APIs
            async with aiohttp.ClientSession() as session:  # 🌐 HTTP Session
                tasks = []  # 📝 Task list

                if url_var not in ["", None]:  # ❓ Check base API
                    tasks.append(
                        session.get(
                            f"{url_var}/Internal/SyncStartShift/{data['_id']}",
                            headers={"Authorization": config("INTERNAL_API_AUTH")},
                            raise_for_status=True,
                        )
                    )

                if panel_url_var not in ["", None]:  # ❓ Check panel API
                    tasks.append(
                        session.post(
                            f"{panel_url_var}/{guild}/SyncStartShift?ID={data['_id']}",
                            headers={"X-Static-Token": config("PANEL_STATIC_AUTH")},
                            raise_for_status=True,
                        )
                    )

                if tasks:  # ❓ If any tasks
                    responses = await asyncio.gather(*tasks, return_exceptions=True)  # 🔀 Run all syncs
                    for response in responses:  # 🔄 Process results
                        if isinstance(response, Exception):  # ❌ Handle error
                            self.logger.error(f"API sync failed: {str(response)}")

        try:  # 🛡️ Execute sync
            await sync_with_apis()
        except aiohttp.ClientError as e:  # 🌐 Web error
            self.logger.error(f"Failed to sync shift start with APIs: {str(e)}")
        except Exception as e:  # ❗ General error
            self.logger.error(f"Unexpected error during API sync: {str(e)}")

        return data["_id"]  # ✅ Return ID

    async def add_time_to_shift(self, identifier: str, seconds: int):  # ➕ Add seconds
        """
        Adds time to the specified user's shift.
        """
        # ⌛ Data model helper: Extend shift duration by adding seconds
        document = await self.shifts.db.find_one({"_id": ObjectId(identifier)})  # 🔍 Find shift
        document["AddedTime"] += int(seconds)  # ➕ Increment
        await self.shifts.update_by_id(document)  # 📡 Update DB
        return document  # ✅ Return updated

    async def remove_time_from_shift(self, identifier: str, seconds: int):  # ➖ Remove seconds
        """
        Removes time from the specified user's shift.
        """
        # ⌛ Data model helper: Reduce shift duration by removing seconds
        document = await self.shifts.db.find_one({"_id": ObjectId(identifier)})  # 🔍 Find shift
        document["RemovedTime"] += int(seconds)  # ➖ Decrement
        await self.shifts.update_by_id(document)  # 📡 Update DB
        return document  # ✅ Return updated

    async def end_shift(  # ⏹️ End active shift
        self, identifier: str, guild_id: int | None = None, timestamp: int | None = None
    ):
        """
        Ends the specified user's shift and syncs with external APIs.
        """
        # ⌛ Data model helper: Terminate current shift and close active breaks
        document = await self.shifts.db.find_one({"_id": ObjectId(identifier)})  # 🔍 Find shift
        if not document:  # ❓ Check existence
            raise ValueError("Shift not found.")  # ❌ Fail if missing

        guild_id = guild_id if guild_id else document["Guild"]  # 🏰 Get guild

        if document["Guild"] != guild_id:  # ❓ Cross-check guild
            raise ValueError("Shift not found.")  # ❌ Fail if mismatch

        current_time = (  # 🕒 Set end time
            datetime.datetime.now().timestamp() if timestamp in [None, 0] else timestamp
        )
        document["EndEpoch"] = current_time  # ⏹️ Mark finished

        # Close any open breaks
        for breaks in document["Breaks"]:  # 🔄 Check breaks
            if breaks["EndEpoch"] == 0:  # ❓ Is break open
                breaks["EndEpoch"] = int(current_time)  # ⏹️ Close it

        await self.shifts.update_by_id(document)  # 📡 Save changes
        return document  # ✅ Return ended

    async def get_current_shift(self, member: discord.Member, guild_id: int):  # 🔍 Current shift
        """
        Gets the current shift for the specified user.
        """
        # ⌛ Data model helper: Retrieve the user's currently active shift
        return await self.shifts.db.find_one(  # 📡 Find active shift
            {"UserID": member.id, "EndEpoch": 0, "Guild": guild_id}
        )
