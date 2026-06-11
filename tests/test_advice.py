from datetime import datetime
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from weather_assistant.advice import synthesize_advice
from weather_assistant.models import Event, WeatherSnapshot


class AdviceTests(unittest.TestCase):
    def make_event(self) -> Event:
        return Event(
            title="FPGA Lab",
            start=datetime(2026, 6, 10, 9, 0),
            end=datetime(2026, 6, 10, 10, 30),
            location="Denton, Texas",
        )

    def test_rainy_weather_recommends_umbrella_and_transit(self) -> None:
        weather = WeatherSnapshot(
            temperature_f=72,
            precipitation_probability=80,
            weather_code=61,
            wind_speed_mph=12,
            observed_at=datetime(2026, 6, 10, 9, 0),
        )

        advice = synthesize_advice(self.make_event(), weather)
        text = " ".join(advice.recommendations).lower()

        self.assertIn("rain", advice.flags)
        self.assertTrue("umbrella" in text or "rain jacket" in text)
        self.assertTrue("bus" in text or "rideshare" in text or "transit" in text)

    def test_clear_weather_keeps_normal_plan(self) -> None:
        weather = WeatherSnapshot(
            temperature_f=70,
            precipitation_probability=5,
            weather_code=0,
            wind_speed_mph=6,
            observed_at=datetime(2026, 6, 10, 9, 0),
        )

        advice = synthesize_advice(self.make_event(), weather)

        self.assertEqual(advice.flags, ["clear"])
        self.assertIn("longer block", advice.recommendations[0].lower())
        self.assertNotIn("umbrella", " ".join(advice.recommendations).lower())

    def test_unavailable_weather_uses_fallback(self) -> None:
        advice = synthesize_advice(self.make_event(), None)

        self.assertEqual(advice.flags, ["weather-unavailable"])
        self.assertIn("Check the forecast manually", advice.recommendations[0])


if __name__ == "__main__":
    unittest.main()
