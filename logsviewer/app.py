from flask import Flask, jsonify, request
import requests
import os

app = Flask(__name__)

PROCESSOR_URL = os.getenv("PROCESSOR_URL")
received_logs = []
healthy = True

@app.route("/receive", methods=["POST"])
def receive_log():
    log = request.json
    received_logs.append(log)
    return "received", 200

@app.route("/logs")
def get_logs():
    # prefer local received logs if any
    if received_logs:
        return jsonify(received_logs)

    # fallback: fetch from processor if configured
    if PROCESSOR_URL:
        try:
            resp = requests.get(f"{PROCESSOR_URL}/logs", timeout=2)
            return jsonify(resp.json())
        except Exception:
            pass

    return jsonify([])

@app.route("/break")
def break_viewer():
    global healthy
    healthy = False
    return "Viewer readiness broken"

@app.route("/fix")
def fix_viewer():
    global healthy
    healthy = True
    return "Viewer readiness fixed"

@app.route("/")
def home():
    return "Viewer running"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)