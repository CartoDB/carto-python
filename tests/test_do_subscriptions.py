import os
import pytest

from carto.do_subscriptions import DOSubscriptionManager


@pytest.fixture(scope="module")
def do_subscription_manager(api_key_auth_client):
    """
    Returns a DO Subscription manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid
                                APIKeyAuthClient object
    :return: DOSubscriptionManager instance
    """
    return DOSubscriptionManager(api_key_auth_client)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_get_token(do_subscription_manager):
    """
    Get all the DO Subscription from the API
    :param do_subscription_manager: Fixture that provides a subscription manager
    """
    subscriptions = do_subscription_manager.all()

    assert subscriptions is not None
    assert isinstance(subscriptions, list)
    assert len(subscriptions) > 0
