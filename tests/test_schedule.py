import json
from pathlib import Path
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from weather_assistant.schedule import ScheduleError, load_schedule


class ScheduleTests(unittest.TestCase):
    def write_calendar(self, payload: object) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        path = Path(temp_dir.name) / "calendar.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return path

    def test_load_schedule_sorts_events_by_start_time(self) -> None:
        path = self.write_calendar(
            [
                {
                    "title": "Afternoon Meeting",
                    "start": "2026-06-10T13:00:00",
                    "end": "2026-06-10T14:00:00",
                    "location": "Denton, Texas",
                },
                {
                    "title": "Morning Lab",
                    "start": "2026-06-10T09:00:00",
                    "end": "2026-06-10T10:00:00",
                    "location": "Denton, Texas",
                },
            ]
        )

        events = load_schedule(path)

        self.assertEqual([event.title for event in events], ["Morning Lab", "Afternoon Meeting"])

    def test_missing_required_field_raises_schedule_error(self) -> None:
        path = self.write_calendar(
            [
                {
                    "title": "Broken Event",
                    "start": "2026-06-10T09:00:00",
                    "end": "2026-06-10T10:00:00",
                }
            ]
        )

        with self.assertRaises(ScheduleError):
            load_schedule(path)

    def test_end_must_be_after_start(self) -> None:
        path = self.write_calendar(
            [
                {
                    "title": "Broken Event",
                    "start": "2026-06-10T10:00:00",
                    "end": "2026-06-10T09:00:00",
                    "location": "Denton, Texas",
                }
            ]
        )

        with self.assertRaises(ScheduleError):
            load_schedule(path)


if __name__ == "__main__":
    unittest.main()
