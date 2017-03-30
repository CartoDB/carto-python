import pytest

from pyrestcli.auth import NoAuthClient

from carto.auth import APIKeyAuthClient
from carto.users import UserManager

from secret import USERNAME, API_KEY, ORGANIZATION


BASE_URL = "https://{organization}.carto.com/user/{user}/".format(organization=ORGANIZATION, user=USERNAME)


@pytest.fixture(scope="session")
def api_key_auth_client():
    """
    Returns a API key authentication client that can be used to send authenticated test requests to CARTO
    :return: APIKeyAuthClient instance
    """
    return APIKeyAuthClient(BASE_URL, API_KEY, ORGANIZATION)


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
    return UserManager(APIKeyAuthClient(BASE_URL, API_KEY, ORGANIZATION)).get(USERNAME) if ORGANIZATION is not None else None
