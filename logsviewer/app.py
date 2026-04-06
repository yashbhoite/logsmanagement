from flask import Flask, jsonify, request, Response
import requests
import os
from prometheus_client import Counter, Histogram, generate_latest
import time

app = Flask(__name__)

PROCESSOR_URL = os.getenv("PROCESSOR_URL")
received_logs = []
healthy = True

REQUEST_COUNT = Counter(
    "viewer_requests_total",
    "Total requests to log viewer"
)

REQUEST_LATENCY = Histogram(
    "viewer_request_latency_seconds",
    "Latency of viewer requests"
)

@app.route("/receive", methods=["POST"])
def receive_log():
    log = request.json
    received_logs.append(log)
    return "received", 200

@app.route("/logs")
def get_logs():
    # prefer local received logs if any
    start = time.time()
    REQUEST_COUNT.inc()
    if received_logs:
        return jsonify({
            "message": "Here are the logs you requested",
            "data": received_logs
        })

    # fallback: fetch from processor if configured
    if PROCESSOR_URL:
        try:
            resp = requests.get(f"{PROCESSOR_URL}/logs", timeout=2)
            return jsonify(resp.json())
        except Exception:
            pass
    REQUEST_LATENCY.observe(time.time() - start)
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

@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype="text/plain")

@app.route("/")
def home():
    return "Viewer running fantastically!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)