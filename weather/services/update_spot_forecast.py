from django.utils import timezone
from weather.models import ForecastHour, StormglassRequestLog
from weather.services.stormglass import (
    fetch_point_weather,
    normalize_hours,
    utc_day_window_for_today,
)


def update_spot_forecast(spot):

    start, end = utc_day_window_for_today()

    payload = fetch_point_weather(
        lat=spot.latitude,
        lng=spot.longitude,
        start_ts=int(start.timestamp()),
        end_ts=int(end.timestamp()),
    )

    hours = normalize_hours(payload)
    created_count = 0

    for h in hours:
        obj, created = ForecastHour.objects.update_or_create(
            spot=spot,
            time=h["time"],
            defaults={
                "wave_height_m": h["wave_h"],
                "wave_period_s": h["wave_period"],
                "wave_direction_deg": h["wave_dir"],
                "swell_height_m": h["swell_h"],
                "swell_period_s": h["swell_period"],
                "swell_direction_deg": h["swell_dir"],
                "wind_speed_ms": h["wind_speed"],
                "wind_direction_deg": h["wind_dir"],
                "water_temp_c": h["water_temp"],
                "air_temp_c": h["air_temp"],
                "source": "stormglass",
            },
        )
        if created:
            created_count += 1

    StormglassRequestLog.objects.create(
        spot=spot,
        status_code=200,
        request_count=1,
        daily_quota=10,
    )

    spot.last_forecast_update = timezone.now()
    spot.save(update_fields=["last_forecast_update"])

    return created_count
