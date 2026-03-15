# Case Depositions API (Python/Flask)

Serves deposition segments: witness, topic tags, impeachment references. Data: `seed_data/depositions.jsonl`.

## Role

Depositions show how trade secrets were described (e.g. "platform as a whole" vs specific docs). Join with Cases by `case_id`. Use `segments[].topic_tags` and `impeachment_reference` for strategy analysis.

## Tech

- **Language**: Python 3.11
- **Framework**: Flask, Gunicorn
- **Config**: `SEED_DATA_DIR` (default `/app/seed_data`)
- **Logging**: Python logging to stdout

## Endpoints

- `GET /health` — health check
- `GET /depositions` — list depositions (query: `case_id`)

## Run locally

```bash
export SEED_DATA_DIR=/path/to/infrastructure/seed_data
pip install -r requirements.txt && gunicorn --bind 0.0.0.0:5000 app:app
```
