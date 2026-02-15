"""
Wealthica SDK Client.
"""

import time
from typing import Any, Dict, List, Optional

import httpx
import jwt

from wealthica.constants import API_URL, CONNECT_URL, DEFAULT_TOKEN_MINIMUM_LIFETIME
from wealthica.exceptions import (
    WealthicaAPIError,
    WealthicaAuthenticationError,
    WealthicaError,
    WealthicaNotFoundError,
    WealthicaRateLimitError,
    WealthicaValidationError,
)
from wealthica.resources.history import History
from wealthica.resources.institutions import Institutions
from wealthica.resources.positions import Positions
from wealthica.resources.providers import Providers
from wealthica.resources.teams import Teams
from wealthica.resources.transactions import Transactions


class Wealthica:
    """
    Wealthica API Client.

    This is the main entry point for interacting with the Wealthica API.
    Initialize with your client_id and secret, then use the login() method
    to create user-specific instances for accessing user data.

    Example:
        ```python
        from wealthica import Wealthica

        # Initialize the client
        wealthica = Wealthica(client_id="your_client_id", secret="your_secret")

        # Get list of providers (no user login required)
        providers = wealthica.providers.get_list()

        # Login as a specific user
        user = wealthica.login("user_123")

        # Get user's institutions
        institutions = user.institutions.get_list()
        ```
    """

    def __init__(
        self,
        client_id: str,
        secret: str,
        base_url: Optional[str] = None,
        connect_url: Optional[str] = None,
        login_name: Optional[str] = None,
        timeout: float = 30.0,
    ):
        """
        Initialize the Wealthica client.

        Args:
            client_id: Your Wealthica client ID.
            secret: Your Wealthica client secret.
            base_url: Optional custom base URL for the API.
            connect_url: Optional custom URL for the Connect widget.
            login_name: Optional user login name for user-specific operations.
            timeout: Request timeout in seconds (default: 30.0).

        Raises:
            WealthicaValidationError: If client_id or secret is invalid.
        """
        if not client_id or not isinstance(client_id, str):
            raise WealthicaValidationError("Please provide a valid Wealthica client_id.")
        if not secret or not isinstance(secret, str):
            raise WealthicaValidationError("Please provide a valid Wealthica secret.")

        self.client_id = client_id
        self.secret = secret
        self.base_url = base_url or API_URL
        self.connect_url = connect_url or CONNECT_URL
        self.login_name = login_name
        self.timeout = timeout

        # Token cache
        self._token: Optional[str] = None
        self._token_payload: Optional[Dict[str, Any]] = None

        # HTTP client for API requests
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={"Content-Type": "application/json"},
        )

        # Initialize resources available without user login
        self.providers = Providers(self)
        self.teams = Teams(self)

        # User-specific resources (only available after login)
        self.institutions: Optional[Institutions] = None
        self.history: Optional[History] = None
        self.transactions: Optional[Transactions] = None
        self.positions: Optional[Positions] = None

        # If login_name provided, initialize as logged-in user
        if login_name:
            self._init_user_resources()

    def _init_user_resources(self) -> None:
        """Initialize user-specific resources."""
        self.institutions = Institutions(self)
        self.history = History(self)
        self.transactions = Transactions(self)
        self.positions = Positions(self)

    def login(self, login_name: str) -> "Wealthica":
        """
        Create a new Wealthica instance logged in as a specific user.

        This method returns a new Wealthica instance that can access user-specific
        resources like institutions, transactions, history, and positions.

        Args:
            login_name: The unique identifier for the user in your system.

        Returns:
            A new Wealthica instance configured for the specified user.

        Raises:
            WealthicaValidationError: If login_name is invalid.

        Example:
            ```python
            wealthica = Wealthica(client_id="...", secret="...")
            user = wealthica.login("user_123")
            institutions = user.institutions.get_list()
            ```
        """
        if not login_name or not isinstance(login_name, str):
            raise WealthicaValidationError("Please provide a valid login_name.")

        return Wealthica(
            client_id=self.client_id,
            secret=self.secret,
            base_url=self.base_url,
            connect_url=self.connect_url,
            login_name=login_name,
            timeout=self.timeout,
        )

    def get_token(self, minimum_lifetime: int = DEFAULT_TOKEN_MINIMUM_LIFETIME) -> str:
        """
        Get an authentication token, fetching a new one if necessary.

        The token is cached and reused until it has less than the specified
        minimum lifetime remaining.

        Args:
            minimum_lifetime: Minimum remaining lifetime in seconds (default: 10).

        Returns:
            A valid authentication token.

        Raises:
            WealthicaAuthenticationError: If token fetch fails.
        """
        current_time = time.time()

        # Check if we have a valid cached token
        if self._token and self._token_payload:
            exp = self._token_payload.get("exp", 0)
            if current_time < (exp - minimum_lifetime):
                return self._token

        # Fetch a new token
        return self.fetch_token()

    def fetch_token(self) -> str:
        """
        Fetch a new authentication token from the API.

        Returns:
            A new authentication token.

        Raises:
            WealthicaAuthenticationError: If token fetch fails.
        """
        if not self.login_name:
            raise WealthicaValidationError(
                "Cannot fetch token without a login_name. Use login() method first."
            )

        try:
            response = self._client.post(
                "/auth/token",
                json={"clientId": self.client_id, "secret": self.secret},
                headers={"loginName": self.login_name},
            )
            self._handle_response_errors(response)

            data = response.json()
            token = data.get("token")

            if not token:
                raise WealthicaAuthenticationError("No token received from API")

            # Decode and cache the token
            self._token = token
            self._token_payload = jwt.decode(token, options={"verify_signature": False})

            return self._token

        except httpx.HTTPError as e:
            raise WealthicaAuthenticationError(f"Failed to fetch token: {str(e)}")

    def get_team(self) -> Dict[str, Any]:
        """
        Get information about your Wealthica team/application.

        Returns:
            Team information including name, features, and settings.

        Example:
            ```python
            team = wealthica.get_team()
            print(team["name"])
            ```
        """
        return self.teams.info()

    def _get_auth_headers(self) -> Dict[str, str]:
        """Get headers with authentication token."""
        return {"Authorization": f"Bearer {self.get_token()}"}

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        authenticated: bool = False,
    ) -> Any:
        """
        Make an API request.

        Args:
            method: HTTP method (GET, POST, DELETE).
            endpoint: API endpoint path.
            params: Query parameters.
            json: JSON body data.
            authenticated: Whether to include authentication header.

        Returns:
            Response data.

        Raises:
            WealthicaAPIError: If the API returns an error.
        """
        headers = {}
        if authenticated:
            headers.update(self._get_auth_headers())

        try:
            response = self._client.request(
                method=method,
                url=endpoint,
                params=params,
                json=json,
                headers=headers,
            )
            self._handle_response_errors(response)

            # Return None for 204 No Content
            if response.status_code == 204:
                return None

            return response.json()

        except httpx.HTTPError as e:
            raise WealthicaAPIError(f"Request failed: {str(e)}")

    def _handle_response_errors(self, response: httpx.Response) -> None:
        """
        Handle API response errors.

        Args:
            response: The HTTP response object.

        Raises:
            WealthicaAuthenticationError: For 401 errors.
            WealthicaNotFoundError: For 404 errors.
            WealthicaRateLimitError: For 429 errors.
            WealthicaAPIError: For other error status codes.
        """
        if response.is_success:
            return

        status_code = response.status_code
        try:
            error_data = response.json()
            message = error_data.get("message", error_data.get("error", response.text))
        except Exception:
            error_data = {}
            message = response.text or f"HTTP {status_code}"

        if status_code == 401:
            raise WealthicaAuthenticationError(message, status_code, error_data)
        elif status_code == 404:
            raise WealthicaNotFoundError(message, status_code, error_data)
        elif status_code == 429:
            raise WealthicaRateLimitError(message, status_code, error_data)
        elif status_code == 400:
            raise WealthicaValidationError(message, status_code, error_data)
        else:
            raise WealthicaAPIError(message, status_code, error_data)

    def close(self) -> None:
        """Close the HTTP client connection."""
        self._client.close()

    def __enter__(self) -> "Wealthica":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()
