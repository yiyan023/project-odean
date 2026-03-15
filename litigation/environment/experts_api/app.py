"""Experts API: expert witnesses, Daubert outcomes, jury reliance."""
import csv
import logging
import os
from pathlib import Path
from flask import Flask, jsonify, request

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("experts-api")

app = Flask(__name__)
SEED_DIR = Path(os.environ.get("SEED_DATA_DIR", "/app/seed_data"))


def load_experts():
    path = SEED_DIR / "experts.csv"
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "experts-api"})


@app.route("/experts")
def list_experts():
    rows = load_experts()
    case_id = request.args.get("case_id")
    if case_id:
        rows = [r for r in rows if r.get("case_id") == case_id]
    return jsonify({"total": len(rows), "experts": rows})


@app.route("/experts/<expert_id>")
def get_expert(expert_id):
    rows = [r for r in load_experts() if r.get("expert_id") == expert_id]
    if not rows:
        return jsonify({"error": "not found"}), 404
    return jsonify(rows[0])


if __name__ == "__main__":
    logger.info("starting experts-api seed_dir=%s", SEED_DIR)
