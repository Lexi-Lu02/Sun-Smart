import httpx
import time
from datetime import datetime

# Simple in-memory cache: key = "lat,lon", value = {data, timestamp}
_cache: dict = {}
CACHE_TTL = 900  # 15 minutes in seconds

# MED values by skin type (Fitzpatrick scale)
MED_VALUES = {
    "type1": 200,
    "type2": 250,
    "type3": 300,
    "type4": 450,
}

UV_LEVELS = [
    (2,  "Low",       "#4ade80", "SPF 15+"),
    (5,  "Moderate",  "#facc15", "SPF 30+"),
    (7,  "High",      "#fb923c", "SPF 30+"),
    (10, "Very High", "#f87171", "SPF 50+"),
    (99, "Extreme",   "#c084fc", "SPF 50+"),
]


def get_uv_level(uv_index: float):
    """Return level label, color, and SPF recommendation."""
    for threshold, label, color, spf in UV_LEVELS:
        if uv_index <= threshold:
            return label, color, spf
    return "Extreme", "#c084fc", "SPF 50+"


def calc_burn_time(uv_index: float, skin_type: str = "type2") -> int:
    """Calculate minutes until skin starts burning."""
    if uv_index <= 0:
        return 999
    med = MED_VALUES.get(skin_type, 250)
    minutes = med / (uv_index * 0.025)
    return int(round(minutes))


def build_alert_message(uv_index: float, burn_time: int) -> str:
    """Generate human language alert string."""
    if burn_time >= 999:
        return "UV levels are safe right now. Enjoy the outdoors!"
    return (
        f"Your skin will start burning in ~{burn_time} minutes "
        f"— find shade or apply SPF 50+ now."
    )


async def fetch_uv_data(lat: float, lon: float, skin_type: str = "type2"):
    """Fetch UV index from Open-Meteo and return processed result."""

    # Round coords to 2 decimal places to improve cache hit rate
    cache_key = f"{round(lat, 2)},{round(lon, 2)}"

    # Check if cache exists and is still valid
    if cache_key in _cache:
        cached = _cache[cache_key]
        if time.time() - cached["timestamp"] < CACHE_TTL:
            # Cache hit — recalculate burn time for requested skin type
            cached["data"]["burn_time_minutes"] = calc_burn_time(
                cached["data"]["uv_index"], skin_type
            )
            cached["data"]["alert_message"] = build_alert_message(
                cached["data"]["uv_index"],
                cached["data"]["burn_time_minutes"]
            )
            return cached["data"]

    # Cache miss — fetch from Open-Meteo
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "uv_index",
        "timezone": "auto",
        "forecast_days": 1,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    # Extract hourly uv_index list
    times = data["hourly"]["time"]        # ["2026-03-13T00:00", ...]
    uv_list = data["hourly"]["uv_index"]  # [0.0, 0.1, 3.2, ...]

    # Get current hour's UV index
    current_hour = datetime.now().hour
    current_uv = uv_list[current_hour]

    # Build hourly forecast (daytime hours 6am–8pm only)
    hourly_forecast = []
    for t, uv in zip(times, uv_list):
        hour = int(t[11:13])  # extract hour from "2026-03-13T08:00"
        if 6 <= hour <= 20:
            level, color, _ = get_uv_level(uv)
            hourly_forecast.append({
                "time": f"{hour}:00",
                "uv_index": round(uv, 1),
                "level": level,
                "color": color,
                "is_current": hour == current_hour,
            })

    # Process current UV
    level, color, spf = get_uv_level(current_uv)
    burn_time = calc_burn_time(current_uv, skin_type)
    alert_msg = build_alert_message(current_uv, burn_time)

    result = {
        "uv_index": round(current_uv, 1),
        "level": level,
        "level_color": color,
        "burn_time_minutes": burn_time,
        "alert_message": alert_msg,
        "spf_recommendation": spf,
        "hourly_forecast": hourly_forecast,
    }

    # Save to cache before returning
    _cache[cache_key] = {
        "timestamp": time.time(),
        "data": result
    }

    return result