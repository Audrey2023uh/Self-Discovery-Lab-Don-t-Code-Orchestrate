from __future__ import annotations

from datetime import datetime
from pathlib import Path

from weather_assistant.advice import synthesize_advice
from weather_assistant.formatting import format_advice, format_event
from weather_assistant.models import Advice, Event, WeatherSnapshot
from weather_assistant.schedule import ScheduleError, events_on_day, load_schedule
from weather_assistant.weather import OpenMeteoWeatherClient, WeatherError


COMMANDS = """
Commands:
  today          Show weather-aware advice for today's events
  schedule       Show all events from calendar.json
  event <num>    Show advice for one event number
  reload         Reload calendar.json
  help           Show this help message
  quit           Exit the assistant
""".strip()


class AssistantApp:
    def __init__(self, project_root: Path, weather_client: OpenMeteoWeatherClient | None = None):
        self.project_root = project_root
        self.calendar_path = project_root / "calendar.json"
        self.weather_client = weather_client or OpenMeteoWeatherClient()
        self.events: list[Event] = []

    def reload(self) -> str:
        self.events = load_schedule(self.calendar_path)
        return f"Loaded {len(self.events)} event(s) from {self.calendar_path.name}."

    def list_schedule(self) -> str:
        if not self.events:
            return "No events found."
        return "\n".join(format_event(index + 1, event) for index, event in enumerate(self.events))

    def build_advice(self, event: Event) -> Advice:
        weather = self._safe_weather(event)
        return synthesize_advice(event, weather)

    def advice_for_event(self, event: Event) -> str:
        return format_advice(self.build_advice(event))

    def today(self, now: datetime | None = None) -> str:
        today = now or datetime.now()
        todays_events = events_on_day(self.events, today)
        if not todays_events:
            return "No events found for today."
        return "\n\n".join(self.advice_for_event(event) for event in todays_events)

    def handle(self, command: str) -> str:
        command = command.strip()
        if command == "help":
            return COMMANDS
        if command == "schedule":
            return self.list_schedule()
        if command == "today":
            return self.today()
        if command == "reload":
            return self.reload()
        if command.startswith("event "):
            return self._handle_event_command(command)
        return "Unknown command. Type 'help' to see available commands."

    def _handle_event_command(self, command: str) -> str:
        raw_index = command.removeprefix("event ").strip()
        if not raw_index.isdigit():
            return "Use the format: event <number>"

        event_index = int(raw_index) - 1
        if event_index < 0 or event_index >= len(self.events):
            return f"Event number must be between 1 and {len(self.events)}."

        return self.advice_for_event(self.events[event_index])

    def _safe_weather(self, event: Event) -> WeatherSnapshot | None:
        try:
            return self.weather_client.weather_for(event.location, event.start)
        except (OSError, WeatherError, RuntimeError) as exc:
            print(f"Weather lookup failed for {event.location}: {exc}")
            return None


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    app = AssistantApp(project_root)

    print("Weather-Aware Personal Assistant")
    print(COMMANDS)
    try:
        print(app.reload())
    except ScheduleError as exc:
        print(f"Could not load schedule: {exc}")
        return

    while True:
        command = input("\nassistant> ").strip()
        if command in {"quit", "exit"}:
            print("Goodbye.")
            return
        print(app.handle(command))
