from flask import Flask, jsonify, request
from flask_cors import CORS
import uuid

app = Flask(__name__)
CORS(app)

# In-memory "database"
users = {
    "u1": {"id": "u1", "name": "Shivam Atre", "email": "shivam@example.com"},
    "u2": {"id": "u2", "name": "Test User", "email": "test@example.com"},
}


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "user-service", "status": "UP"}), 200


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(list(users.values())), 200


@app.route("/users/<user_id>", methods=["GET"])
def get_user(user_id):
    user = users.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json(force=True)
    user_id = str(uuid.uuid4())[:8]
    user = {"id": user_id, "name": data.get("name"), "email": data.get("email")}
    users[user_id] = user
    return jsonify(user), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
