# API Endpoints Reference

All APIs use **port 80**. No authentication. From the host machine, if the hostnames do not resolve, use `curl -H "Host: <hostname>" http://127.0.0.1:80/...` or add entries to `/etc/hosts` for `*.halcyon-pierce.internal` → `127.0.0.1`.

---

## Cases

Base URL: `http://cases.halcyon-pierce.internal`  
**Convention**: JSON responses use **camelCase** (e.g. `caseId`, `opposingFirmName`, `verdictFor`). Other APIs use snake_case; join on `caseId` ↔ `case_id` as needed.

### GET /health
Returns `{"status": "ok", "service": "cases-api"}`.

### GET /cases
List cases. Query params: `case_id`, `opposing_firm_name`.

Response: `{ "total": N, "cases": [ {...} ] }` — fields in camelCase: caseId, docketNumber, courtName, judgeName, ourRole, opposingFirmName, opposingLeadCounsel, resolvedVia, verdictFor, damagesAwarded, piMotionOutcome, summaryJudgmentOutcome, tradeSecretProfile, appealFlag, appealOutcome, etc.

### GET /cases/<case_id>
Single case by ID. Returns 404 if not found. Response object uses camelCase.

---

## Motions

Base URL: `http://motions.halcyon-pierce.internal`  
**Convention**: List endpoint returns `{ "data": [...], "meta": { "total", "limit", "offset" } }` (limit/offset pagination). Other APIs use a flat `total` + array.

### GET /health
Returns `{"status": "ok", "service": "motions-api"}`.

### GET /motions
List motion brief filenames. Query params: `case_id` (filter by case), `limit` (default 100, max 500), `offset` (default 0).

Response: `{ "data": [ { "filename": "...", "case_id": "..." } ], "meta": { "total": N, "limit": L, "offset": O } }`

### GET /motions/<filename>
Raw text of a motion brief. Example: `C-2020-0312_MSJ_defense_donovan-grant.txt`.

---

## Rulings

Base URL: `http://rulings.halcyon-pierce.internal`

### GET /health
Returns `{"status": "ok", "service": "rulings-api"}`.

### GET /rulings
Court ruling metadata (from ruling_text). Query param: `case_id`.

Response: `{ "total": N, "rulings": [ {...} ] }` — ruling_id, case_id, ruling_stage, moving_party, outcome, findings_flags_json, key_holdings_text, expert_id (if Daubert), etc.

### GET /rulings/files
List ruling excerpt filenames. Query param: `case_id`.

Response: `{ "total": N, "ruling_files": [ { "filename": "...", "case_id": "..." } ] }`

### GET /rulings/files/<filename>
Raw text of a ruling excerpt file.

---

## Case Experts

Base URL: `http://experts.halcyon-pierce.internal`

### GET /health
Returns `{"status": "ok", "service": "experts-api"}`.

### GET /experts
List experts. Query param: `case_id`.

Response: `{ "total": N, "experts": [ {...} ] }` — expert_id, case_id, side (us/them), expert_name, discipline, daubert_outcome, jury_reliance_indicator, etc.

### GET /experts/<expert_id>
Single expert by ID. Returns 404 if not found.

---

## Evidence

Base URL: `http://evidence.halcyon-pierce.internal`

### GET /health
Returns `{"status": "ok", "service": "evidence-api"}`.

### GET /evidence
Evidence inventory. Query param: `case_id`.

Response: `{ "total": N, "evidence": [ {...} ] }` — case_id, exhibit_id, producing_party, doc_type, hot_doc_flag, spoliation_related_flag, notes, etc.

---

## Depositions

Base URL: `http://depositions.halcyon-pierce.internal`

### GET /health
Returns `{"status": "ok", "service": "depositions-api"}`.

### GET /depositions
Deposition segments. Query param: `case_id`.

Response: `{ "total": N, "depositions": [ {...} ] }` — case_id, depo_id, witness_name, segments (array of { topic_tags, text, uncertainty_flag, impeachment_reference }), etc.

---

## Citations

Base URL: `http://citations.halcyon-pierce.internal`

### GET /health
Returns `{"status": "ok", "service": "citations-api"}`.

### GET /citations
Precedent citation network. Query param: `source_case_id`.

Response: `{ "total": N, "citations": [ {...} ] }` — source_case_id, target_case_citation, precedent_issue, treatment (followed/distinguished/rejected), strength_indicator, etc.

---

## Tips

- Filter cases by `opposing_firm_name=Donovan Grant LLP` or opposing_lead_counsel containing "Donovan" or "Grant" to focus on the relevant matters.
- Join data across APIs by `case_id` (and `source_case_id` for citations).
- In rulings, use `findings_flags_json` for spoliation_sanction, adverse_inference, trade_secret_defined_narrowly.
- Compare Donovan/Grant case outcomes and motion/ruling text to other firms to isolate strategy patterns.
