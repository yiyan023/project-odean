# Cases API (Go)

Serves case metadata for the litigation strategy pipeline: docket, court, parties, verdict, and motion outcomes. Data is read from `seed_data/cases.csv`.

## Role

This service is the primary case registry. Other APIs (rulings, experts, evidence, depositions, motions, citations) reference cases by `caseId`. Use this API to list or filter cases, then join with other services by `case_id` / `caseId`.

## Tech

- **Language**: Go 1.21
- **HTTP**: net/http (stdlib)
- **Logging**: log/slog (JSON to stdout)
- **Config**: `SEED_DATA_DIR` (default `/app/seed_data`); optional `config.yaml` for local runs

## Endpoints

- `GET /health` — health check
- `GET /cases` — list cases (query: `case_id`, `opposing_firm_name`)
- `GET /cases/<case_id>` — single case

## Response format

JSON uses **camelCase** (e.g. `caseId`, `opposingFirmName`, `verdictFor`) to match common Go/API conventions. Other services in this stack use snake_case; when joining, map `caseId` ↔ `case_id` as needed.

## Run locally

```bash
export SEED_DATA_DIR=/path/to/infrastructure/seed_data
go run .
```

## Build

```bash
go build -o cases-api .
```
