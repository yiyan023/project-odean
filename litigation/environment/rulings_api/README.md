# Rulings API (Python/Flask)

Serves court ruling metadata (PI, MSJ, Daubert outcomes, key holdings) and ruling excerpt text files. Data sources: `seed_data/ruling_text.csv` and `seed_data/rulings/*.txt`.

## Role

Rulings determine what reaches trial and how judges apply precedent. Join with Cases by `case_id` to analyze outcomes per case. Use `findings_flags_json` for spoliation_sanction, adverse_inference, trade_secret_defined_narrowly.

## Tech

- **Language**: Python 3.11
- **Framework**: Flask, Gunicorn
- **Config**: `SEED_DATA_DIR` (default `/app/seed_data`); see `config.yaml` for local overrides
- **Logging**: Python logging to stdout (time, level, message)

## Endpoints

- `GET /health` — health check
- `GET /rulings` — list ruling metadata (query: `case_id`)
- `GET /rulings/files` — list ruling excerpt filenames (query: `case_id`)
- `GET /rulings/files/<filename>` — raw text of a ruling excerpt

## Run locally

```bash
export SEED_DATA_DIR=/path/to/infrastructure/seed_data
pip install -r requirements.txt && gunicorn --bind 0.0.0.0:5000 app:app
```
