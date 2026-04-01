"""
This configuration is used in setup as a base configuration before modification.
"""

import discord # 🎮 Import discord

base_configuration = { # ⚙️ Default bot settings
    "_id": 0, # 🆔 Primary key
    "antiping": { # 🔇 Anti-ping configuration
        "enabled": False, # 🔘 Active flag
        "role": [], # 🛡️ Targeted roles
        "bypass_role": [], # 🔓 Exempt roles
        "use_hierarchy": False, # ⚖️ Hierarchy check
    },
    "staff_management": { # 👥 Staff management module
        "enabled": False, # 🔘 Active flag
        "role": [], # 🎖️ Staff roles
        "management_role": [], # 👔 Management roles
        "channel": None, # 📺 Logs channel
        "loa_role": [], # 📅 LOA roles
        "ra_role": [], # 🛡️ RA roles
    },
    "punishments": { # 🔨 Punishment settings
        "enabled": False, # 🔘 Active flag
        "channel": None, # 📺 Main logs
        "kick_channel": None, # 👢 Kick logs
        "ban_channel": None, # 🚫 Ban logs
        "bolo_channel": None, # 🚨 BOLO logs
    },
    "shift_management": { # 👕 Shift tracking module
        "enabled": False, # 🔘 Active flag
        "role": [], # 🎖️ Staff roles
        "channel": None, # 📺 Shift logs
        "quota": 0, # 🔢 Time quota
        "nickname_prefix": "", # 🏷️ Nickname prefix
        "maximum_staff": 0, # 📶 Capacity limit
        "role_quotas": [], # 📊 Tiered quotas
    },
    "customisation": {"prefix": ">"}, # 🎨 Command prefix
    "shift_types": {"types": []}, # 👕 Shift categories
    "game_security": { # 🛡️ Game security module
        "enabled": False, # 🔘 Active flag
        "webhook_channel": None, # 📡 Webhook target
        "channel": None, # 📺 Security channel
        "role": [], # 🎖️ Security roles
    },
    "game_logging": { # 📋 Game logs module
        "message": {"enabled": False, "channel": None}, # 💬 Chat logs
        "sts": {"enabled": False, "channel": None}, # 👮 STS logs
        "priority": {"enabled": False, "channel": None}, # 🚨 Priority logs
    },
    "ERLC": { # 🧱 ERLC specific integration
        "player_logs": None, # 📺 Player tracking
        "kill_logs": None, # 💀 Kill tracking
        "elevation_required": None, # 📶 Permission level
        "rdm_mentionables": [], # 🔔 RDM pings
        "rdm_channel": None, # 📺 RDM reporting
        "automatic_shifts": {"enabled": False, "shift_type": None}, # 🤖 Auto-shifting
    },
}

"""
    Colour constants
"""

BLANK_COLOR = 0x2B2D31 # ⬛ Dark theme color
blank_color = BLANK_COLOR  # Redundancy # ⬛ Alias


GREEN_COLOR = discord.Colour.brand_green() # 🟩 Success color
RED_COLOR = 0xD12F32 # 🟥 Error color
ORANGE_COLOR = discord.Colour.orange() # 🟧 Warning color

SERVER_CONDITIONS = { # 📊 Condition mapping
    "In-Game Players": "ERLC_Players", # 👥 Players
    "In-Game Moderators": "ERLC_Moderators", # 🛡️ Mods
    "In-Game Admins": "ERLC_Admins", # 👔 Admins
    "In-Game Owner": "ERLC_Owner", # 👑 Owners
    "In-Game Staff": "ERLC_Staff", # 🎖️ Staff
    "In-Game Queue": "ERLC_Queue", # ⏳ Queue
    "On Duty Staff": "OnDuty", # 👕 Active
    "On Break Staff": "OnBreak", # ⏸️ Resting
    "Players on Police": "ERLC_Police", # 👮 LEO
    "Players on Sheriff": "ERLC_Sheriff", # 🤠 Sheriff
    "Players on Fire": "ERLC_Fire", # 🚒 Fire
    "Players on DOT": "ERLC_DOT", # 🚧 DOT
    "Players on Civilian": "ERLC_Civilian", # 🚶 Civs
    "Players on Jail": "ERLC_Jail", # ⛓️ Prisoners
    "Vehicles Spawned": "ERLC_Vehicles", # 🚘 Cars
    "If ... is in-game": "ERLC_X_InGame", # ❓ Specific search
}

RELEVANT_DESCRIPTIONS = [
    "All players currently in the in-game server.",
    "Number of moderators in the in-game server.",
    "Number of admins in the in-game server.",
    "Number of those with Co-Owner or Owner permission within the server.",
    "Number of staff members in the in-game server.",
    "Number of players in the queue.",
    "All staff members currently on duty.",
    "All staff members currently on break.",
    "Number of players on the Police team.",
    "Number of players on the Sheriff team.",
    "Number of players on the Fire team.",
    "Number of players on the DOT team.",
    "Number of players on the Civilian team.",
    "Number of players on the Jail team.",
    "Number of vehicles spawned in-game.",
    "If a specific user is in-game.",
]

CONDITION_OPTIONS = {
    "Equals": "==",
    "Less Than": "<",
    "Less Than or Equals To": "<=",
    "Not Equals To": "!=",
    "More Than": ">",
    "More Than or Equals To": ">=",
}

OPTION_DESCRIPTIONS = [
    "If the value is equal to the specified value.",
    "If the value is less than the specified value.",
    "If the value is less than or equal to the specified value.",
    "If the value is not equal to the specified value.",
    "If the value is more than the specified value.",
    "If the value is more than or equal to the specified value.",
]
