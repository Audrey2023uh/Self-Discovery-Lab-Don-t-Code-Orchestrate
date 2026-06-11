from datetime import datetime
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from weather_assistant.weather import snapshot_nearest_to


class WeatherTests(unittest.TestCase):
    def test_snapshot_nearest_to_selects_closest_hour(self) -> None:
        payload = {
            "hourly": {
                "time": [
                    "2026-06-10T08:00",
                    "2026-06-10T09:00",
                    "2026-06-10T10:00",
                ],
                "temperature_2m": [68.0, 70.0, 72.0],
                "precipitation_probability": [10, 20, 80],
                "weather_code": [0, 2, 61],
                "wind_speed_10m": [5.0, 7.0, 12.0],
            }
        }

        snapshot = snapshot_nearest_to(payload, datetime(2026, 6, 10, 9, 20))

        self.assertEqual(snapshot.temperature_f, 70.0)
        self.assertEqual(snapshot.precipitation_probability, 20)
        self.assertEqual(snapshot.weather_code, 2)
        self.assertEqual(snapshot.wind_speed_mph, 7.0)


if __name__ == "__main__":
    unittest.main()
