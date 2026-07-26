from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid
import os
import requests

app = Flask(__name__)
CORS(app)

orders = {}

# Service URLs are injected via environment variables so this works
# both in docker-compose (service names) and in Kubernetes (service DNS).
USER_SERVICE_URL = os.environ.get("USER_SERVICE_URL", "http://localhost:5001")
PAYMENT_SERVICE_URL = os.environ.get("PAYMENT_SERVICE_URL", "http://localhost:5002")
NOTIFICATION_SERVICE_URL = os.environ.get("NOTIFICATION_SERVICE_URL", "http://localhost:5003")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "order-service", "status": "UP"}), 200


@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(list(orders.values())), 200


@app.route("/orders/<order_id>", methods=["GET"])
def get_order(order_id):
    order = orders.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404
    return jsonify(order), 200


@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    items = data.get("items", [])
    amount = data.get("amount", 0)

    # 1. Validate the user exists by calling user-service
    try:
        user_resp = requests.get(f"{USER_SERVICE_URL}/users/{user_id}", timeout=5)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"user-service unreachable: {e}"}), 503

    if user_resp.status_code != 200:
        return jsonify({"error": "Invalid user_id, order rejected"}), 400
    user = user_resp.json()

    order_id = str(uuid.uuid4())[:8]

    # 2. Call payment-service to process payment
    try:
        payment_resp = requests.post(
            f"{PAYMENT_SERVICE_URL}/payments",
            json={"order_id": order_id, "amount": amount},
            timeout=5,
        )
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"payment-service unreachable: {e}"}), 503

    payment = payment_resp.json()

    if payment.get("status") != "SUCCESS":
        order = {
            "id": order_id,
            "user_id": user_id,
            "items": items,
            "amount": amount,
            "status": "PAYMENT_FAILED",
            "payment": payment,
        }
        orders[order_id] = order
        return jsonify(order), 402

    order = {
        "id": order_id,
        "user_id": user_id,
        "items": items,
        "amount": amount,
        "status": "CONFIRMED",
        "payment": payment,
    }
    orders[order_id] = order

    # 3. Fire a notification (best-effort, don't fail the order if this fails)
    try:
        requests.post(
            f"{NOTIFICATION_SERVICE_URL}/notify",
            json={
                "to": user.get("email"),
                "message": f"Your order {order_id} has been confirmed.",
                "channel": "email",
            },
            timeout=5,
        )
    except requests.exceptions.RequestException:
        pass

    return jsonify(order), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
