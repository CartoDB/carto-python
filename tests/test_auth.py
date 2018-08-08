import pytest
import re
import requests
import requests_mock

from secret import API_KEY
from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from conftest import USR_BASE_URL, DEFAULT_PUBLIC_API_KEY
from carto.auth import AuthAPIClient
from carto.auth import _ClientIdentifier


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

USER1_BASE_URL = 'https://user1.carto.com/'
USER1_USERNAME = 'user1'


def test_api_key_auth_client_username():
    conf_username = APIKeyAuthClient(USER1_BASE_URL, API_KEY).username
    assert conf_username == USER1_USERNAME


def test_api_key_auth_client_me_endpoint():
    client = APIKeyAuthClient(USER1_BASE_URL, API_KEY)
    username = client.send('/api/v3/me', 'get').json()['config']['user_name']
    assert username == USER1_USERNAME


def test_auth_api_client_username():
    conf_username = AuthAPIClient(USER1_BASE_URL, API_KEY).username
    assert conf_username == USER1_USERNAME


def test_auth_api_client_me_endpoint():
    client = AuthAPIClient(USER1_BASE_URL, API_KEY)
    username = client.send('/api/v3/me', 'get').json()['config']['user_name']
    assert username == USER1_USERNAME


def test_api_key_auth_can_only_read_default_public_with_default_public():
    client = APIKeyAuthClient(USER1_BASE_URL, DEFAULT_PUBLIC_API_KEY)
    response = client.send('/api/v3/api_keys', 'get')
    assert response.status_code == 200
    api_keys = response.json()
    assert api_keys['count'] == 1
    assert len(api_keys['result']) == 1
    assert api_keys['result'][0]['name'] == 'Default public'
    assert api_keys['result'][0]['token'] == 'default_public'


def test_auth_api_can_read_api_keys_with_default_public():
    client = AuthAPIClient(USER1_BASE_URL, DEFAULT_PUBLIC_API_KEY)
    response = client.send('/api/v3/api_keys', 'get')
    assert response.status_code == 200
    assert response.json()['count'] == 1


def test_auth_api_is_valid_api_key_with_wrong_key():
    assert AuthAPIClient(USER1_BASE_URL, 'wadus').is_valid_api_key() is False


def test_auth_api_is_valid_api_key_with_default_public_key():
    assert AuthAPIClient(USER1_BASE_URL, DEFAULT_PUBLIC_API_KEY). \
               is_valid_api_key()


def test_auth_api_is_valid_api_key_with_master_key():
    if API_KEY == 'mockmockmock':
        pytest.skip("Can't be tested with mock api key")
    assert AuthAPIClient(USR_BASE_URL, API_KEY).is_valid_api_key()


def test_client_identifier():
    ci = _ClientIdentifier()

    client_id_pattern = re.compile('carto-python-sdk/\d+\.\d+\.\d+')
    assert client_id_pattern.match(ci.get_user_agent())

    client_id_pattern = re.compile('test/\d+\.\d+\.\d+')
    assert client_id_pattern.match(ci.get_user_agent('test'))

def test_user_agent():
    expected_user_agent = _ClientIdentifier().get_user_agent()
    adapter = requests_mock.Adapter()
    session = requests.Session()

    # Using file:// cause urllib's urljoin (used in pyrestcli) does not support a mock:// schema
    session.mount('file', adapter)
    adapter.register_uri('POST', 'file://test.carto.com/headers',
                         request_headers={'User-Agent': expected_user_agent})

    client = APIKeyAuthClient('file://test.carto.com', 'some_api_key', None, session)
    resp = client.send('headers', 'post')
