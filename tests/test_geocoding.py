from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from weather_assistant.geocoding import OpenMeteoGeocoder, best_result_for, search_terms_for


DENTON_RESULTS = [
    {
        "name": "Denton",
        "latitude": 33.21484,
        "longitude": -97.13307,
        "country": "United States",
        "country_code": "US",
        "admin1": "Texas",
        "admin2": "Denton",
    },
    {
        "name": "Denton",
        "latitude": 38.88456,
        "longitude": -75.82716,
        "country": "United States",
        "country_code": "US",
        "admin1": "Maryland",
        "admin2": "Caroline",
    },
]


class FakeGeocoder(OpenMeteoGeocoder):
    def __init__(self) -> None:
        self.searches: list[str] = []

    def _fetch_results(self, search_term: str) -> list[dict]:
        self.searches.append(search_term)
        if search_term == "Denton, Texas":
            return []
        if search_term == "Denton":
            return DENTON_RESULTS
        return []


class GeocodingTests(unittest.TestCase):
    def test_search_terms_include_city_fallback(self) -> None:
        self.assertEqual(search_terms_for("Denton, Texas"), ["Denton, Texas", "Denton"])

    def test_best_result_uses_state_qualifier(self) -> None:
        result = best_result_for("Denton, TX", list(reversed(DENTON_RESULTS)))

        self.assertIsNotNone(result)
        self.assertEqual(result["admin1"], "Texas")

    def test_lookup_falls_back_to_city_and_resolves_denton_texas(self) -> None:
        geocoder = FakeGeocoder()

        location = geocoder.lookup("Denton, Texas")

        self.assertEqual(geocoder.searches, ["Denton, Texas", "Denton"])
        self.assertEqual(location.name, "Denton, Texas, United States")
        self.assertAlmostEqual(location.latitude, 33.21484)
        self.assertAlmostEqual(location.longitude, -97.13307)


if __name__ == "__main__":
    unittest.main()
