from flask import Flask, request
import random
import logging
import requests
import os
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

PROCESSOR_URL = os.getenv("PROCESSOR_URL", "http://localhost:5001")
VIEWER_URL = os.getenv("RECEIVER_URL","http://localhost:5002")
DEFAULT_LOG_COUNT = int(os.getenv("DEFAULT_LOG_COUNT", 1))

@app.route("/")
def generate_log():
    log_type = random.choice(["INFO", "WARNING", "ERROR"])

    if log_type == "INFO":
        message = "User accessed homepage"
        logging.info(message)
    elif log_type == "WARNING":
        message = "High memory usage detected"
        logging.warning(message)
    else:
        message = "Application crashed unexpectedly"
        logging.error(message)

    log = {
        "type": log_type,
        "message": message,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }

    try:
        requests.post(f"{PROCESSOR_URL}/ingest", json=log, timeout=2)
    except Exception as e:
        logging.exception("Failed to POST log to processor: %s", e)

    return {"status": "log generated"}


@app.route("/direct-viewer")
def send_logs_to_viewer():
    count = int(request.args.get("count", DEFAULT_LOG_COUNT))  # default 1 log

    logs_sent = 0

    for _ in range(count):
        log_type = random.choice(["INFO", "WARNING", "ERROR"])

        if log_type == "INFO":
            message = "User accessed homepage (direct viewer)"
            logging.info(message)
        elif log_type == "WARNING":
            message = "High memory usage detected (direct viewer)"
            logging.warning(message)
        else:
            message = "Application crashed unexpectedly (direct viewer)"
            logging.error(message)

        log = {
            "type": log_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        try:
            requests.post(f"{VIEWER_URL}/receive", json=log, timeout=2)
            logs_sent += 1
        except Exception as e:
            logging.exception("Failed to POST log to viewer: %s", e)

    return {
        "status": "completed",
        "logs_requested": count,
        "logs_sent": logs_sent
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)