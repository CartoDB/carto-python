import pytest

from secret import USERNAME, API_KEY, ORGANIZATION

from carto.api import APIKeyAuthClient, NoAuthClient
from carto.models import UserManager


@pytest.fixture(scope="session")
def api_key_auth_client():
    return APIKeyAuthClient(API_KEY, USERNAME, ORGANIZATION)


@pytest.fixture(scope="session")
def no_auth_client():
    return NoAuthClient()


@pytest.fixture(scope="session")
def user():
    return UserManager(APIKeyAuthClient(API_KEY, USERNAME, ORGANIZATION)).get(USERNAME) if ORGANIZATION is not None else None
