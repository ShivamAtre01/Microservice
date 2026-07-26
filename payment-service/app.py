from flask import Flask, jsonify, request
import uuid
import random

app = Flask(__name__)

payments = {}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "payment-service", "status": "UP"}), 200


@app.route("/payments", methods=["POST"])
def process_payment():
    data = request.get_json(force=True)
    amount = data.get("amount", 0)
    order_id = data.get("order_id")

    # Simulate a payment gateway: fail only if amount is invalid
    success = amount is not None and amount > 0

    payment_id = str(uuid.uuid4())[:8]
    payment = {
        "id": payment_id,
        "order_id": order_id,
        "amount": amount,
        "status": "SUCCESS" if success else "FAILED",
        "transaction_ref": f"TXN-{random.randint(100000, 999999)}",
    }
    payments[payment_id] = payment

    status_code = 201 if success else 402
    return jsonify(payment), status_code


@app.route("/payments/<payment_id>", methods=["GET"])
def get_payment(payment_id):
    payment = payments.get(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    return jsonify(payment), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
