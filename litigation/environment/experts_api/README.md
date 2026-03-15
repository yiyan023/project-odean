# Case Experts API (Python/Flask)

Serves expert witness data: discipline, Daubert outcomes, jury reliance. Data: `seed_data/experts.csv`.

## Role

Experts drive damages and technical liability. Join with Cases and Rulings by `case_id`. Filter by `daubert_outcome` and `jury_reliance_indicator` to see how opposing counsel limits our experts.

## Tech

- **Language**: Python 3.11
- **Framework**: Flask, Gunicorn
- **Config**: `SEED_DATA_DIR` (default `/app/seed_data`)
- **Logging**: Python logging to stdout

## Endpoints

- `GET /health` — health check
- `GET /experts` — list experts (query: `case_id`)
- `GET /experts/<expert_id>` — single expert

## Run locally

```bash
export SEED_DATA_DIR=/path/to/infrastructure/seed_data
pip install -r requirements.txt && gunicorn --bind 0.0.0.0:5000 app:app
```
