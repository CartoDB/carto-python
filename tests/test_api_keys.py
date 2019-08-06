import pytest
from time import time

from pyrestcli.exceptions import NotFoundException, UnprocessableEntityError

from carto.api_keys import APIKeyManager
from carto.datasets import DatasetManager
from carto.exceptions import CartoException
from secret import EXISTING_POINT_DATASET


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
def dataset_manager(api_key_auth_client_usr):
    """
    Returns a DatasetManager instance that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient
                                object
    :return: DatasetManager instance
    """
    return DatasetManager(api_key_auth_client_usr)


@pytest.fixture(scope="module")
def no_auth_client_fixture(no_auth_client):
    return no_auth_client


def test_get_api_key_not_found(api_key_manager):
    with pytest.raises(NotFoundException):
        api_key_manager.get('non-existent')


def random_api_key_name():
    return '_'.join(str(time()).split('.'))


def create_api_key(api_key_manager, grants, api_key_name=None):
    if api_key_name is None:
        api_key_name = random_api_key_name()
    api_key_manager.create(name=api_key_name, apis=grants[0]['apis'], tables=grants[1]['tables'])
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
    assert api_key.grants.apis == ["sql", "maps"]
    assert api_key.grants.tables == []

    api_key.delete()


def test_create_regular_api_key_with_tables(api_key_manager, dataset_manager):
    table = dataset_manager.get(EXISTING_POINT_DATASET)
    grants = [
        {
            "type": "apis",
            "apis": ["sql", "maps"]
        },
        {
            "type": "database",
            "tables": [{
                "schema": api_key_manager.client.username,
                "name": table.name,
                "permissions": [
                    "insert",
                    "select",
                    "update"
                ]
            }]
        }
    ]
    api_key_name = create_api_key(api_key_manager, grants)
    api_key = api_key_manager.get(api_key_name)
    assert api_key.name == api_key_name
    assert api_key.type == 'regular'
    assert api_key.grants.apis == ["sql", "maps"]
    assert len(api_key.grants.tables) == 1
    assert api_key.grants.tables[0].schema == api_key_manager.client.username
    assert api_key.grants.tables[0].name == table.name
    assert api_key.grants.tables[0].permissions == ['insert', 'select', 'update']

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
    with pytest.raises(CartoException):
        api_key_name = random_api_key_name()
        api_key_manager.create(name=api_key_name, apis=[])


def test_create_invalid_tables_api_key(api_key_manager):
    with pytest.raises(UnprocessableEntityError):
        api_key_name = random_api_key_name()
        api_key_manager.create(name=api_key_name, tables=[{'t': 'pra'}])


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
