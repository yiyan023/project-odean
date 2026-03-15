"""Internal API: service registry only (not advertised to agent; no Slack/casual comms)."""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "internal-api"})


@app.route("/")
def index():
    """Service registry: base URLs for case-data APIs (for discovery)."""
    return jsonify({
        "services": {
            "cases": "http://cases.halcyon-pierce.internal",
            "motions": "http://motions.halcyon-pierce.internal",
            "rulings": "http://rulings.halcyon-pierce.internal",
            "experts": "http://experts.halcyon-pierce.internal",
            "evidence": "http://evidence.halcyon-pierce.internal",
            "depositions": "http://depositions.halcyon-pierce.internal",
            "citations": "http://citations.halcyon-pierce.internal",
        }
    })
