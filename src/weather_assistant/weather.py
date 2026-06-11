from __future__ import annotations

import json
from datetime import datetime
from urllib.parse import urlencode
from urllib.request import urlopen

from weather_assistant.geocoding import OpenMeteoGeocoder
from weather_assistant.models import Location, WeatherSnapshot


class WeatherError(RuntimeError):
    """Raised when weather data cannot be fetched or interpreted."""


class OpenMeteoWeatherClient:
    base_url = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, geocoder: OpenMeteoGeocoder | None = None):
        self.geocoder = geocoder or OpenMeteoGeocoder()

    def weather_for(self, location_name: str, event_start: datetime) -> WeatherSnapshot:
        location = self.geocoder.lookup(location_name)
        return self.weather_for_coordinates(location, event_start)

    def weather_for_coordinates(self, location: Location, event_start: datetime) -> WeatherSnapshot:
        query = urlencode(
            {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "hourly": "temperature_2m,precipitation_probability,weather_code,wind_speed_10m",
                "temperature_unit": "fahrenheit",
                "wind_speed_unit": "mph",
                "timezone": "auto",
                "forecast_days": 7,
            }
        )
        url = f"{self.base_url}?{query}"

        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        return snapshot_nearest_to(payload, event_start)


def snapshot_nearest_to(payload: dict, target: datetime) -> WeatherSnapshot:
    hourly = payload.get("hourly") or {}
    times = hourly.get("time") or []
    temperatures = hourly.get("temperature_2m") or []
    precipitation = hourly.get("precipitation_probability") or []
    weather_codes = hourly.get("weather_code") or []
    wind_speeds = hourly.get("wind_speed_10m") or []

    if not times:
        raise WeatherError("Weather response did not include hourly forecast times")

    parsed_times = [datetime.fromisoformat(value) for value in times]
    nearest_index = min(
        range(len(parsed_times)),
        key=lambda index: abs((parsed_times[index] - target.replace(tzinfo=None)).total_seconds()),
    )

    try:
        return WeatherSnapshot(
            temperature_f=float(temperatures[nearest_index]),
            precipitation_probability=int(precipitation[nearest_index]),
            weather_code=int(weather_codes[nearest_index]),
            wind_speed_mph=float(wind_speeds[nearest_index]),
            observed_at=parsed_times[nearest_index],
        )
    except (IndexError, TypeError, ValueError) as exc:
        raise WeatherError("Weather response is missing expected hourly values") from exc
