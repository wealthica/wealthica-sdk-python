#!/usr/bin/env python3
"""
Basic usage example for the Wealthica Python SDK.

This example demonstrates:
1. Initializing the Wealthica client
2. Fetching provider information (no auth required)
3. Logging in as a user
4. Fetching user institutions, transactions, positions, and history

Before running:
1. Set your WEALTHICA_CLIENT_ID and WEALTHICA_CLIENT_SECRET environment variables
2. Install the SDK: pip install wealthica

Usage:
    export WEALTHICA_CLIENT_ID="your_client_id"
    export WEALTHICA_CLIENT_SECRET="your_secret"
    python basic.py --loginName user_123
"""

import argparse
import os
import sys
from datetime import datetime, timedelta

# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
except ImportError:
    pass

from wealthica import (
    Wealthica,
    WealthicaError,
    WealthicaAuthenticationError,
    WealthicaNotFoundError,
)


def print_separator(title: str = "") -> None:
    """Print a visual separator."""
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Wealthica Python SDK basic example")
    parser.add_argument("--loginName", required=True, help="User login name")
    args = parser.parse_args()

    # Get credentials from environment variables
    client_id = os.getenv("WEALTHICA_CLIENT_ID")
    client_secret = os.getenv("WEALTHICA_CLIENT_SECRET")

    if not client_id or not client_secret:
        print("Error: Please set WEALTHICA_CLIENT_ID and WEALTHICA_CLIENT_SECRET environment variables")
        print("\nExample:")
        print('  export WEALTHICA_CLIENT_ID="your_client_id"')
        print('  export WEALTHICA_CLIENT_SECRET="your_secret"')
        sys.exit(1)

    # Initialize the Wealthica client
    print_separator("Initializing Wealthica Client")

    with Wealthica(
        client_id=client_id,
        secret=client_secret,
        base_url=os.getenv("WEALTHICA_API_URL") or None,
        connect_url=os.getenv("WEALTHICA_CONNECT_URL") or None,
    ) as wealthica:
        # ============================================================
        # 1. Get Provider Information (No Authentication Required)
        # ============================================================
        print_separator("1. Fetching Providers")

        try:
            providers = wealthica.providers.get_list()
            print(f"Found {len(providers)} supported providers\n")

            # Show first 5 providers
            print("Sample providers:")
            for provider in providers[:5]:
                print(f"  - {provider['name']} ({provider['type']})")
                print(f"    Class: {provider.get('class', 'N/A')}, URL: {provider.get('url', 'N/A')}")

            if len(providers) > 5:
                print(f"\n  ... and {len(providers) - 5} more providers")

        except WealthicaError as e:
            print(f"Error fetching providers: {e}")

        # ============================================================
        # 2. Get Team Information
        # ============================================================
        print_separator("2. Fetching Team Information")

        try:
            team = wealthica.get_team()
            print(f"Team: {team.get('name', 'Unknown')}")
        except WealthicaError as e:
            print(f"Error fetching team info: {e}")

        # ============================================================
        # 3. User Operations (Requires User Login)
        # ============================================================
        print_separator("3. User Operations")

        login_name = args.loginName
        print(f"Logging in as user: {login_name}")
        user = wealthica.login(login_name)

        # ============================================================
        # 3a. Get User Institutions
        # ============================================================
        print("\n--- User Institutions ---")

        try:
            institutions = user.institutions.get_list()

            if institutions:
                print(f"Found {len(institutions)} institution(s)\n")

                for inst in institutions:
                    inst_id = inst.get('_id') or inst.get('id') or 'unknown'
                    print(f"Institution: {inst_id}")
                    provider = inst.get('provider') or inst.get('type') or 'unknown'
                    if isinstance(provider, dict):
                        print(f"  Provider: {provider.get('display_name', provider.get('name', 'unknown'))}")
                    else:
                        print(f"  Provider: {provider}")
                    sync_date = inst.get('sync_date') or 'unknown'
                    print(f"  Last Sync: {sync_date}")

                    balances = inst.get('balances', [])
                    if balances:
                        print(f"  Balances ({len(balances)}):")
                        for balance in balances[:3]:
                            print(f"    - {balance.get('ticker', '?')}: {balance.get('amount', 0)}")
                        if len(balances) > 3:
                            print(f"    ... and {len(balances) - 3} more")
                    print()

                # ============================================================
                # 3b. Get Positions
                # ============================================================
                print("--- Positions ---")
                first_institution_id = institutions[0].get('_id') or institutions[0].get('id')

                try:
                    positions = user.positions.get_list(
                        institutions=[first_institution_id]
                    )

                    if positions:
                        print(f"Found {len(positions)} position(s)\n")

                        for pos in positions[:5]:
                            security = pos.get('security', {})
                            print(f"  {security.get('name', 'Unknown')} ({security.get('symbol', '?')})")
                            print(f"    Quantity: {pos.get('quantity', 0)}")
                            print(f"    Market Value: ${pos.get('market_value', 0)}")
                            print(f"    Gain: {pos.get('gain_percent', 0)}%")
                            print()
                    else:
                        print("No positions found")

                except WealthicaError as e:
                    print(f"Error fetching positions: {e}")

                # ============================================================
                # 3c. Get Transactions
                # ============================================================
                print("--- Recent Transactions ---")

                thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

                try:
                    transactions = user.transactions.get_list(
                        institutions=[first_institution_id],
                        from_date=thirty_days_ago,
                        limit=5,
                    )

                    if transactions:
                        print(f"Found recent transactions\n")

                        for tx in transactions[:5]:
                            print(f"  Type: {tx.get('type', 'unknown')}")
                            print(f"  Date: {tx.get('date', 'unknown')}")
                            print(f"  Description: {tx.get('description', '')}")
                            print()
                    else:
                        print("No recent transactions found")

                except WealthicaError as e:
                    print(f"Error fetching transactions: {e}")

                # ============================================================
                # 3d. Get Balance History
                # ============================================================
                print("--- Balance History ---")

                try:
                    history = user.history.get_list(
                        institutions=[first_institution_id],
                        from_date=thirty_days_ago
                    )

                    if history:
                        print(f"Found {len(history)} history entries\n")

                        for entry in history[-5:]:
                            print(f"  {entry.get('date', 'Unknown')}: {entry.get('investment', '')}")
                    else:
                        print("No history found for this period")

                except WealthicaError as e:
                    print(f"Error fetching history: {e}")

            else:
                print("No institutions found for this user.")
                print("\nTo connect institutions, use the Wealthica Connect widget")
                print("in your frontend application.")

        except WealthicaAuthenticationError as e:
            print(f"Authentication error: {e}")
            print("\nMake sure your credentials are correct.")
        except WealthicaError as e:
            print(f"Error: {e}")

    print_separator("Done")
    print("For more examples, see the README and API documentation:")
    print("  https://wealthica.com/docs")


if __name__ == "__main__":
    main()
