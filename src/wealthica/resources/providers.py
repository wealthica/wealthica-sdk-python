"""
Providers Resource.

Providers represent financial institutions and brokerages
that users can connect to through Wealthica.
"""

from typing import Any, Dict, List, Optional

from wealthica.exceptions import WealthicaValidationError
from wealthica.resources.base import BaseResource


class Providers(BaseResource):
    """
    Providers API resource.

    This resource allows you to retrieve information about supported
    financial providers (banks, brokerages, etc.).

    Example:
        ```python
        # Get all providers
        providers = wealthica.providers.get_list()

        # Get a specific provider
        provider = wealthica.providers.get_one("questrade")
        ```
    """

    def get_list(self) -> List[Dict[str, Any]]:
        """
        Get the list of all supported providers.

        Returns:
            List of provider objects.

        Example:
            ```python
            providers = wealthica.providers.get_list()
            for provider in providers:
                print(f"{provider['name']}: {provider['display_name']}")
            ```
        """
        return self._get("/providers", params={"format": "array"})

    def get_one(self, provider_id: str) -> Dict[str, Any]:
        """
        Get a specific provider by ID/name.

        Args:
            provider_id: The provider's unique name (e.g., "questrade", "wealthsimple").

        Returns:
            Provider object.

        Raises:
            WealthicaValidationError: If provider_id is invalid.
            WealthicaNotFoundError: If provider is not found.

        Example:
            ```python
            provider = wealthica.providers.get_one("questrade")
            print(f"Auth type: {provider['auth_type']}")
            ```
        """
        if not provider_id or not isinstance(provider_id, str):
            raise WealthicaValidationError("Please provide a valid provider ID.")

        return self._get(f"/providers/{provider_id}")
