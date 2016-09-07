import pytest

from secret import USERNAME, API_KEY, ORGANIZATION

from carto.api import APIKeyAuthClient, NoAuthClient
from carto.models import UserManager


@pytest.fixture(scope="session")
def api_key_auth_client():
    """
    Returns a API key authentication client that can be used to send authenticated test requests to CARTO
    :return: APIKeyAuthClient instance
    """
    return APIKeyAuthClient(API_KEY, USERNAME, ORGANIZATION)


@pytest.fixture(scope="session")
def no_auth_client():
    """
    Returns an authentication client that can be used to send anonymous test requests to CARTO
    :return: NoAuthClient instance
    """
    return NoAuthClient()


@pytest.fixture(scope="session")
def user():
    """
    Handy way for tests to have access to a user object
    :return: User instance that correspond to the test user
    """
    return UserManager(APIKeyAuthClient(API_KEY, USERNAME, ORGANIZATION)).get(USERNAME) if ORGANIZATION is not None else None
