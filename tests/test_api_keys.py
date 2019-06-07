import pytest
from time import time

from pyrestcli.exceptions import NotFoundException, UnprocessableEntityError

from carto.api_keys import APIKeyManager


@pytest.fixture(scope="module")
def api_key_manager(api_key_auth_client_usr):
    """
    Returns an APIKeyManager instance that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient
                                object
    :return: APIKeyManager instance
    """
    return APIKeyManager(api_key_auth_client_usr)


@pytest.fixture(scope="module")
def no_auth_client_fixture(no_auth_client):
    return no_auth_client


def test_get_api_key_not_found(api_key_manager):
    with pytest.raises(NotFoundException):
        api_key_manager.get('non-existent')


def create_api_key(api_key_manager, grants, api_key_name=None):
    if api_key_name is None:
        api_key_name = '_'.join(str(time()).split('.'))
    api_key_manager.create(name=api_key_name, grants=grants)
    return api_key_name


def test_create_regular_api_key(api_key_manager):
    grants = [
        {
            "type": "apis",
            "apis": ["sql", "maps"]
        },
        {
            "type": "database",
            "tables": []
        }
    ]
    api_key_name = create_api_key(api_key_manager, grants)
    api_key = api_key_manager.get(api_key_name)
    assert api_key.name == api_key_name
    assert api_key.type == 'regular'
    assert api_key.grants == grants

    api_key.delete()


def test_regenerate_token(api_key_manager):
    grants = [
        {
            "type": "apis",
            "apis": ["sql", "maps"]
        },
        {
            "type": "database",
            "tables": []
        }
    ]
    api_key_name = create_api_key(api_key_manager, grants)
    api_key = api_key_manager.get(api_key_name)
    old_token = api_key.token
    api_key.regenerate_token()
    assert old_token != api_key.token

    api_key.delete()


def test_create_invalid_api_key(api_key_manager):
    with pytest.raises(UnprocessableEntityError):
        api_key_name = 'wrong_grants'
        api_key_manager.create(name=api_key_name, grants=[])


def test_duplicate_key(api_key_manager):
    grants = [
        {
            "type": "apis",
            "apis": ["sql", "maps"]
        },
        {
            "type": "database",
            "tables": []
        }
    ]
    api_key_name = create_api_key(api_key_manager, grants)
    with pytest.raises(UnprocessableEntityError):
        create_api_key(api_key_manager, grants, api_key_name)

    api_key = api_key_manager.get(api_key_name)
    api_key.delete()


def test_api_key_manager_get_all(api_key_manager):
    api_keys = api_key_manager.all()

    assert len(api_keys) >= 2


def test_api_key_manager_filter_master(api_key_manager):
    api_keys = api_key_manager.filter(type='master')

    assert len(api_keys) == 1
    assert api_keys[0].type == 'master'
    assert api_keys[0].token is not None


def test_api_key_manager_filter_default(api_key_manager):
    api_keys = api_key_manager.filter(type='default')

    assert len(api_keys) == 1
    assert api_keys[0].type == 'default'
    assert api_keys[0].token is not None


def test_api_key_manager_filter_multiple(api_key_manager):
    api_keys = api_key_manager.filter(type='default,master')

    assert len(api_keys) == 2
