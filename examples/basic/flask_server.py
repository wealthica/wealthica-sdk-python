#!/usr/bin/env python3
"""
Flask server example for Wealthica Python SDK.

This example demonstrates how to:
1. Generate auth tokens for your frontend
2. Handle Wealthica Connect callbacks
3. Fetch user data from your backend

Before running:
1. Install dependencies: pip install wealthica flask python-dotenv
2. Set environment variables or create a .env file
3. Run: python flask_server.py

Environment variables:
    WEALTHICA_CLIENT_ID - Your Wealthica client ID
    WEALTHICA_CLIENT_SECRET - Your Wealthica client secret
"""

import os
from flask import Flask, jsonify, request, render_template

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from wealthica import Wealthica, WealthicaError

app = Flask(__name__)

# Initialize Wealthica client
wealthica = Wealthica(
    client_id=os.getenv("WEALTHICA_CLIENT_ID", ""),
    secret=os.getenv("WEALTHICA_CLIENT_SECRET", ""),
    base_url=os.getenv("WEALTHICA_API_URL") or None,
    connect_url=os.getenv("WEALTHICA_CONNECT_URL") or None,
)

@app.route("/")
def index():
    """Serve the demo page."""
    return render_template(
        "index.html",
        client_id=os.getenv("WEALTHICA_CLIENT_ID", ""),
        api_url=os.getenv("WEALTHICA_API_URL", ""),
        connect_url=os.getenv("WEALTHICA_CONNECT_URL", ""),
        connect_type=os.getenv("WEALTHICA_CONNECT_TYPE", ""),
    )


@app.route("/api/providers")
def get_providers():
    """Get list of supported providers."""
    try:
        providers = wealthica.providers.get_list()
        return jsonify({
            "success": True,
            "count": len(providers),
            "providers": providers
        })
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/providers/<provider_id>")
def get_provider(provider_id):
    """Get a specific provider."""
    try:
        provider = wealthica.providers.get_one(provider_id)
        return jsonify({"success": True, "provider": provider})
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 404


@app.route("/api/team")
def get_team():
    """Get team information."""
    try:
        team = wealthica.get_team()
        return jsonify({"success": True, "team": team})
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/wealthica/auth", methods=["POST"])
def wealthica_auth():
    """
    Auth endpoint used by both the frontend and the Wealthica JS SDK.

    Accepts loginName from JSON body, form data, query params, or headers.
    Returns { token } for the given user.
    """
    login_name = (
        (request.get_json(silent=True) or {}).get("loginName")
        or request.form.get("loginName")
        or request.args.get("loginName")
        or request.headers.get("loginName")
    )

    if not login_name:
        return jsonify({"error": "loginName is required"}), 400

    try:
        user = wealthica.login(login_name)
        token = user.get_token()
        return jsonify({"token": token, "loginName": login_name})
    except WealthicaError as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/institutions")
def get_institutions():
    """Get institutions for a user."""
    login_name = request.args.get("loginName")

    if not login_name:
        return jsonify({"success": False, "error": "loginName is required"}), 400

    try:
        user = wealthica.login(login_name)
        institutions = user.institutions.get_list()
        return jsonify({
            "success": True,
            "loginName": login_name,
            "count": len(institutions),
            "institutions": institutions
        })
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/institutions/<institution_id>")
def get_institution(institution_id):
    """Get a specific institution."""
    login_name = request.args.get("loginName")

    if not login_name:
        return jsonify({"success": False, "error": "loginName is required"}), 400

    try:
        user = wealthica.login(login_name)
        institution = user.institutions.get_one(institution_id)
        return jsonify({"success": True, "institution": institution})
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/institutions/<institution_id>/sync", methods=["POST"])
def sync_institution(institution_id):
    """Trigger a sync for an institution."""
    json_data = request.get_json(silent=True) or {}
    login_name = request.form.get("loginName") or json_data.get("loginName")

    if not login_name:
        return jsonify({"success": False, "error": "loginName is required"}), 400

    try:
        user = wealthica.login(login_name)
        institution = user.institutions.sync(institution_id)
        return jsonify({"success": True, "institution": institution})
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/positions")
def get_positions():
    """Get positions for a user."""
    login_name = request.args.get("loginName")
    institutions = request.args.get("institutions", "").split(",") if request.args.get("institutions") else None

    if not login_name:
        return jsonify({"success": False, "error": "loginName is required"}), 400

    try:
        user = wealthica.login(login_name)
        positions = user.positions.get_list(institutions=institutions)
        return jsonify({
            "success": True,
            "count": len(positions),
            "positions": positions
        })
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/transactions")
def get_transactions():
    """Get transactions for a user."""
    login_name = request.args.get("loginName")
    institutions = request.args.get("institutions", "").split(",") if request.args.get("institutions") else None
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    limit = request.args.get("limit", type=int)

    if not login_name:
        return jsonify({"success": False, "error": "loginName is required"}), 400

    try:
        user = wealthica.login(login_name)
        transactions = user.transactions.get_list(
            institutions=institutions,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
        )
        return jsonify({
            "success": True,
            "count": len(transactions),
            "transactions": transactions
        })
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/history")
def get_history():
    """Get balance history for a user."""
    login_name = request.args.get("loginName")
    institutions = request.args.get("institutions", "").split(",") if request.args.get("institutions") else None
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    if not login_name:
        return jsonify({"success": False, "error": "loginName is required"}), 400

    try:
        user = wealthica.login(login_name)
        history = user.history.get_list(
            institutions=institutions,
            from_date=from_date,
            to_date=to_date,
        )
        return jsonify({
            "success": True,
            "count": len(history),
            "history": history
        })
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    # Check for required environment variables
    if not os.getenv("WEALTHICA_CLIENT_ID") or not os.getenv("WEALTHICA_CLIENT_SECRET"):
        print("Warning: WEALTHICA_CLIENT_ID and WEALTHICA_CLIENT_SECRET environment variables not set")
        print("Set them before running the server:")
        print('  export WEALTHICA_CLIENT_ID="your_client_id"')
        print('  export WEALTHICA_CLIENT_SECRET="your_secret"')
        print()

    print("Starting Wealthica Demo Server...")
    print("Open http://localhost:3001 in your browser")
    print()

    app.run(host="0.0.0.0", port=3001, debug=True)
