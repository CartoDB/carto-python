import pytest

from secret import USERNAME

from carto.models import UserManager


@pytest.fixture(scope="module")
def user_manager(api_key_auth_client):
    return UserManager(api_key_auth_client)


def test_get_users(user_manager):
    pass


def test_get_one_user(user_manager, user):
    assert user is not None
    assert user.username == USERNAME


def test_modify_user(user_manager, user):
    old_email = user.email
    new_email = "a" + old_email

    user.email = new_email
    user.save()

    user = user_manager.get(USERNAME)
    assert user.email == new_email

    user.email = old_email
    user.save()

    user = user_manager.get(USERNAME)
    assert user.email == old_email


def test_create_and_delete_user(user_manager):
    pytest.set_trace()
    new_user = user_manager.create(username="test-carto-python-sdk-1r2t3", password="test_8g7d6", email="test_carto_python_sdk_1r2t3@test.com")
    assert new_user.username == "test-carto-python-sdk-1r2t3"

    new_user = user_manager.get("test-carto-python-sdk-1r2t3")
    assert new_user.username == "test-carto-python-sdk-1r2t3"

    new_user.delete()
    assert new_user.id is None
    assert user_manager.get("test-carto-python-sdk-1r2t3") is None
