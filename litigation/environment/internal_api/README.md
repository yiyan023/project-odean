# Internal API (Python/Flask)

Service registry: returns base URLs for all case-data APIs. Used for discovery and healthchecks; not advertised to the agent in the task prompt.

## Role

Provides `GET /` with a map of service names to base URLs and `GET /health` for orchestration. No case data is served here.

## Tech

- **Language**: Python 3.11
- **Framework**: Flask, Gunicorn
- **Config**: None (no seed data)

## Endpoints

- `GET /health` — health check
- `GET /` — service registry JSON

## Run locally

```bash
pip install -r requirements.txt && gunicorn --bind 0.0.0.0:5000 app:app
```
