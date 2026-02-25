"""
Transactions Resource.

Transactions represent financial movements (buys, sells, dividends, etc.)
for a user's connected institutions.
"""

from typing import Any, Dict, List, Optional

from wealthica.exceptions import WealthicaValidationError
from wealthica.resources.base import BaseResource


class Transactions(BaseResource):
    """
    Transactions API resource.

    This resource allows you to retrieve transaction history for user institutions.

    Note: This resource requires user authentication. Use `wealthica.login(login_name)`
    to create a user-authenticated client first.

    Example:
        ```python
        user = wealthica.login("user_123")

        # Get transactions
        transactions = user.transactions.get_list(
            institutions=["603522490d2b02001233a5d6"]
        )

        # Get a specific transaction
        tx = user.transactions.get_one(tx_id="tx_id")
        ```
    """

    def get_list(
        self,
        institutions: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        investments: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        assets: Optional[bool] = None,
        liabilities: Optional[bool] = None,
        banking: Optional[bool] = None,
        types: Optional[List[str]] = None,
        deleted: Optional[bool] = None,
        invalid: Optional[bool] = None,
        new: Optional[bool] = None,
        peek: Optional[bool] = None,
        missing: Optional[bool] = None,
        last: Optional[str] = None,
        limit: Optional[int] = None,
        sort: Optional[str] = None,
        security: Optional[bool] = None,
        skip_date_filter: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get the list of transactions.

        Returns data within the last 1 year by default.

        Args:
            institutions: List of institution IDs to filter by.
            from_date: Start date filter (YYYY-MM-DD format).
            to_date: End date filter (YYYY-MM-DD format).
            investments: List of investment identifiers to filter by.
            groups: List of groups to filter by.
            assets: Include asset transactions.
            liabilities: Include liability transactions.
            banking: Include banking transactions.
            types: List of transaction types to include.
            deleted: Include deleted transactions.
            invalid: Include invalid transactions.
            new: Include new transactions.
            peek: Peek mode.
            missing: Include missing transactions.
            last: Last transaction ID for pagination.
            limit: Maximum number of transactions to return.
            sort: Sort order.
            security: Include security info.
            skip_date_filter: Skip date filtering.

        Returns:
            List of transaction objects.

        Example:
            ```python
            transactions = user.transactions.get_list(
                institutions=["603522490d2b02001233a5d6"],
                from_date="2024-01-01",
                to_date="2024-06-30",
                limit=100
            )

            for tx in transactions:
                print(f"Type: {tx['type']}, Date: {tx['date']}")
            ```
        """
        params = {}
        if institutions:
            params["institutions"] = ",".join(institutions)
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if investments:
            params["investments"] = ",".join(investments)
        if groups:
            params["groups"] = ",".join(groups)
        if assets is not None:
            params["assets"] = assets
        if liabilities is not None:
            params["liabilities"] = liabilities
        if banking is not None:
            params["banking"] = banking
        if types:
            params["types"] = ",".join(types)
        if deleted is not None:
            params["deleted"] = deleted
        if invalid is not None:
            params["invalid"] = invalid
        if new is not None:
            params["new"] = new
        if peek is not None:
            params["peek"] = peek
        if missing is not None:
            params["missing"] = missing
        if last is not None:
            params["last"] = last
        if limit is not None:
            params["limit"] = limit
        if sort:
            params["sort"] = sort
        if security is not None:
            params["security"] = security
        if skip_date_filter is not None:
            params["skip_date_filter"] = skip_date_filter

        return self._get("/transactions", params=params or None, authenticated=True)

    def get_one(self, tx_id: str) -> Dict[str, Any]:
        """
        Get a specific transaction by ID.

        Args:
            tx_id: The transaction ID.

        Returns:
            Transaction object.

        Raises:
            WealthicaValidationError: If tx_id is invalid.
            WealthicaNotFoundError: If transaction is not found.

        Example:
            ```python
            tx = user.transactions.get_one(tx_id="603522490d2b02001233a5d6")
            print(f"Type: {tx['type']}")
            ```
        """
        if not tx_id or not isinstance(tx_id, str):
            raise WealthicaValidationError("Please provide a valid Wealthica transaction ID.")

        return self._get(f"/transactions/{tx_id}", authenticated=True)
