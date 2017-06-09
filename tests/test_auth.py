import pytest

from secret import API_KEY

from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException


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
