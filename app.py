from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

# ================== ENV VARIABLES ==================

PAYHERO_API_USERNAME = os.getenv("PAYHERO_API_USERNAME")
PAYHERO_API_PASSWORD = os.getenv("PAYHERO_API_PASSWORD")
PAYHERO_CHANNEL_ID = os.getenv("PAYHERO_CHANNEL_ID")
CALLBACK_URL = os.getenv("CALLBACK_URL")

PAYHERO_BASE_URL = "https://backend.payhero.co.ke/api/v2/"

# ==================================================


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "service": "PAYHERO BACKEND RUNNING"}), 200


# ================== STK PUSH ==================

@app.route("/api/stk-push", methods=["POST"])
def stk_push():

    data = request.get_json()

    phone = data.get("phone")
    amount = data.get("amount")

    if not phone or not amount:
        return jsonify({"error": "phone and amount required"}), 400

    url = PAYHERO_BASE_URL + "payments"

    payload = {
        "amount": int(amount),
        "phone_number": phone,
        "channel_id": int(PAYHERO_CHANNEL_ID),
        "external_reference": "RailwayTillPayment",
        "provider": "m-pesa",
        "callback_url": CALLBACK_URL
    }

    response = requests.post(
        url,
        json=payload,
        auth=(PAYHERO_API_USERNAME, PAYHERO_API_PASSWORD),
        headers={
            "Content-Type": "application/json"
        }
    )

    return jsonify(response.json()), response.status_code


# ================== CALLBACK ==================

@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():

    data = request.get_json()

    print("==== PAYHERO CALLBACK RECEIVED ====")
    print(data)

    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
