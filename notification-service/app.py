from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

notifications_log = []


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "notification-service", "status": "UP"}), 200


@app.route("/notify", methods=["POST"])
def notify():
    data = request.get_json(force=True)
    entry = {
        "to": data.get("to", "unknown"),
        "message": data.get("message", ""),
        "channel": data.get("channel", "email"),
        "timestamp": datetime.utcnow().isoformat(),
    }
    notifications_log.append(entry)

    # In a real system this would call an email/Slack API.
    print(f"[NOTIFY] via {entry['channel']} to {entry['to']}: {entry['message']}")

    return jsonify({"status": "SENT", "notification": entry}), 201


@app.route("/notifications", methods=["GET"])
def list_notifications():
    return jsonify(notifications_log), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
