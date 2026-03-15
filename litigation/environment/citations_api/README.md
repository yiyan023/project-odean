# Citations API (Python/Flask)

Serves precedent citation network: source case, target citation, precedent issue, treatment (followed/distinguished/rejected). Data: `seed_data/citation_network.csv`.

## Role

Citations show how opposing counsel uses Vertex, Helios, Quantum Metrics, etc., and how courts follow or distinguish. Join with Cases by `source_case_id`. Filter by `treatment` to see which precedents drive outcomes.

## Tech

- **Language**: Python 3.11
- **Framework**: Flask, Gunicorn
- **Config**: `SEED_DATA_DIR` (default `/app/seed_data`)
- **Logging**: Python logging to stdout

## Endpoints

- `GET /health` — health check
- `GET /citations` — list citations (query: `source_case_id`)

## Run locally

```bash
export SEED_DATA_DIR=/path/to/infrastructure/seed_data
pip install -r requirements.txt && gunicorn --bind 0.0.0.0:5000 app:app
```
