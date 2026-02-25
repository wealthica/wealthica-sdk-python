"""
Institutions Resource.

Institutions represent user connections to financial institutions
(banks, brokerages, etc.) through Wealthica.
"""

from typing import Any, Dict, List, Optional

from wealthica.exceptions import WealthicaValidationError
from wealthica.resources.base import BaseResource


class Institutions(BaseResource):
    """
    Institutions API resource.

    This resource allows you to manage user institutions (connections to
    financial institutions and brokerages).

    Note: This resource requires user authentication. Use `wealthica.login(login_name)`
    to create a user-authenticated client first.

    Example:
        ```python
        user = wealthica.login("user_123")

        # Get all institutions
        institutions = user.institutions.get_list()

        # Get a specific institution
        institution = user.institutions.get_one("institution_id")

        # Sync an institution
        user.institutions.sync("institution_id")

        # Remove an institution
        user.institutions.remove("institution_id")
        ```
    """

    def get_list(self) -> List[Dict[str, Any]]:
        """
        Get the list of all institutions for the user.

        Returns:
            List of institution objects with balances and provider info.

        Example:
            ```python
            institutions = user.institutions.get_list()
            for inst in institutions:
                print(f"Institution: {inst['id']}")
                print(f"Provider: {inst['provider']['display_name']}")
            ```
        """
        return self._get("/institutions", authenticated=True)

    def get_one(self, institution_id: str) -> Dict[str, Any]:
        """
        Get a specific institution by ID.

        Args:
            institution_id: The Wealthica institution ID.

        Returns:
            Institution object with balances and provider info.

        Raises:
            WealthicaValidationError: If institution_id is invalid.
            WealthicaNotFoundError: If institution is not found.

        Example:
            ```python
            institution = user.institutions.get_one("603522490d2b02001233a5d6")
            print(f"Provider: {institution['provider']['display_name']}")
            ```
        """
        if not institution_id or not isinstance(institution_id, str):
            raise WealthicaValidationError("Please provide a valid Wealthica institution ID.")

        return self._get(f"/institutions/{institution_id}", authenticated=True)

    def sync(self, institution_id: str) -> Dict[str, Any]:
        """
        Trigger a sync for an institution to fetch latest data.

        This will initiate a refresh of the institution's data from the
        connected provider.

        Args:
            institution_id: The Wealthica institution ID.

        Returns:
            Updated institution object.

        Raises:
            WealthicaValidationError: If institution_id is invalid.
            WealthicaNotFoundError: If institution is not found.

        Example:
            ```python
            institution = user.institutions.sync("603522490d2b02001233a5d6")
            ```
        """
        if not institution_id or not isinstance(institution_id, str):
            raise WealthicaValidationError("Please provide a valid Wealthica institution ID.")

        return self._post(f"/institutions/{institution_id}/sync", json={}, authenticated=True)

    def remove(self, institution_id: str) -> None:
        """
        Remove an institution from the user.

        This will disconnect the institution and delete all associated data.

        Args:
            institution_id: The Wealthica institution ID.

        Raises:
            WealthicaValidationError: If institution_id is invalid.
            WealthicaNotFoundError: If institution is not found.

        Example:
            ```python
            user.institutions.remove("603522490d2b02001233a5d6")
            ```
        """
        if not institution_id or not isinstance(institution_id, str):
            raise WealthicaValidationError("Please provide a valid Wealthica institution ID.")

        self._delete(f"/institutions/{institution_id}", authenticated=True)
