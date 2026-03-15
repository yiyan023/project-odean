"""Depositions API: deposition segments (witness, topic tags, impeachment refs)."""
import json
import logging
import os
from pathlib import Path
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("depositions-api")

app = Flask(__name__)
SEED_DIR = Path(os.environ.get("SEED_DATA_DIR", "/app/seed_data"))


def load_depositions():
    path = SEED_DIR / "depositions.jsonl"
    if not path.exists():
        return []
    out = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "depositions-api"})


@app.route("/depositions")
def list_depositions():
    rows = load_depositions()
    case_id = request.args.get("case_id")
    if case_id:
        rows = [r for r in rows if r.get("case_id") == case_id]
    return jsonify({"total": len(rows), "depositions": rows})


if __name__ == "__main__":
    logger.info("starting depositions-api seed_dir=%s", SEED_DIR)
