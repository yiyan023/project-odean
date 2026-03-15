"""Evidence API: evidence inventory (exhibits, custodians, spoliation flags)."""
import csv
import logging
import os
from pathlib import Path
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("evidence-api")

app = Flask(__name__)
SEED_DIR = Path(os.environ.get("SEED_DATA_DIR", "/app/seed_data"))


def load_evidence():
    path = SEED_DIR / "evidence_inventory.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "evidence-api"})


@app.route("/evidence")
def list_evidence():
    rows = load_evidence()
    case_id = request.args.get("case_id")
    if case_id:
        rows = [r for r in rows if r.get("case_id") == case_id]
    return jsonify({"total": len(rows), "evidence": rows})


if __name__ == "__main__":
    logger.info("starting evidence-api seed_dir=%s", SEED_DIR)
