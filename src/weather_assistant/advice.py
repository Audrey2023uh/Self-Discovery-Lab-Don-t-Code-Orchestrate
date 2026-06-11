from __future__ import annotations

from weather_assistant.models import Advice, Event, WeatherSnapshot


RAIN_CODES = {
    51,
    53,
    55,
    56,
    57,
    61,
    63,
    65,
    66,
    67,
    80,
    81,
    82,
    95,
    96,
    99,
}
SNOW_CODES = {71, 73, 75, 77, 85, 86}
FOG_CODES = {45, 48}
THUNDERSTORM_CODES = {95, 96, 99}


def is_rainy(weather: WeatherSnapshot) -> bool:
    return weather.weather_code in RAIN_CODES or weather.precipitation_probability >= 50


def is_hot(weather: WeatherSnapshot) -> bool:
    return weather.temperature_f >= 85


def is_cold(weather: WeatherSnapshot) -> bool:
    return weather.temperature_f <= 45


def is_windy(weather: WeatherSnapshot) -> bool:
    return weather.wind_speed_mph >= 25


def synthesize_advice(event: Event, weather: WeatherSnapshot | None) -> Advice:
    if weather is None:
        return Advice(
            summary=f"{event.title}: weather is unavailable, so plan with normal timing.",
            recommendations=[
                "Check the forecast manually before leaving.",
                "Keep a small time buffer because the assistant could not verify conditions.",
            ],
            flags=["weather-unavailable"],
        )

    flags: list[str] = []
    recommendations: list[str] = []

    if is_rainy(weather):
        flags.append("rain")
        recommendations.append("Bring an umbrella or rain jacket.")
        recommendations.append("Consider taking the bus, rideshare, or another covered transit option.")

    if weather.weather_code in THUNDERSTORM_CODES:
        flags.append("storm")
        recommendations.append("Move outdoor parts of this event indoors if possible.")

    if weather.weather_code in SNOW_CODES:
        flags.append("snow")
        recommendations.append("Leave early and wear shoes with good traction.")

    if weather.weather_code in FOG_CODES:
        flags.append("fog")
        recommendations.append("Use extra travel time because visibility may be low.")

    if is_hot(weather):
        flags.append("heat")
        recommendations.append("Carry water and avoid standing outside longer than necessary.")

    if is_cold(weather):
        flags.append("cold")
        recommendations.append("Wear a warm layer before heading out.")

    if is_windy(weather):
        flags.append("wind")
        recommendations.append("Secure loose papers, laptop sleeves, and lightweight bags.")

    if event.duration_minutes >= 90:
        recommendations.append("Pack what you need for a longer block so weather does not force an extra trip.")

    if not recommendations:
        recommendations.append("Weather looks manageable. Keep your normal plan.")

    summary = (
        f"{event.title}: {round(weather.temperature_f)}F, "
        f"{weather.precipitation_probability}% precipitation chance, "
        f"{round(weather.wind_speed_mph)} mph wind near {weather.observed_at.strftime('%I:%M %p')}."
    )

    return Advice(summary=summary, recommendations=recommendations, flags=flags or ["clear"])
