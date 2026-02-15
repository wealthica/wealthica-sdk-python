"""Tests for the Wealthica client."""

import pytest

from wealthica import Wealthica, WealthicaValidationError


class TestWealthicaInit:
    """Test Wealthica client initialization."""

    def test_init_with_valid_credentials(self):
        client = Wealthica(client_id="test_id", secret="test_secret")
        assert client.client_id == "test_id"
        assert client.secret == "test_secret"
        assert client.providers is not None
        assert client.teams is not None
        assert client.institutions is None
        assert client.history is None
        assert client.transactions is None
        assert client.positions is None
        client.close()

    def test_init_without_client_id(self):
        with pytest.raises(WealthicaValidationError, match="client_id"):
            Wealthica(client_id="", secret="test_secret")

    def test_init_without_secret(self):
        with pytest.raises(WealthicaValidationError, match="secret"):
            Wealthica(client_id="test_id", secret="")

    def test_init_with_invalid_client_id_type(self):
        with pytest.raises(WealthicaValidationError, match="client_id"):
            Wealthica(client_id=123, secret="test_secret")

    def test_init_with_custom_base_url(self):
        client = Wealthica(
            client_id="test_id",
            secret="test_secret",
            base_url="https://custom.api.com/v1",
        )
        assert client.base_url == "https://custom.api.com/v1"
        client.close()

    def test_init_with_login_name(self):
        client = Wealthica(
            client_id="test_id",
            secret="test_secret",
            login_name="user_123",
        )
        assert client.login_name == "user_123"
        assert client.institutions is not None
        assert client.history is not None
        assert client.transactions is not None
        assert client.positions is not None
        client.close()


class TestWealthicaLogin:
    """Test Wealthica login method."""

    def test_login_returns_new_instance(self):
        client = Wealthica(client_id="test_id", secret="test_secret")
        user = client.login("user_123")

        assert user is not client
        assert user.login_name == "user_123"
        assert user.client_id == "test_id"
        assert user.secret == "test_secret"
        assert user.institutions is not None
        assert user.history is not None
        assert user.transactions is not None
        assert user.positions is not None

        client.close()
        user.close()

    def test_login_without_login_name(self):
        client = Wealthica(client_id="test_id", secret="test_secret")
        with pytest.raises(WealthicaValidationError, match="login_name"):
            client.login("")
        client.close()

    def test_login_with_invalid_login_name_type(self):
        client = Wealthica(client_id="test_id", secret="test_secret")
        with pytest.raises(WealthicaValidationError, match="login_name"):
            client.login(123)
        client.close()

    def test_login_preserves_config(self):
        client = Wealthica(
            client_id="test_id",
            secret="test_secret",
            base_url="https://custom.api.com/v1",
            connect_url="https://custom.connect.com",
            timeout=60.0,
        )
        user = client.login("user_123")

        assert user.base_url == "https://custom.api.com/v1"
        assert user.connect_url == "https://custom.connect.com"
        assert user.timeout == 60.0

        client.close()
        user.close()


class TestWealthicaContextManager:
    """Test Wealthica context manager support."""

    def test_context_manager(self):
        with Wealthica(client_id="test_id", secret="test_secret") as client:
            assert client.client_id == "test_id"


class TestWealthicaFetchToken:
    """Test token fetching."""

    def test_fetch_token_without_login(self):
        client = Wealthica(client_id="test_id", secret="test_secret")
        with pytest.raises(WealthicaValidationError, match="login_name"):
            client.fetch_token()
        client.close()
