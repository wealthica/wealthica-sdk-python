"""
Positions Resource.

Positions represent investment holdings for a user's connected institutions.
"""

from typing import Any, Dict, List, Optional

from wealthica.resources.base import BaseResource


class Positions(BaseResource):
    """
    Positions API resource.

    This resource allows you to retrieve investment positions for user institutions.

    Note: This resource requires user authentication. Use `wealthica.login(login_name)`
    to create a user-authenticated client first.

    Example:
        ```python
        user = wealthica.login("user_123")

        # Get all positions
        positions = user.positions.get_list()

        # Get positions for specific institutions
        positions = user.positions.get_list(
            institutions=["603522490d2b02001233a5d6"]
        )
        ```
    """

    def get_list(
        self,
        institutions: Optional[List[str]] = None,
        investments: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
        assets: Optional[bool] = None,
        liabilities: Optional[bool] = None,
        banking: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """
        Get user positions.

        Args:
            institutions: List of institution IDs to filter by.
            investments: List of investment identifiers to filter by.
            groups: List of groups to filter by.
            assets: Include asset positions.
            liabilities: Include liability positions.
            banking: Include banking positions.

        Returns:
            List of position objects with security and investment details.

        Example:
            ```python
            positions = user.positions.get_list(
                institutions=["603522490d2b02001233a5d6"]
            )

            for pos in positions:
                print(f"Security: {pos['security']['name']}")
                print(f"  Quantity: {pos['quantity']}")
                print(f"  Market Value: {pos['market_value']}")
                print(f"  Gain: {pos['gain_percent']}%")
            ```
        """
        params = {}
        if institutions:
            params["institutions"] = ",".join(institutions)
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

        return self._get("/positions", params=params or None, authenticated=True)
