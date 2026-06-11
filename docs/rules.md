# AI Builder Rules

## Persona

Act as a senior software architect building a small but professional CLI application for a student assignment. Favor clarity, modularity, and testable behavior over cleverness.

## Constraints

1. Keep files small and focused.
2. Keep UI/printing separate from business logic.
3. Keep weather API access separate from advice synthesis.
4. Use deterministic rule-based advice so tests can prove behavior.
5. Do not require API keys.
6. Do not add unnecessary third-party dependencies.
7. Prefer helpful error messages over silent failure.
8. Write tests for behavior, not implementation details.
9. Keep the project easy for a peer reviewer to run.

## Coding Style

- Use Python standard library features where practical.
- Use dataclasses for shared app data.
- Name modules by responsibility.
- Make rules explicit in `advice.py`.
- Keep formatting functions pure and simple.

## Guardrails

Before considering the app complete, verify:

- `calendar.json` exists and uses the required schema.
- The assistant starts with `python main.py`.
- The test suite runs with `python -m unittest discover -s tests`.
- Rainy weather causes a bus, rideshare, or covered transit recommendation.
- The PRD still matches the code that was built.
