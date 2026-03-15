# Evidence API (Python/Flask)

Serves evidence inventory: exhibits, custodians, doc types, hot-doc and spoliation-related flags. Data: `seed_data/evidence_inventory.csv`.

## Role

Evidence drives spoliation and impeachment. Join with Cases by `case_id`. Use `spoliation_related_flag` and `notes` to correlate with ruling outcomes.

## Tech

- **Language**: Python 3.11
- **Framework**: Flask, Gunicorn
- **Config**: `SEED_DATA_DIR` (default `/app/seed_data`)
- **Logging**: Python logging to stdout

## Endpoints

- `GET /health` — health check
- `GET /evidence` — list evidence (query: `case_id`)

## Run locally

```bash
export SEED_DATA_DIR=/path/to/infrastructure/seed_data
pip install -r requirements.txt && gunicorn --bind 0.0.0.0:5000 app:app
```
