from __future__ import annotations

import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from weather_assistant.cli import AssistantApp
from weather_assistant.models import Advice, Event
from weather_assistant.schedule import ScheduleError


HOST = "127.0.0.1"
PORT = 8000


HTML_PAGE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Weather-Aware Personal Assistant</title>
  <style>
    :root {
      color-scheme: light;
      font-family: Arial, sans-serif;
      --blue: #2563eb;
      --ink: #172033;
      --muted: #5f6b7a;
      --card: #ffffff;
      --page: #eef4ff;
      --line: #d6e0f0;
    }
    body {
      background: var(--page);
      color: var(--ink);
      margin: 0;
      padding: 32px;
    }
    main {
      max-width: 980px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 24px;
    }
    h1 {
      margin-bottom: 8px;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .card {
      background: var(--card);
      border: 1px solid var(--line);
      border-radius: 16px;
      box-shadow: 0 12px 30px rgba(37, 99, 235, 0.10);
      padding: 18px;
    }
    button {
      background: var(--blue);
      border: 0;
      border-radius: 999px;
      color: white;
      cursor: pointer;
      font-weight: 700;
      padding: 10px 14px;
    }
    button.secondary {
      background: #334155;
    }
    .event {
      border: 1px solid var(--line);
      border-radius: 12px;
      margin: 12px 0;
      padding: 12px;
    }
    .muted {
      color: var(--muted);
    }
    .recommendation {
      background: #f8fbff;
      border-left: 4px solid var(--blue);
      margin: 8px 0;
      padding: 8px 10px;
    }
    .error {
      color: #b91c1c;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Weather-Aware Personal Assistant</h1>
      <p class="muted">Loads calendar.json, checks Open-Meteo, and gives planning advice.</p>
      <button onclick="loadSchedule()">Load Schedule</button>
      <button class="secondary" onclick="loadToday()">Today Advice</button>
    </header>
    <section class="grid">
      <div class="card">
        <h2>Schedule</h2>
        <div id="schedule">Click Load Schedule.</div>
      </div>
      <div class="card">
        <h2>Advice</h2>
        <div id="advice">Choose an event or click Today Advice.</div>
      </div>
    </section>
  </main>
  <script>
    async function fetchJson(url) {
      const response = await fetch(url);
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.error || 'Request failed');
      }
      return payload;
    }

    function eventHtml(event) {
      return `
        <div class="event">
          <strong>${event.index}. ${event.title}</strong>
          <div class="muted">${event.start} to ${event.end}</div>
          <div>${event.location}</div>
          <button onclick="loadAdvice(${event.index})">Get Advice</button>
        </div>
      `;
    }

    function adviceHtml(advice) {
      const recommendations = advice.recommendations
        .map(item => `<div class="recommendation">${item}</div>`)
        .join('');
      return `<h3>${advice.summary}</h3>${recommendations}`;
    }

    async function loadSchedule() {
      const target = document.getElementById('schedule');
      target.textContent = 'Loading...';
      try {
        const payload = await fetchJson('/api/events');
        target.innerHTML = payload.events.map(eventHtml).join('');
      } catch (error) {
        target.innerHTML = `<p class="error">${error.message}</p>`;
      }
    }

    async function loadAdvice(index) {
      const target = document.getElementById('advice');
      target.textContent = 'Checking weather...';
      try {
        const payload = await fetchJson(`/api/advice?event=${index}`);
        target.innerHTML = adviceHtml(payload.advice);
      } catch (error) {
        target.innerHTML = `<p class="error">${error.message}</p>`;
      }
    }

    async function loadToday() {
      const target = document.getElementById('advice');
      target.textContent = 'Checking today...';
      try {
        const payload = await fetchJson('/api/today');
        target.innerHTML = payload.items.map(item => adviceHtml(item.advice)).join('<hr>');
      } catch (error) {
        target.innerHTML = `<p class="error">${error.message}</p>`;
      }
    }

    loadSchedule();
  </script>
</body>
</html>
"""


def event_to_dict(index: int, event: Event) -> dict:
    return {
        "index": index,
        "title": event.title,
        "start": event.start.strftime("%a %b %d, %I:%M %p"),
        "end": event.end.strftime("%I:%M %p"),
        "location": event.location,
    }


def advice_to_dict(advice: Advice) -> dict:
    return {
        "summary": advice.summary,
        "recommendations": advice.recommendations,
        "flags": advice.flags,
    }


class WebHandler(BaseHTTPRequestHandler):
    app: AssistantApp

    def do_GET(self) -> None:
        parsed = urlparse(self.path)

        if parsed.path == "/":
            self.send_html(HTML_PAGE)
            return
        if parsed.path == "/api/events":
            self.handle_events()
            return
        if parsed.path == "/api/advice":
            self.handle_advice(parsed.query)
            return
        if parsed.path == "/api/today":
            self.handle_today()
            return

        self.send_json({"error": "Not found"}, status=404)

    def handle_events(self) -> None:
        self.send_json(
            {
                "events": [
                    event_to_dict(index + 1, event)
                    for index, event in enumerate(self.app.events)
                ]
            }
        )

    def handle_advice(self, query: str) -> None:
        event_values = parse_qs(query).get("event", [])
        if not event_values or not event_values[0].isdigit():
            self.send_json({"error": "Use /api/advice?event=1"}, status=400)
            return

        event_index = int(event_values[0]) - 1
        if event_index < 0 or event_index >= len(self.app.events):
            self.send_json({"error": "Event number is out of range"}, status=400)
            return

        event = self.app.events[event_index]
        advice = self.app.build_advice(event)
        self.send_json({"event": event_to_dict(event_index + 1, event), "advice": advice_to_dict(advice)})

    def handle_today(self) -> None:
        today = datetime.now()
        items = []
        for index, event in enumerate(self.app.events):
            if event.start.date() == today.date():
                items.append(
                    {
                        "event": event_to_dict(index + 1, event),
                        "advice": advice_to_dict(self.app.build_advice(event)),
                    }
                )

        if not items:
            self.send_json({"error": "No events found for today"}, status=404)
            return

        self.send_json({"items": items})

    def send_html(self, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def send_json(self, payload: dict, status: int = 200) -> None:
        encoded = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    project_root = Path(__file__).resolve().parents[2]
    app = AssistantApp(project_root)
    try:
        app.reload()
    except ScheduleError as exc:
        raise SystemExit(f"Could not load schedule: {exc}") from exc

    WebHandler.app = app
    server = ThreadingHTTPServer((HOST, PORT), WebHandler)
    print(f"Browser UI running at http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()
