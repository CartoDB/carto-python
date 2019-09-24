import os
import pytest

from carto.do_token import DoTokenManager


@pytest.fixture(scope="module")
def do_token_manager(api_key_auth_client):
    """
    Returns a do token manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid
                                APIKeyAuthClient object
    :return: DoTokenManager instance
    """
    return DoTokenManager(api_key_auth_client)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_get_token(do_token_manager):
    """
    Get all the datasets from the API
    :param do_token_manager: Fixture that provides a do token manager to work with
    """
    token = do_token_manager.get()

    assert token is not None
    assert token.access_token is not None
    assert isinstance(token.access_token, str)
    assert len(token.access_token) > 0
