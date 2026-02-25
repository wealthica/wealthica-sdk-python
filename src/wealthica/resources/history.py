"""
History Resource.

History represents the balance history over time for a user's connected institutions.
"""

from typing import Any, Dict, List, Optional

from wealthica.resources.base import BaseResource


class History(BaseResource):
    """
    History API resource.

    This resource allows you to retrieve balance history for user institutions.

    Note: This resource requires user authentication. Use `wealthica.login(login_name)`
    to create a user-authenticated client first.

    Example:
        ```python
        user = wealthica.login("user_123")

        # Get balance history
        history = user.history.get_list(
            institutions=["603522490d2b02001233a5d6"]
        )
        ```
    """

    def get_list(
        self,
        institutions: Optional[List[str]] = None,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        investments: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get the balance history.

        Returns data within the last 1 year by default.

        Args:
            institutions: List of institution IDs to filter by.
            from_date: Start date filter (YYYY-MM-DD format).
            to_date: End date filter (YYYY-MM-DD format).
            investments: List of investment identifiers to filter by.

        Returns:
            List of history entry objects.

        Example:
            ```python
            history = user.history.get_list(
                institutions=["603522490d2b02001233a5d6"],
                from_date="2024-01-01",
                to_date="2024-06-30"
            )

            for entry in history:
                print(f"Date: {entry['date']}, Investment: {entry['investment']}")
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

        return self._get("/history", params=params or None, authenticated=True)
