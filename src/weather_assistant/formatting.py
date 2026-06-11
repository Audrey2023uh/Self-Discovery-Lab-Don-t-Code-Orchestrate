from __future__ import annotations

from weather_assistant.models import Advice, Event


def format_event(index: int, event: Event) -> str:
    start = event.start.strftime("%a %b %d, %I:%M %p")
    end = event.end.strftime("%I:%M %p")
    return f"{index}. {event.title} | {start}-{end} | {event.location}"


def format_advice(advice: Advice) -> str:
    lines = [advice.summary]
    for recommendation in advice.recommendations:
        lines.append(f"  - {recommendation}")
    return "\n".join(lines)
