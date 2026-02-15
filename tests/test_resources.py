"""Tests for Wealthica API resources."""

import pytest

from wealthica import Wealthica, WealthicaValidationError


@pytest.fixture
def client():
    c = Wealthica(client_id="test_id", secret="test_secret")
    yield c
    c.close()


@pytest.fixture
def user(client):
    u = client.login("test_user")
    yield u
    u.close()


class TestProviders:
    """Test Providers resource."""

    def test_providers_available_without_login(self, client):
        assert client.providers is not None

    def test_get_one_validates_id(self, client):
        with pytest.raises(WealthicaValidationError, match="provider ID"):
            client.providers.get_one("")

    def test_get_one_validates_id_type(self, client):
        with pytest.raises(WealthicaValidationError, match="provider ID"):
            client.providers.get_one(123)


class TestTeams:
    """Test Teams resource."""

    def test_teams_available_without_login(self, client):
        assert client.teams is not None


class TestInstitutions:
    """Test Institutions resource."""

    def test_institutions_not_available_without_login(self, client):
        assert client.institutions is None

    def test_institutions_available_after_login(self, user):
        assert user.institutions is not None

    def test_get_one_validates_id(self, user):
        with pytest.raises(WealthicaValidationError, match="institution ID"):
            user.institutions.get_one("")

    def test_get_one_validates_id_type(self, user):
        with pytest.raises(WealthicaValidationError, match="institution ID"):
            user.institutions.get_one(123)

    def test_sync_validates_id(self, user):
        with pytest.raises(WealthicaValidationError, match="institution ID"):
            user.institutions.sync("")

    def test_remove_validates_id(self, user):
        with pytest.raises(WealthicaValidationError, match="institution ID"):
            user.institutions.remove("")


class TestTransactions:
    """Test Transactions resource."""

    def test_transactions_not_available_without_login(self, client):
        assert client.transactions is None

    def test_transactions_available_after_login(self, user):
        assert user.transactions is not None

    def test_get_one_validates_id(self, user):
        with pytest.raises(WealthicaValidationError, match="transaction ID"):
            user.transactions.get_one("")

    def test_get_one_validates_id_type(self, user):
        with pytest.raises(WealthicaValidationError, match="transaction ID"):
            user.transactions.get_one(123)


class TestPositions:
    """Test Positions resource."""

    def test_positions_not_available_without_login(self, client):
        assert client.positions is None

    def test_positions_available_after_login(self, user):
        assert user.positions is not None


class TestHistory:
    """Test History resource."""

    def test_history_not_available_without_login(self, client):
        assert client.history is None

    def test_history_available_after_login(self, user):
        assert user.history is not None
