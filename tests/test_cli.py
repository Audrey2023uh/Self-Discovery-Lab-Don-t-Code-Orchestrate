from datetime import datetime
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from weather_assistant.cli import AssistantApp
from weather_assistant.models import Event, WeatherSnapshot


class FakeWeatherClient:
    def weather_for(self, location_name: str, event_start: datetime) -> WeatherSnapshot:
        return WeatherSnapshot(
            temperature_f=71,
            precipitation_probability=75,
            weather_code=61,
            wind_speed_mph=9,
            observed_at=event_start,
        )


class AssistantAppTests(unittest.TestCase):
    def test_build_advice_returns_structured_advice(self) -> None:
        app = AssistantApp(PROJECT_ROOT, weather_client=FakeWeatherClient())
        event = Event(
            title="Lab",
            start=datetime(2026, 6, 10, 9, 0),
            end=datetime(2026, 6, 10, 10, 0),
            location="Denton, Texas",
        )

        advice = app.build_advice(event)

        self.assertIn("rain", advice.flags)
        self.assertTrue(any("bus" in item.lower() for item in advice.recommendations))

    def test_event_command_uses_weather_advice_not_fallback(self) -> None:
        app = AssistantApp(PROJECT_ROOT, weather_client=FakeWeatherClient())
        app.events = [
            Event(
                title="Lab",
                start=datetime(2026, 6, 10, 9, 0),
                end=datetime(2026, 6, 10, 10, 0),
                location="Denton, Texas",
            )
        ]

        output = app.handle("event 1")

        self.assertIn("75% precipitation chance", output)
        self.assertIn("bus", output.lower())
        self.assertNotIn("weather is unavailable", output.lower())

    def test_today_command_uses_weather_advice_not_fallback(self) -> None:
        app = AssistantApp(PROJECT_ROOT, weather_client=FakeWeatherClient())
        app.events = [
            Event(
                title="Lab",
                start=datetime(2026, 6, 10, 9, 0),
                end=datetime(2026, 6, 10, 10, 0),
                location="Denton, Texas",
            )
        ]

        output = app.today(now=datetime(2026, 6, 10, 8, 0))

        self.assertIn("75% precipitation chance", output)
        self.assertIn("bus", output.lower())
        self.assertNotIn("weather is unavailable", output.lower())


if __name__ == "__main__":
    unittest.main()
