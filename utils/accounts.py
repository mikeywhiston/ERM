import discord


class Accounts:
    # 👥 Roblox and Discord account management
    def __init__(self, bot):
        self.bot = bot

    # 🔢 Batch get Roblox user IDs from usernames
    async def batch_user_ids(self, usernames: list):
        roblox_users = await self.bot.roblox.get_users_by_usernames(usernames, expand=False)
        return [user.id for user in roblox_users if user]

    # 🔗 Convert Roblox username to Discord member
    async def roblox_to_discord(self, guild: discord.Guild, username: str, roles: list[int] = None, roblox_user_id=None):
        bot = self.bot

        # oauth2_users
        if not roblox_user_id:
            roblox_user = await bot.roblox.get_user_by_username(username, expand=False)
            roblox_id = roblox_user.id
        else:
            roblox_id = roblox_user_id
        
        linked_accounts = [i async for i in bot.oauth2_users.db.find({"roblox_id": roblox_id})]
        for linked_account in linked_accounts: 
            if guild.get_member(int(linked_account["discord_id"] or 0)):
                return guild.get_member(int(linked_account["discord_id"] or 0))
            else:
                try:
                    return await guild.fetch_member(int(linked_account["discord_id"] or 0))
                except discord.NotFound:
                    pass

        # query members
        members = await guild.query_members(username)
        if not members:
            return None
        
        if roles is not None:
            for member in members:
                if any(role.id in roles for role in member.roles):
                    return member
        
        # if no roles specified OR no member with roles, return the first member found
        return members[0] if members else None

    # 🔗 Convert Discord user ID to Roblox username
    async def discord_to_roblox(self, guild: discord.Guild, user_id: int):
        bot = self.bot

        # oauth2_users
        linked_account = await bot.oauth2_users.db.find_one({"discord_id": user_id})
        if linked_account:
            roblox_id = linked_account["roblox_id"]
            roblox_user = await bot.roblox.get_user(roblox_id)
            return roblox_user.name

        bloxlink_user = await bot.bloxlink.find_roblox(user_id)
        if bloxlink_user:
            roblox_id = bloxlink_user["robloxID"]
            roblox_user = await bot.roblox.get_user(roblox_id)
            return roblox_user.name
        
        return None