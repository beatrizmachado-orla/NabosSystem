# "48f18508-f04b-11f0-a8f4-0242ac130003-48f1856c-f04b-11f0-a8f4-0242ac130003"
import os
import requests
from datetime import datetime, timezone as dt_timezone

BASE_URL = "https://api.stormglass.io/v2/weather/point"

DEFAULT_PARAMS = [
    "windSpeed", "windDirection", "gust",
    "waveHeight", "waveDirection", "wavePeriod",
    "swellHeight", "swellDirection", "swellPeriod",
    "waterTemperature",
    "airTemperature",
]


def _pick_first_source(value_obj: dict):
    if not isinstance(value_obj, dict):
        return None

    priority = ["noaa", "meteo", "dwd", "smhi", "sg"]
    for src in priority:
        if src in value_obj and value_obj[src] is not None:
            return value_obj[src]

    for _, v in value_obj.items():
        if v is not None:
            return v
    return None


def fetch_point_weather(lat: float, lng: float, start_ts: int, end_ts: int, params=None, sources=None):
    api_key = "48f18508-f04b-11f0-a8f4-0242ac130003-48f1856c-f04b-11f0-a8f4-0242ac130003"
    if not api_key:
        raise RuntimeError("STORMGLASS_API_KEY não definido no ambiente")

    params_list = params or DEFAULT_PARAMS

    query = {
        "lat": lat,
        "lng": lng,
        "params": ",".join(params_list),
        "start": start_ts,
        "end": end_ts,
    }

    if sources:
        query["source"] = ",".join(sources) if isinstance(sources, (list, tuple)) else str(sources)

    response = requests.get(
        BASE_URL,
        params=query,
        headers={"Authorization": api_key},
        timeout=20,
    )
    response.raise_for_status()
    return response.json()


def normalize_hours(payload: dict):
    hours = payload.get("hours", [])
    out = []

    for h in hours:
        out.append({
            "time": h.get("time"),
            "air_temp": _pick_first_source(h.get("airTemperature")),
            "water_temp": _pick_first_source(h.get("waterTemperature")),
            "wind_speed": _pick_first_source(h.get("windSpeed")),
            "wind_dir": _pick_first_source(h.get("windDirection")),
            "gust": _pick_first_source(h.get("gust")),
            "wave_h": _pick_first_source(h.get("waveHeight")),
            "wave_dir": _pick_first_source(h.get("waveDirection")),
            "wave_period": _pick_first_source(h.get("wavePeriod")),
            "swell_h": _pick_first_source(h.get("swellHeight")),
            "swell_dir": _pick_first_source(h.get("swellDirection")),
            "swell_period": _pick_first_source(h.get("swellPeriod")),
        })

    return out


def utc_day_window_for_today():
    now = datetime.now(dt_timezone.utc)
    start = datetime(now.year, now.month, now.day, 0, 0, 0, tzinfo=dt_timezone.utc)
    end = datetime(now.year, now.month, now.day, 23, 59, 59, tzinfo=dt_timezone.utc)
    return start, end
