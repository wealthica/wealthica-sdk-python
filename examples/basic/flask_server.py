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
from flask import Flask, jsonify, request, render_template_string

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
)

# Simple HTML template for the demo
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Wealthica Python SDK Demo</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .card {
            background: white;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { color: #333; }
        h2 { color: #666; margin-top: 0; }
        pre {
            background: #f0f0f0;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
            color: #333;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 5px;
            border: none;
            cursor: pointer;
        }
        .btn:hover { background: #45a049; }
        .btn-blue { background: #2196F3; }
        .btn-blue:hover { background: #1976D2; }
        input {
            padding: 10px;
            margin: 5px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            width: 200px;
        }
    </style>
</head>
<body>
    <h1>Wealthica Python SDK Demo</h1>

    <div class="card">
        <h2>1. Get Providers</h2>
        <p>Fetch the list of supported financial providers.</p>
        <a href="/api/providers" class="btn">Get Providers</a>
    </div>

    <div class="card">
        <h2>2. Get Team Info</h2>
        <p>Fetch your Wealthica team/application information.</p>
        <a href="/api/team" class="btn btn-blue">Get Team Info</a>
    </div>

    <div class="card">
        <h2>3. User Operations</h2>
        <p>Login as a user and fetch their data.</p>
        <form action="/api/auth/token" method="POST" id="tokenForm">
            <input type="text" name="user_id" placeholder="Enter User ID" required>
            <button type="submit" class="btn">Get Auth Token</button>
        </form>
        <br>
        <form action="/api/institutions" method="GET" id="institutionsForm">
            <input type="text" name="user_id" placeholder="Enter User ID" required>
            <button type="submit" class="btn btn-blue">Get Institutions</button>
        </form>
    </div>

    <div class="card">
        <h2>API Response</h2>
        <pre id="response">Click a button above to see the API response...</pre>
    </div>

    <script>
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const formData = new FormData(form);
                const method = form.method.toUpperCase();
                const url = form.action + (method === 'GET' ? '?' + new URLSearchParams(formData) : '');

                try {
                    const response = await fetch(url, {
                        method: method,
                        body: method === 'POST' ? formData : undefined
                    });
                    const data = await response.json();
                    document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('response').textContent = 'Error: ' + error.message;
                }
            });
        });

        document.querySelectorAll('a.btn').forEach(link => {
            link.addEventListener('click', async (e) => {
                e.preventDefault();
                try {
                    const response = await fetch(link.href);
                    const data = await response.json();
                    document.getElementById('response').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('response').textContent = 'Error: ' + error.message;
                }
            });
        });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Serve the demo page."""
    return render_template_string(HTML_TEMPLATE)


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


@app.route("/api/auth/token", methods=["POST"])
def get_auth_token():
    """
    Generate an auth token for a user.

    This endpoint would be called by your frontend to get a token
    for Wealthica Connect.
    """
    json_data = request.get_json(silent=True) or {}
    user_id = request.form.get("user_id") or json_data.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    try:
        user = wealthica.login(user_id)
        token = user.get_token()
        return jsonify({
            "success": True,
            "token": token,
            "user_id": user_id
        })
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/institutions")
def get_institutions():
    """Get institutions for a user."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    try:
        user = wealthica.login(user_id)
        institutions = user.institutions.get_list()
        return jsonify({
            "success": True,
            "user_id": user_id,
            "count": len(institutions),
            "institutions": institutions
        })
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/institutions/<institution_id>")
def get_institution(institution_id):
    """Get a specific institution."""
    user_id = request.args.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    try:
        user = wealthica.login(user_id)
        institution = user.institutions.get_one(institution_id)
        return jsonify({"success": True, "institution": institution})
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/institutions/<institution_id>/sync", methods=["POST"])
def sync_institution(institution_id):
    """Trigger a sync for an institution."""
    json_data = request.get_json(silent=True) or {}
    user_id = request.form.get("user_id") or json_data.get("user_id")

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    try:
        user = wealthica.login(user_id)
        institution = user.institutions.sync(institution_id)
        return jsonify({"success": True, "institution": institution})
    except WealthicaError as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/positions")
def get_positions():
    """Get positions for a user."""
    user_id = request.args.get("user_id")
    institutions = request.args.get("institutions", "").split(",") if request.args.get("institutions") else None

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    try:
        user = wealthica.login(user_id)
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
    user_id = request.args.get("user_id")
    institutions = request.args.get("institutions", "").split(",") if request.args.get("institutions") else None
    from_date = request.args.get("from")
    to_date = request.args.get("to")
    limit = request.args.get("limit", type=int)

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    try:
        user = wealthica.login(user_id)
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
    user_id = request.args.get("user_id")
    institutions = request.args.get("institutions", "").split(",") if request.args.get("institutions") else None
    from_date = request.args.get("from")
    to_date = request.args.get("to")

    if not user_id:
        return jsonify({"success": False, "error": "user_id is required"}), 400

    try:
        user = wealthica.login(user_id)
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
