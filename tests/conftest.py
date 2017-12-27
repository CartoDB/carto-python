import os
import pytest

from pyrestcli.auth import NoAuthClient

from carto.auth import APIKeyAuthClient, NonVerifiedAPIKeyAuthClient
from carto.users import UserManager
from mocks import MockRequests, NotMockRequests

if "API_KEY" in os.environ:
    API_KEY = os.environ["API_KEY"]
else:
    from secret import API_KEY

if "ORGANIZATION" in os.environ:
    ORGANIZATION = os.environ["ORGANIZATION"]
else:
    from secret import ORGANIZATION

if "USERNAME" in os.environ:
    USERNAME = os.environ["USERNAME"]
else:
    from secret import USERNAME

if "ONPREMISES" in os.environ:
    ONPREMISES = os.environ["ONPREMISES"]
else:
    from secret import ONPREMISES

if "ONPREM_USERNAME" in os.environ:
    ONPREM_USERNAME = os.environ["ONPREM_USERNAME"]
else:
    from secret import ONPREM_USERNAME

if "ONPREM_ORGANIZATION" in os.environ:
    ONPREM_ORGANIZATION = os.environ["ONPREM_ORGANIZATION"]
else:
    from secret import ONPREM_ORGANIZATION

if "ONPREM_API_KEY" in os.environ:
    ONPREM_API_KEY = os.environ["ONPREM_API_KEY"]
else:
    from secret import ONPREM_API_KEY

BASE_URL = "https://{organization}.carto.com/user/{user}/". \
    format(organization=ORGANIZATION,
           user=USERNAME)
ONPREMISES_USR_BASE_URL = "https://{onpremises}/user/{onpremuser}/". \
    format(onpremises=ONPREMISES,
           onpremuser=ONPREM_USERNAME)
USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)


@pytest.fixture(scope="session")
def api_key_auth_client():
    """
    Returns a API key authentication client that can be used to send
    authenticated test requests to CARTO
    :return: APIKeyAuthClient instance
    """
    return APIKeyAuthClient(BASE_URL, API_KEY, ORGANIZATION)


@pytest.fixture(scope="session")
def api_key_auth_client_usr():
    """
    Returns a API key authentication client that can be used to send
    authenticated test requests to CARTO
    :return: APIKeyAuthClient instance
    """
    return APIKeyAuthClient(USR_BASE_URL, API_KEY)


@pytest.fixture(scope="session")
def no_auth_client():
    """
    Returns an authentication client that can be used to send anonymous
    test requests to CARTO
    :return: NoAuthClient instance
    """
    return NoAuthClient(USR_BASE_URL)


@pytest.fixture(scope="session")
def non_verified_auth_client():
    """
    Returns an authentication client that can be used to send authenticated
    test requests to CARTO onpremises
    :return: NonVerifiedAPIKeyAuthClient instance
    """
    if not ONPREM_API_KEY:
        return None
    return NonVerifiedAPIKeyAuthClient(ONPREMISES_USR_BASE_URL, ONPREM_API_KEY, ONPREM_ORGANIZATION)


@pytest.fixture(scope="session")
def wrong_onprem_auth_client():
    """
    Returns an authentication client that can be used to send authenticated
    test requests to CARTO onpremises
    :return: NonVerifiedAPIKeyAuthClient instance
    """
    if not ONPREM_API_KEY:
        return None
    return APIKeyAuthClient(ONPREMISES_USR_BASE_URL, ONPREM_API_KEY, ONPREM_ORGANIZATION)


@pytest.fixture(scope="session")
def user():
    """
    Handy way for tests to have access to a user object
    :return: User instance that correspond to the test user
    """
    return UserManager(APIKeyAuthClient(BASE_URL, API_KEY, ORGANIZATION)). \
        get(USERNAME) if ORGANIZATION is not None else None


@pytest.fixture(scope="session")
def mock_requests():
    """
    Returns a new MockRequests instance
    :return: MockRequests instance
    """
    if USERNAME == "mock":
        return MockRequests()
    else:
        return NotMockRequests()
