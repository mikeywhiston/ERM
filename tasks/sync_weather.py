import asyncio
import logging
from discord.ext import tasks
import aiohttp
from decouple import config

from utils.prc_api import ResponseFailure

# Open-Meteo WMO weather code -> ERLC :weather command value
# https://open-meteo.com/en/docs (WMO Weather interpretation codes)
WMO_TO_ERLC = {
    0:  "Clear",        # Clear sky
    1:  "Clear",        # Mainly clear
    2:  "Clouds",       # Partly cloudy
    3:  "Clouds",       # Overcast
    45: "Fog",          # Foggy
    48: "Fog",          # Icy fog
    51: "Drizzle",      # Light drizzle
    53: "Drizzle",      # Moderate drizzle
    55: "Drizzle",      # Dense drizzle
    61: "Rain",         # Slight rain
    63: "Rain",         # Moderate rain
    65: "Rain",         # Heavy rain
    71: "Snow",         # Slight snow
    73: "Snow",         # Moderate snow
    75: "Snow",         # Heavy snow
    77: "Snow",         # Snow grains
    80: "Rain",         # Slight rain showers
    81: "Rain",         # Moderate rain showers
    82: "Rain",         # Violent rain showers
    85: "Snow",         # Slight snow showers
    86: "Snow",         # Heavy snow showers
    95: "Thunderstorm", # Thunderstorm
    96: "Thunderstorm", # Thunderstorm with hail
    99: "Thunderstorm", # Thunderstorm with heavy hail
}

# Open-Meteo hour (0-23) -> ERLC :time command value
def hour_to_erlc_time(hour: int) -> str:
    # 🕒 Converting hour to ERLC time...
    if 5 <= hour < 7:
        return "Morning"
    elif 7 <= hour < 12:
        return "Noon"
    elif 12 <= hour < 17:
        return "Afternoon"
    elif 17 <= hour < 20:
        return "Evening"
    else:
        return "Night"


async def geocode_location(session: aiohttp.ClientSession, location: str) -> tuple[float, float, str] | None:
    # 📍 Geocoding location...
    """Convert a location name to lat/lon + timezone using Open-Meteo geocoding API."""
    try:
        async with session.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": location, "count": 1, "language": "en", "format": "json"},
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            results = data.get("results")
            if not results:
                return None
            r = results[0]
            return r["latitude"], r["longitude"], r.get("timezone", "UTC")
    except Exception as e:
        logging.error(f"Geocoding failed for location '{location}': {e}")
        return None


async def fetch_weather(session: aiohttp.ClientSession, lat: float, lon: float, timezone: str) -> dict | None:
    # 🌤️ Fetching weather data...
    """Fetch current weather code and local hour from Open-Meteo."""
    try:
        async with session.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "weather_code,is_day",
                "hourly": "weather_code",
                "timezone": timezone,
                "forecast_days": 1,
            },
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()

            current = data.get("current", {})
            weather_code = current.get("weather_code", 0)

            # Derive local hour from the current_time string e.g. "2024-03-01T14:00"
            current_time_str = data.get("current_time") or current.get("time", "")
            if "T" in current_time_str:
                hour = int(current_time_str.split("T")[1].split(":")[0])
            else:
                hour = 12  # fallback to noon

            return {
                "weatherType": WMO_TO_ERLC.get(weather_code, "Clear"),
                "time": hour_to_erlc_time(hour),
            }
    except Exception as e:
        logging.error(f"Weather fetch failed for ({lat}, {lon}): {e}")
        return None


@tasks.loop(minutes=2, reconnect=True)
async def sync_weather(bot):
    # ☁️ Syncing weather across servers...
    chosen_filter = {
        "CUSTOM": {"_id": int(config("CUSTOM_GUILD_ID", default=0))},
        "_": {
            "_id": {
                "$nin": [
                    int(item["GuildID"] or 0)
                    async for item in bot.whitelabel.db.find({})
                ]
            }
        },
    }["CUSTOM" if config("ENVIRONMENT") == "CUSTOM" else "_"]

    try:
        logging.info("Starting weather sync task...")

        pipeline = [
            {
                "$match": {
                    "ERLC.weather": {"$exists": True},
                    "$or": [
                        {"ERLC.weather.sync_time": True},
                        {"ERLC.weather.sync_weather": True},
                    ],
                    "ERLC.weather.location": {"$exists": True, "$ne": ""},
                    **chosen_filter,
                }
            },
            {
                "$lookup": {
                    "from": "server_keys",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "server_key",
                }
            },
            {"$match": {"server_key": {"$ne": []}}},
        ]

        server_count = await bot.settings.db.count_documents(
            {
                "ERLC.weather": {"$exists": True},
                "$or": [
                    {"ERLC.weather.sync_time": True},
                    {"ERLC.weather.sync_weather": True},
                ],
                "ERLC.weather.location": {"$exists": True, "$ne": ""},
            }
        )
        logging.info(f"Found {server_count} servers with weather sync enabled")

        # Cache geocoding results within this run to avoid duplicate lookups
        geocode_cache: dict[str, tuple[float, float, str] | None] = {}

        processed = 0
        async with aiohttp.ClientSession() as session:
            async for guild_data in bot.settings.db.aggregate(pipeline):
                processed += 1
                guild_id = guild_data["_id"]

                if config("ENVIRONMENT") == "CUSTOM":
                    if guild_id != int(config("CUSTOM_GUILD_ID", default=0)):
                        continue

                weather_settings = guild_data["ERLC"]["weather"]
                location = weather_settings["location"]

                logging.info(f"Processing guild {guild_id} ({processed}/{server_count}), location: {location}")

                try:
                    # Geocode if not already cached
                    if location not in geocode_cache:
                        geocode_cache[location] = await geocode_location(session, location)

                    geo = geocode_cache[location]
                    if geo is None:
                        logging.error(f"Could not geocode location '{location}' for guild {guild_id}")
                        continue

                    lat, lon, timezone = geo
                    weather_data = await fetch_weather(session, lat, lon, timezone)

                    if weather_data is None:
                        logging.error(f"Could not fetch weather for guild {guild_id}")
                        continue

                    logging.info(f"Weather data for guild {guild_id}: {weather_data}")

                    if weather_settings.get("sync_weather"):
                        try:
                            await bot.prc_api.run_command(guild_id, f":weather {weather_data['weatherType']}")
                            logging.info(f"Set weather to {weather_data['weatherType']} for guild {guild_id}")
                        except ResponseFailure as e:
                            logging.error(f"Failed to sync weather for guild {guild_id}: {str(e)}")

                    if weather_settings.get("sync_time"):
                        try:
                            await bot.prc_api.run_command(guild_id, f":time {weather_data['time']}")
                            logging.info(f"Set time to {weather_data['time']} for guild {guild_id}")
                        except ResponseFailure as e:
                            logging.error(f"Failed to sync time for guild {guild_id}: {str(e)}")

                except Exception as e:
                    logging.error(f"Error syncing weather for guild {guild_id}: {str(e)}", exc_info=True)

        logging.info(f"Weather sync task completed. Processed {processed}/{server_count} servers")

    except Exception as e:
        logging.error(f"Critical error in weather sync task: {str(e)}", exc_info=True)
