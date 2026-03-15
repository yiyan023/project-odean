"""Rulings API: court ruling metadata (ruling_text) and ruling excerpt files."""
import csv
import logging
import os
from pathlib import Path
from flask import Flask, jsonify, request, send_file

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("rulings-api")

app = Flask(__name__)
SEED_DIR = Path(os.environ.get("SEED_DATA_DIR", "/app/seed_data"))


def load_ruling_text():
    path = SEED_DIR / "ruling_text.csv"
    if not path.exists():
        return []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))
    except Exception as e:
        logger.exception("Failed to load ruling_text.csv: %s", e)
        return []


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "rulings-api"})


@app.route("/rulings")
def list_rulings():
    rows = load_ruling_text()
    case_id = request.args.get("case_id")
    if case_id:
        rows = [r for r in rows if r.get("case_id") == case_id]
    return jsonify({"total": len(rows), "rulings": rows})


@app.route("/rulings/files")
def list_ruling_files():
    rulings_dir = SEED_DIR / "rulings"
    if not rulings_dir.exists():
        return jsonify({"total": 0, "ruling_files": []})
    try:
        case_id = request.args.get("case_id")
        files = []
        for f in sorted(rulings_dir.iterdir()):
            if f.suffix != ".txt":
                continue
            name = f.name
            if case_id and not name.startswith(case_id):
                continue
            files.append({"filename": name, "case_id": name.split("_")[0]})
        return jsonify({"total": len(files), "ruling_files": files})
    except Exception as e:
        logger.exception("Failed to list ruling files: %s", e)
        return jsonify({"total": 0, "ruling_files": []})


@app.route("/rulings/files/<path:filename>")
def get_ruling_file(filename):
    if ".." in filename:
        return jsonify({"error": "not found"}), 404
    path = SEED_DIR / "rulings" / filename
    if not path.exists():
        return jsonify({"error": "not found"}), 404
    return send_file(path, mimetype="text/plain", as_attachment=False)


if __name__ == "__main__":
    logger.info("starting rulings-api seed_dir=%s", SEED_DIR)
