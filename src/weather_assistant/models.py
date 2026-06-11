from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Event:
    title: str
    start: datetime
    end: datetime
    location: str

    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() // 60)


@dataclass(frozen=True)
class Location:
    name: str
    latitude: float
    longitude: float


@dataclass(frozen=True)
class WeatherSnapshot:
    temperature_f: float
    precipitation_probability: int
    weather_code: int
    wind_speed_mph: float
    observed_at: datetime


@dataclass(frozen=True)
class Advice:
    summary: str
    recommendations: list[str]
    flags: list[str]
