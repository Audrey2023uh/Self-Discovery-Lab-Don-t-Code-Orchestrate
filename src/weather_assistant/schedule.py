from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from weather_assistant.models import Event


REQUIRED_EVENT_FIELDS = {"title", "start", "end", "location"}


class ScheduleError(ValueError):
    """Raised when calendar.json cannot be loaded as a valid schedule."""


def parse_datetime(value: str) -> datetime:
    try:
        normalized = value.replace("Z", "+00:00")
        return datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise ScheduleError(f"Invalid datetime value: {value}") from exc


def event_from_dict(raw_event: dict, index: int) -> Event:
    missing = REQUIRED_EVENT_FIELDS - set(raw_event)
    if missing:
        missing_fields = ", ".join(sorted(missing))
        raise ScheduleError(f"Event {index} is missing required field(s): {missing_fields}")

    title = str(raw_event["title"]).strip()
    location = str(raw_event["location"]).strip()
    start = parse_datetime(str(raw_event["start"]))
    end = parse_datetime(str(raw_event["end"]))

    if not title:
        raise ScheduleError(f"Event {index} title cannot be blank")
    if not location:
        raise ScheduleError(f"Event {index} location cannot be blank")
    if end <= start:
        raise ScheduleError(f"Event {index} end must be after start")

    return Event(title=title, start=start, end=end, location=location)


def load_schedule(path: Path) -> list[Event]:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ScheduleError(f"Schedule file not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ScheduleError(f"Schedule file is not valid JSON: {path}") from exc

    if not isinstance(raw, list):
        raise ScheduleError("Schedule must be a list of events")

    events = [event_from_dict(item, index + 1) for index, item in enumerate(raw)]
    return sorted(events, key=lambda event: event.start)


def events_on_day(events: Iterable[Event], day: datetime) -> list[Event]:
    return [event for event in events if event.start.date() == day.date()]
