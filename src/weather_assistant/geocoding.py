from __future__ import annotations

import json
from urllib.parse import urlencode
from urllib.request import urlopen

from weather_assistant.models import Location


class GeocodingError(RuntimeError):
    """Raised when a location cannot be resolved to coordinates."""


US_STATE_ALIASES = {
    "alabama": {"alabama", "al"},
    "alaska": {"alaska", "ak"},
    "arizona": {"arizona", "az"},
    "arkansas": {"arkansas", "ar"},
    "california": {"california", "ca"},
    "colorado": {"colorado", "co"},
    "connecticut": {"connecticut", "ct"},
    "delaware": {"delaware", "de"},
    "florida": {"florida", "fl"},
    "georgia": {"georgia", "ga"},
    "hawaii": {"hawaii", "hi"},
    "idaho": {"idaho", "id"},
    "illinois": {"illinois", "il"},
    "indiana": {"indiana", "in"},
    "iowa": {"iowa", "ia"},
    "kansas": {"kansas", "ks"},
    "kentucky": {"kentucky", "ky"},
    "louisiana": {"louisiana", "la"},
    "maine": {"maine", "me"},
    "maryland": {"maryland", "md"},
    "massachusetts": {"massachusetts", "ma"},
    "michigan": {"michigan", "mi"},
    "minnesota": {"minnesota", "mn"},
    "mississippi": {"mississippi", "ms"},
    "missouri": {"missouri", "mo"},
    "montana": {"montana", "mt"},
    "nebraska": {"nebraska", "ne"},
    "nevada": {"nevada", "nv"},
    "new hampshire": {"new hampshire", "nh"},
    "new jersey": {"new jersey", "nj"},
    "new mexico": {"new mexico", "nm"},
    "new york": {"new york", "ny"},
    "north carolina": {"north carolina", "nc"},
    "north dakota": {"north dakota", "nd"},
    "ohio": {"ohio", "oh"},
    "oklahoma": {"oklahoma", "ok"},
    "oregon": {"oregon", "or"},
    "pennsylvania": {"pennsylvania", "pa"},
    "rhode island": {"rhode island", "ri"},
    "south carolina": {"south carolina", "sc"},
    "south dakota": {"south dakota", "sd"},
    "tennessee": {"tennessee", "tn"},
    "texas": {"texas", "tx"},
    "utah": {"utah", "ut"},
    "vermont": {"vermont", "vt"},
    "virginia": {"virginia", "va"},
    "washington": {"washington", "wa"},
    "west virginia": {"west virginia", "wv"},
    "wisconsin": {"wisconsin", "wi"},
    "wyoming": {"wyoming", "wy"},
}


COUNTRY_ALIASES = {
    "united states": {"united states", "us", "usa", "u.s.", "u.s.a."},
    "united kingdom": {"united kingdom", "gb", "uk", "great britain"},
}


class OpenMeteoGeocoder:
    base_url = "https://geocoding-api.open-meteo.com/v1/search"

    def lookup(self, location_name: str) -> Location:
        location_name = location_name.strip()
        if not location_name:
            raise GeocodingError("Location name cannot be blank")

        attempted_queries: list[str] = []
        all_results: list[dict] = []

        for search_term in search_terms_for(location_name):
            attempted_queries.append(search_term)
            results = self._fetch_results(search_term)
            all_results.extend(results)

            match = best_result_for(location_name, results)
            if match is not None:
                return location_from_result(match, location_name)

        if all_results:
            return location_from_result(all_results[0], location_name)

        attempted = ", ".join(attempted_queries)
        raise GeocodingError(f"Could not find coordinates for {location_name} using: {attempted}")

    def _fetch_results(self, search_term: str) -> list[dict]:
        query = urlencode({"name": search_term, "count": 10, "language": "en", "format": "json"})
        url = f"{self.base_url}?{query}"

        with urlopen(url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))

        return payload.get("results") or []


def search_terms_for(location_name: str) -> list[str]:
    pieces = split_location(location_name)
    terms = [location_name]
    if pieces and pieces[0] != location_name:
        terms.append(pieces[0])
    return unique_preserving_order(terms)


def split_location(location_name: str) -> list[str]:
    return [piece.strip() for piece in location_name.split(",") if piece.strip()]


def best_result_for(location_name: str, results: list[dict]) -> dict | None:
    if not results:
        return None

    pieces = split_location(location_name)
    city = normalize(pieces[0]) if pieces else normalize(location_name)
    qualifiers = qualifier_aliases(pieces[1:])

    exact_city_results = [result for result in results if normalize(result.get("name", "")) == city]
    candidates = exact_city_results or results

    if qualifiers:
        for result in candidates:
            if result_matches_qualifiers(result, qualifiers):
                return result
        return None

    return candidates[0]


def result_matches_qualifiers(result: dict, qualifiers: set[str]) -> bool:
    result_values = {
        normalize(result.get("admin1", "")),
        normalize(result.get("admin2", "")),
        normalize(result.get("country", "")),
        normalize(result.get("country_code", "")),
    }
    return bool(result_values & qualifiers)


def qualifier_aliases(raw_qualifiers: list[str]) -> set[str]:
    aliases: set[str] = set()
    for raw_value in raw_qualifiers:
        normalized = normalize(raw_value)
        aliases.add(normalized)

        for state_aliases in US_STATE_ALIASES.values():
            if normalized in state_aliases:
                aliases.update(state_aliases)

        for country_aliases in COUNTRY_ALIASES.values():
            if normalized in country_aliases:
                aliases.update(country_aliases)

    return aliases


def location_from_result(result: dict, fallback_name: str) -> Location:
    display_name = result.get("name", fallback_name)
    admin = result.get("admin1")
    country = result.get("country")
    pieces = [piece for piece in [display_name, admin, country] if piece]

    return Location(
        name=", ".join(pieces),
        latitude=float(result["latitude"]),
        longitude=float(result["longitude"]),
    )


def normalize(value: str) -> str:
    return " ".join(value.strip().lower().replace(".", "").split())


def unique_preserving_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        normalized = normalize(value)
        if normalized not in seen:
            seen.add(normalized)
            unique.append(value)
    return unique
