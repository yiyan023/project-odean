"""Citations API: precedent citation network (source case, target citation, treatment)."""
import csv
import logging
import os
from pathlib import Path
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("citations-api")

app = Flask(__name__)
SEED_DIR = Path(os.environ.get("SEED_DATA_DIR", "/app/seed_data"))


def load_citations():
    path = SEED_DIR / "citation_network.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "citations-api"})


@app.route("/citations")
def list_citations():
    rows = load_citations()
    case_id = request.args.get("source_case_id")
    if case_id:
        rows = [r for r in rows if r.get("source_case_id") == case_id]
    return jsonify({"total": len(rows), "citations": rows})


if __name__ == "__main__":
    logger.info("starting citations-api seed_dir=%s", SEED_DIR)
