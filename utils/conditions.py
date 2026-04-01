import asyncio
from utils.prc_api import Player, ResponseFailure
from discord.ext import commands

# 🔄 Run a coroutine in the current event loop
def run_coroutine_in_loop(coro):
    loop = asyncio.get_running_loop()
    fut = loop.create_future()

    def wrapper():
        asyncio.ensure_future(coro).add_done_callback(
            lambda task: fut.set_result(task.result())
        )

    loop.call_soon(wrapper)
    return fut


"""
Condition Variables
- ERLC_Players
- ERLC_Moderators
- ERLC_Admins
- ERLC_Owner
- ERLC_Staff
- ERLC_Queue 
- ERLC_Police
- ERLC_Sheriff
- ERLC_Fire
- ERLC_DOT
- ERLC_Civilian
- ERLC_Jail
- ERLC_Vehicles
- OnDuty
- OnBreak
- ERLC_X_InGame
"""

"""
NOTABLE DESIGN LIMITATIONS
::: YOU MUST NOT HAVE SPACES IN YOUR CONSTANTS.
"""


# 🔢 Get the number of arguments for a function
def function_argument_count(func):
    return func.__code__.co_argcount


# 📛 Get the names of the arguments for a function
def argument_names(func):
    return func.__code__.co_varnames


"""
PREDETERMINED FUTURE FUNCTIONS
- These are asynchronous functions which help in the fetching of variables before passing to a custom function.
"""


# 📥 Fetch ERLC server queue status
async def get_queue(api_client, guild_id):
    try:
        queue = await api_client.get_server_queue(guild_id)
    except:  # this can end up not being implemented in MC API client; so just hope and pray ig
        queue = []


# 🕰️ Fetch online shifts for a guild
# 📡 Fetch online shifts for a guild
async def online_shifts(bot, guild_id):
    return [
        i
        async for i in bot.shift_management.shifts.db.find(
            {"Guild": guild_id, "EndEpoch": 0}
        )
    ]


# 🚗 Fetch spawned vehicles in ERLC server
async def get_vehicles(api_client, guild_id):
    try:
        vehicles = await api_client.get_server_vehicles(guild_id)
    except:  # this can end up not being implemented in MC API client; so just hope and pray ig
        vehicles = []
    return vehicles


"""
CUSTOM FUNCTIONS
- The arguments you can provide in these functions are shown in the fetch_predetermined_futures function.
"""


# 📊 Count ERLC players
def count_erlc_players(players: list[Player]):
    return len(players)


# 🛡️ Count ERLC moderators
def count_erlc_moderators(players: list[Player]):
    return len(list(filter(lambda x: x.permission == "Server Moderator", players)))


# 👮 Count ERLC admins
def count_erlc_admins(players: list[Player]):
    return len(list(filter(lambda x: x.permission == "Server Administrator", players)))


# 👑 Count ERLC owners
def count_erlc_owners(players: list[Player]):
    return len(
        list(
            filter(
                lambda x: x.permission
                not in ["Server Moderator", "Normal", "Server Administrator"],
                players,
            )
        )
    )


# 🚶 Count ERLC queue size
def count_erlc_queue(
    queue: list[Player],
):  # this one isnt supported for maple county yet
    return len(queue)


# 🚓 Count players on Police team
def count_erlc_police(players: list[Player]):
    return len(list(filter(lambda x: x.team == "Police", players)))


# 🏔️ Count players on Sheriff team
def count_erlc_sheriff(players: list[Player]):
    return len(list(filter(lambda x: x.team == "Sheriff", players)))


# 🚒 Count players on Fire team
def count_erlc_fire(players: list[Player]):
    return len(list(filter(lambda x: x.team == "Fire", players)))


# 🏗️ Count players on DOT team
def count_erlc_dot(players: list[Player]):
    return len(list(filter(lambda x: x.team == "DOT", players)))


# 🏘️ Count players on Civilian team
def count_erlc_civilian(players: list[Player]):
    return len(list(filter(lambda x: x.team == "Civilian", players)))


# ⛓️ Count players on Jail team
def count_erlc_jail(players: list[Player]):
    return len(list(filter(lambda x: x.team == "Jail", players)))


# 🚘 Count spawned vehicles
def count_erlc_vehicles(vehicles: list):
    return len(vehicles)


# 🔍 Check if a specific player is in-game
def x_ingame(players: list[Player], player: str):
    return int(player.lower() in [p.username.lower() for p in players])


# 🧹 Filter online status (incomplete)
def filter_online(shifts: list):
    return len(list(filter))


"""
Comparison Operators
(we're not stupid enough to use eval.)
"""


# ⚖️ Equals comparison
def equals_operator(v1: int, v2: int):
    return v1 == v2


# 📉 Less than comparison
def less_than_operator(v1: int, v2: int):
    return v1 < v2


# 📉 Less than or equal comparison
def less_than_or_equals_to_operator(v1: int, v2: int):
    return v1 <= v2


# 📈 More than comparison
def more_than_operator(v1: int, v2: int):
    return v1 > v2


# 📈 More than or equal comparison
def more_than_or_equals_to_operator(v1: int, v2: int):
    return v1 >= v2


# 🚫 Not equals comparison
def not_equals_to(v1: int, v2: int):
    return v1 != v2


operator_table = {
    "==": equals_operator,
    "<": less_than_operator,
    "<=": less_than_or_equals_to_operator,
    "!=": not_equals_to,
    ">": more_than_operator,
    ">=": more_than_or_equals_to_operator,
}

variable_table = [
    "ERLC_Players",  # these obviously still work for maple county as well
    "ERLC_Moderators",
    "ERLC_Admins",
    "ERLC_Owner",
    "ERLC_Staff",
    "ERLC_Queue",  # this doesnt work for maple county :(
    "ERLC_Police",
    "ERLC_Sheriff",
    "ERLC_Fire",
    "ERLC_DOT",
    "ERLC_Civilian",
    "ERLC_Jail",
    "ERLC_Vehicles",
    "OnDuty",
    "OnBreak",
    "ERLC_X_InGame",
]

value_finder_table = {
    "ERLC_Players": count_erlc_players,
    "ERLC_Moderators": count_erlc_moderators,
    "ERLC_Admins": count_erlc_admins,
    "ERLC_Owners": count_erlc_owners,
    "ERLC_Queue": count_erlc_queue,
    "ERLC_X_InGame": x_ingame,
    "ERLC_Police": count_erlc_police,
    "ERLC_Sheriff": count_erlc_sheriff,
    "ERLC_Fire": count_erlc_fire,
    "ERLC_DOT": count_erlc_dot,
    "ERLC_Civilian": count_erlc_civilian,
    "ERLC_Jail": count_erlc_jail,
    "ERLC_Vehicles": count_erlc_vehicles,
}


def handle_comparison_operations(v1, v2, operator):
    function = operator_table[operator]
    return function(v1, v2)


def separate_arguments(condition):
    return condition.split(" ")[0], condition.split(" ")[1:]  # ERLC_XInGame i_iMikey


async def handle_value(value, futures) -> int:
    condition, args = separate_arguments(value)
    if condition not in variable_table:
        return value  # this means we're comparing a raw constant
    else:
        func, func_args = determine_func_info(condition)
        submitted_arguments = []
        for item in func_args:
            submitted_arguments.append(futures[item.lower()]())

        if len(func_args) > 1:
            return func(*submitted_arguments, *args)
        else:
            return func(*submitted_arguments)


def determine_func_info(cond):
    func = value_finder_table[cond]
    return func, argument_names(func)


async def fetch_predetermined_futures(bot: commands.Bot, guild_id, condition, value, api_client=None):
    return { # these have been turned to futures for asynchronous reasons
        "queue": lambda: run_coroutine_in_loop(get_queue(api_client, guild_id)),
        "shifts": lambda: run_coroutine_in_loop(online_shifts(bot, guild_id)),
        "vehicles": lambda: run_coroutine_in_loop(get_vehicles(api_client, guild_id)),
        "bot": lambda: bot,
        "guild_id": lambda: guild_id,
        "condition": lambda: condition,
        "player": lambda: separate_arguments(value)[1][0],
    }
