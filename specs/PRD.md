# Product Requirements Document

## Product Name

Weather-Aware Personal Assistant

## Mission

Build a command-line personal assistant that reads a student's local schedule, checks the weather for each event location, and synthesizes practical advice before the student leaves. Include a lightweight browser UI for demonstration while preserving the assignment-required CLI REPL.

The app should prove the "Don't Code, Orchestrate" idea by using a professional multi-file structure with clear boundaries between user interface, schedule parsing, weather API access, and advice logic.

## Target User

A student who wants quick, practical planning help from the terminal or a simple browser page before classes, labs, meetings, and study sessions.

## Core User Story

As a student, I want to load my calendar and ask for weather-aware advice so that I know whether to bring rain gear, leave early, choose transit, or adjust my plan.

## Functional Requirements

1. The assistant must run as a CLI REPL.
2. The assistant must load events from a local `calendar.json` file.
3. Each event must include `title`, `start`, `end`, and `location`.
4. The assistant must fetch weather data from a public API.
5. The assistant must synthesize advice using deterministic rules.
6. The assistant must include commands for schedule viewing, today's events, one-event advice, reloading the schedule, help, and quit.
7. The assistant must include an optional browser UI that lists events and generates advice.
8. The assistant must keep logic separate from print/UI code.
9. The app must include automated tests for the core rules.

## Non-Goals

1. The app does not need account login.
2. The app does not need to write back to a calendar provider.
3. The app does not need account-based personalization.
4. The app does not need an LLM because deterministic rules are easier to test for this assignment.

## Data Source

Weather data comes from Open-Meteo:

- Geocoding API: resolves event locations into latitude and longitude.
- Forecast API: returns hourly temperature, precipitation probability, weather code, and wind speed.

Open-Meteo was chosen because it is public and does not require an API key.

## Advice Rules

The advice engine must return both a summary and recommendations.

Rain rule:

- If the weather code is rainy or precipitation probability is at least 50%, recommend an umbrella or rain jacket.
- If rainy, recommend taking the bus, rideshare, or another covered transit option.

Storm rule:

- If the weather code is thunderstorm-related, recommend moving outdoor parts indoors.

Snow rule:

- If the weather code is snow-related, recommend leaving early and wearing traction-friendly shoes.

Fog rule:

- If the weather code is fog-related, recommend extra travel time.

Heat rule:

- If temperature is at least 85F, recommend water and reducing unnecessary outdoor waiting.

Cold rule:

- If temperature is 45F or below, recommend warm layers.

Wind rule:

- If wind speed is at least 25 mph, recommend securing lightweight items.

Long event rule:

- If an event lasts at least 90 minutes, recommend packing what is needed for a longer block.

Fallback rule:

- If no weather concerns are found, say that weather looks manageable.
- If weather is unavailable, tell the user to manually check the forecast and keep a time buffer.

## Acceptance Criteria

1. `python main.py` starts the assistant.
2. The assistant loads `calendar.json`.
3. `schedule` lists local events.
4. `today` generates weather-aware advice for today's events.
5. `event <num>` generates advice for a selected event.
6. Rainy weather produces umbrella and transit recommendations.
7. `python web_app.py` starts the optional browser UI at `http://127.0.0.1:8000`.
8. Tests can be run with `python -m unittest discover -s tests`.

## Architecture

The app is intentionally modular:

- `cli.py` owns the REPL and command routing.
- `schedule.py` owns calendar loading and validation.
- `geocoding.py` owns location lookup.
- `weather.py` owns Open-Meteo forecast access and hourly forecast selection.
- `advice.py` owns rule-based synthesis.
- `formatting.py` owns display strings.
- `web.py` owns the optional browser UI and JSON endpoints.
- `models.py` owns shared dataclasses.

## Risks

1. Public API calls can fail because of network outages or invalid locations.
2. Free API responses can change over time.
3. Local event dates must be kept current for `today` to show events.

## Testing Strategy

Automated tests should prove the most important logic without depending on live network calls:

- Schedule parsing validates fields and event order.
- Rain advice recommends umbrella and transit.
- Clear weather produces a normal-plan recommendation.
- Weather forecast parsing selects the nearest hourly forecast.
