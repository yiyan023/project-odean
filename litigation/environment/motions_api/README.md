# Motions API (Node.js)

Serves motion brief filings: list of motion files and raw text content. Used by the litigation strategy pipeline to read defense/plaintiff briefs per case.

## Role

Motion briefs are key to understanding opposing counsel’s arguments (e.g. precedent citations, trade-secret identification). This API exposes them by case. Join with the Cases API by `case_id` to filter motions for a given case.

## Tech

- **Runtime**: Node.js 20
- **Framework**: Express
- **Config**: `SEED_DATA_DIR` (default `/app/seed_data`), `PORT` (default 5000)
- **Logging**: JSON lines to stdout

## API conventions

- **Response shape**: List endpoint returns `{ data: [...], meta: { total, limit, offset } }` (limit/offset pagination). Other services use `{ total, motions }`; this one uses `data` + `meta` for variety.
- **Query params**: `case_id`, `limit`, `offset` (default limit 100, max 500).

## Endpoints

- `GET /health` — health check
- `GET /motions` — list motion filenames (query: `case_id`, `limit`, `offset`)
- `GET /motions/<filename>` — raw text of a motion brief

## Run locally

```bash
export SEED_DATA_DIR=/path/to/infrastructure/seed_data
npm install && npm start
```
