# Weather-Aware Personal Assistant

**By:** Audrey Rah
**Course:** EDS6397 – Generative AI and Applications
#**University:** University of Houston

**Assignment:** Self Discovery Lab: Don't Code, Orchestrate

A CLI-based personal assistant that reads a local schedule, checks public weather data from Open-Meteo, and gives rule-based advice for each event. It also includes an optional browser UI for easier demonstration.



## How To Run

```bash
python main.py
```

Useful REPL commands:

- `today` - show today's weather-aware agenda.
- `schedule` - show every event in `calendar.json`.
- `event 1` - get advice for one numbered event.
- `reload` - reload `calendar.json` after edits.
- `help` - show commands.
- `quit` - exit.

## Optional Browser UI

```bash
python web_app.py
```

Then open:

```text
http://127.0.0.1:8000
```

The browser UI loads `calendar.json`, lists events, and lets you click an event to generate weather-aware advice.

## How To Test

```bash
python -m unittest discover -s tests
```

The tests focus on the guardrail logic: schedule validation, weather classification, and whether rainy weather produces transit/umbrella recommendations.

## Project Structure

```text
.
├── calendar.json
├── docs/
│   └── rules.md
├── main.py
├── specs/
│   └── PRD.md
├── src/
│   └── weather_assistant/
│       ├── advice.py
│       ├── cli.py
│       ├── formatting.py
│       ├── geocoding.py
│       ├── models.py
│       ├── schedule.py
│       ├── weather.py
│       └── web.py
├── web_app.py
└── tests/
    ├── test_advice.py
    ├── test_cli.py
    ├── test_geocoding.py
    ├── test_schedule.py
    └── test_weather.py
```

## Vibe Report

**Where did the AI's vibe drift?**  
The first design instinct was to make the assistant too broad, with reminders, productivity scoring, and general life-coach responses. I steered it back to the assignment's intent: weather plus local schedule plus practical advice. The final app keeps the weather API separate from the REPL so the system feels like a professional tool instead of one large script.

**When did I use the Builder Hammer?**  
I used the Builder Hammer around the advice rules. The AI originally treated rain as only "bring an umbrella," but the rubric example specifically asks for logic like suggesting a bus when it is raining. I tightened that behavior into a testable rule: rainy forecasts must recommend umbrella protection and a transit-friendly option.

**Most successful steering prompt:**  
"Build this as an architected CLI assistant, not a single script. Keep API access, schedule parsing, advice rules, and display formatting in separate small files. Use a rule-based synthesizer and write tests that prove rain changes the recommendation."

## Design Notes

This project uses a rule-based synthesizer instead of an LLM so that the behavior is deterministic, testable, and easy for peers to grade. The weather source is Open-Meteo, which does not require an API key.
