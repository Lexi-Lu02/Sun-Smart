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

    # Cache miss — fetch from Open-Meteo (UV, temperature, cloud cover)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "uv_index,temperature_2m,apparent_temperature,cloud_cover",
        "timezone": "auto",
        "forecast_days": 1,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

    # Extract hourly lists
    times = data["hourly"]["time"]
    uv_list = data["hourly"]["uv_index"]
    temp_list = data["hourly"].get("temperature_2m", [0] * len(times))
    feels_list = data["hourly"].get("apparent_temperature", temp_list)
    cloud_list = data["hourly"].get("cloud_cover", [0] * len(times))

    # Get current hour index (use first 24h)
    now = datetime.now()
    current_hour = now.hour
    current_uv = uv_list[current_hour] if current_hour < len(uv_list) else (uv_list[0] if uv_list else 0)
    current_temp = temp_list[current_hour] if current_hour < len(temp_list) else None
    current_feels = feels_list[current_hour] if current_hour < len(feels_list) else current_temp
    current_cloud = cloud_list[current_hour] if current_hour < len(cloud_list) else None

    # Peak UV: hour (0-23) with max UV in daytime 6–20
    peak_uv_val = 0.0
    peak_uv_hour = 12
    for i, (t, uv) in enumerate(zip(times, uv_list)):
        hour = int(t[11:13]) if len(t) >= 13 else i
        if 6 <= hour <= 20 and uv > peak_uv_val:
            peak_uv_val = uv
            peak_uv_hour = hour

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

    # Peak UV time string e.g. "1–3 PM"
    peak_end = min(peak_uv_hour + 2, 20)
    h1 = peak_uv_hour % 12 or 12
    h2 = peak_end % 12 or 12
    ampm = "PM" if peak_uv_hour >= 12 else "AM"
    peak_uv_time = f"{h1}–{h2} {ampm}"

    result = {
        "uv_index": round(current_uv, 1),
        "level": level,
        "level_color": color,
        "burn_time_minutes": burn_time,
        "alert_message": alert_msg,
        "spf_recommendation": spf,
        "hourly_forecast": hourly_forecast,
        "current_temp": round(current_temp, 1) if current_temp is not None else None,
        "feels_like": round(current_feels, 1) if current_feels is not None else None,
        "cloud_cover": int(round(current_cloud)) if current_cloud is not None else None,
        "peak_uv_time": peak_uv_time,
        "peak_uv_hour": peak_uv_hour,
    }

    # Save to cache before returning
    _cache[cache_key] = {
        "timestamp": time.time(),
        "data": result
    }

    return result