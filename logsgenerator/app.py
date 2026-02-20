from flask import Flask
import random
import logging
import requests
import os
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)

PROCESSOR_URL = os.getenv("PROCESSOR_URL", "http://localhost:5001")

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)