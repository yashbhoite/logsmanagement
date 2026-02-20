from flask import Flask, request, jsonify
import os
import requests
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

processed_logs = []
RECEIVER_URL = os.getenv("RECEIVER_URL")  # e.g. http://logsviewer:5002

@app.route("/ingest", methods=["POST"])
def ingest_log():
    log = request.json
    processed_logs.append(log)

    # forward to receiver if configured
    if RECEIVER_URL:
        try:
            requests.post(f"{RECEIVER_URL}/receive", json=log, timeout=2)
        except Exception as e:
            logging.exception("Failed to forward log to receiver: %s", e)

    return jsonify({"message": "log received"}), 200

@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify(processed_logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)