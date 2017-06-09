import os
import pytest
import time
from pyrestcli.exceptions import NotFoundException

from carto.users import UserManager

if "USERNAME" in os.environ:
    USERNAME = os.environ["USERNAME"]
else:
    from secret import USERNAME


@pytest.fixture(scope="module")
def user_manager(api_key_auth_client):
    """
    Returns a user manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient
                                object
    :return: UserManager instance
    """
    return UserManager(api_key_auth_client)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_get_users(user_manager):
    """
    Currently not supported by the user API. If we actually tried to perform
    this test, an exception would be raised
    :param user_manager: User manager to work with
    """
    pass


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_get_one_user(user):
    """
    Test retrieval of a single user from the API
    :param user: There is a fixture that returns a user object, so let's use it
                    instead of specifically requesting a user
    """
    assert user is not None
    assert user.username == USERNAME


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_modify_user(user_manager, user):
    """
    Test modifying a user
    :param user_manager: User manager to work with
    :param user: User to be modified
    """
    old_email = user.email
    new_email = "a" + old_email

    user.email = new_email
    user.save()

    user = user_manager.get(USERNAME)
    assert user.email == new_email

    # Let's undo the change
    user.email = old_email
    user.save()

    user = user_manager.get(USERNAME)
    assert user.email == old_email


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_create_and_delete_user(user_manager):
    """
    Test creating a user and then deleting it
    :param user_manager: User manager to work with
    """
    new_user = user_manager.create(
        username="test-carto-python-sdk-1r2t31",
        password="test_8g7d6",
        email="test_carto_python_sdk_1r2t31@test.com")
    assert new_user.username == "test-carto-python-sdk-1r2t31"

    # We need to wait until a GET request will find the recently created user
    time.sleep(10)
    new_user = user_manager.get("test-carto-python-sdk-1r2t31")
    assert new_user.username == "test-carto-python-sdk-1r2t31"

    new_user.delete()
    with pytest.raises(NotFoundException):
        user_manager.get("test-carto-python-sdk-1r2t31")
