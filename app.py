from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import time
import base64

app = Flask(__name__)
CORS(app)

# ================== ENV VARIABLES ==================

PAYHERO_API_USERNAME = os.getenv("PAYHERO_API_USERNAME")
PAYHERO_API_PASSWORD = os.getenv("PAYHERO_API_PASSWORD")

# UPDATED CHANNEL ID
PAYHERO_CHANNEL_ID = os.getenv("PAYHERO_CHANNEL_ID", "5276")

# CALLBACK URL (unchanged)
CALLBACK_URL = os.getenv(
    "CALLBACK_URL",
    "https://pkurui-backend.onrender.com/api/payhero/callback"
)

PAYHERO_URL = "https://backend.payhero.co.ke/api/v2/payments"

# ===================================================


@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "OK", "service": "PAYHERO BACKEND RUNNING"}), 200


@app.route("/api/stk-push", methods=["POST"])
def stk_push():
    data = request.get_json(force=True)

    phone = data.get("phone")
    amount = data.get("amount")
    reference = data.get("reference", f"TXN_{int(time.time())}")
    customer_name = data.get("customer_name", "Customer")

    if not phone or not amount:
        return jsonify({"error": "phone and amount are required"}), 400

    if not PAYHERO_API_USERNAME or not PAYHERO_API_PASSWORD:
        return jsonify({"error": "PayHero API credentials not configured"}), 500

    # Build Basic Auth token
    auth_string = f"{PAYHERO_API_USERNAME}:{PAYHERO_API_PASSWORD}"
    auth_token = base64.b64encode(auth_string.encode()).decode()

    payload = {
        "amount": int(amount),
        "phone_number": phone,
        "channel_id": int(PAYHERO_CHANNEL_ID),
        "provider": "m-pesa",
        "external_reference": reference,
        "customer_name": customer_name,
        "callback_url": CALLBACK_URL
    }

    headers = {
        "Authorization": f"Basic {auth_token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(
            PAYHERO_URL,
            json=payload,
            headers=headers,
            timeout=30
        )

        print("=== STK PUSH REQUEST ===")
        print("STATUS:", response.status_code)
        print("RESPONSE:", response.text)

        return jsonify(response.json()), response.status_code

    except requests.exceptions.RequestException as e:
        print("REQUEST ERROR:", str(e))
        return jsonify({"error": "Request failed", "details": str(e)}), 500


@app.route("/api/payhero/callback", methods=["POST"])
def payhero_callback():
    data = request.get_json(force=True)

    print("=== PAYHERO CALLBACK RECEIVED ===")
    print(data)

    # You can later save:
    # - transaction status
    # - phone
    # - amount
    # - reference

    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
