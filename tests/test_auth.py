import pytest

from secret import API_KEY
from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from conftest import USR_BASE_URL, USERNAME, DEFAULT_PUBLIC_API_KEY
from carto.auth import AuthAPIClient


def test_wrong_url():
    with pytest.raises(CartoException):
        APIKeyAuthClient('https://wrongurl', API_KEY).username


def test_cloud_personal_url():
    user1 = APIKeyAuthClient('https://user1.carto.com/a/b/c',
                             API_KEY).username
    user2 = APIKeyAuthClient('https://www.user2.carto.com',
                             API_KEY).username
    user3 = APIKeyAuthClient('http://www.user3.carto.com/a/b/c',
                             API_KEY).username
    assert user1 == 'user1'
    assert user2 == 'user2'
    assert user3 == 'user3'


def test_on_prem_url():
    user1 = APIKeyAuthClient('https://carto.com/user/user1/a/b/c',
                             API_KEY).username
    user2 = APIKeyAuthClient('https://www.carto.com/user/user2',
                             API_KEY).username
    user3 = APIKeyAuthClient('http://www.carto.com/user/user3/a/b/c',
                             API_KEY).username
    assert user1 == 'user1'
    assert user2 == 'user2'
    assert user3 == 'user3'


def test_api_key_auth_client_username():
    conf_username = APIKeyAuthClient(USR_BASE_URL, API_KEY).username
    assert conf_username == USERNAME


def test_api_key_auth_client_me_endpoint():
    client = APIKeyAuthClient(USR_BASE_URL, API_KEY)
    username = client.send('/api/v3/me', 'get').json()['config']['user_name']
    assert username == USERNAME


def test_auth_api_client_username():
    conf_username = AuthAPIClient(USR_BASE_URL, API_KEY).username
    assert conf_username == USERNAME


def test_auth_api_client_me_endpoint():
    client = AuthAPIClient(USR_BASE_URL, API_KEY)
    username = client.send('/api/v3/me', 'get').json()['config']['user_name']
    assert username == USERNAME


def test_api_key_auth_cant_read_api_keys_with_default_public():
    client = APIKeyAuthClient(USR_BASE_URL, DEFAULT_PUBLIC_API_KEY)
    response = client.send('/api/v3/api_keys', 'get')
    assert response.status_code == 401


def test_auth_api_can_read_api_keys_with_default_public():
    client = AuthAPIClient(USR_BASE_URL, DEFAULT_PUBLIC_API_KEY)
    response = client.send('/api/v3/api_keys', 'get')
    assert response.status_code == 200
    assert response.json()['count'] == 1


def test_auth_api_is_valid_api_key_with_wrong_key():
    assert AuthAPIClient(USR_BASE_URL, 'wadus').is_valid_api_key() == False


def test_auth_api_is_valid_api_key_with_default_public_key():
    assert AuthAPIClient(USR_BASE_URL, DEFAULT_PUBLIC_API_KEY). \
               is_valid_api_key() == True


def test_auth_api_is_valid_api_key_with_master_key():
    assert AuthAPIClient(USR_BASE_URL, API_KEY).is_valid_api_key() == True
