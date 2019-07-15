import pytest
from time import time

from pyrestcli.exceptions import NotFoundException, UnprocessableEntityError

from carto.oauth_apps import OauthAppManager


@pytest.fixture(scope="module")
def oauth_app_manager(api_key_auth_client_usr):
    """
    Returns an OauthAppManager instance that can be reused in tests
    :param oauth_app_auth_client: Fixture that provides a valid OauthAppAuthClient
                                object
    :return: OauthAppManager instance
    """
    return OauthAppManager(api_key_auth_client_usr)


def test_get_oauth_app_not_found(oauth_app_manager):
    with pytest.raises(NotFoundException):
        oauth_app_manager.get('non-existent')


def random_oauth_app_name():
    return '_'.join(str(time()).split('.'))


def create_oauth_app(oauth_app_manager, oauth_app_name=None, redirect_uris=['https://localhost']):
    if oauth_app_name is None:
        oauth_app_name = random_oauth_app_name()
    return oauth_app_manager.create(name=oauth_app_name,
                                    redirect_uris=redirect_uris,
                                    icon_url='https://localhost',
                                    website_url='https://localhost')


def test_create_oauth_app(oauth_app_manager):
    oauth_app = create_oauth_app(oauth_app_manager)
    oauth_app_get = oauth_app_manager.get(oauth_app.id)
    assert oauth_app.id == oauth_app_get.id
    assert oauth_app.name == oauth_app_get.name
    assert oauth_app.redirect_uris == oauth_app_get.redirect_uris
    assert oauth_app.icon_url == oauth_app_get.icon_url
    assert oauth_app.website_url == oauth_app_get.website_url
    assert oauth_app.client_id is not None
    assert oauth_app.client_secret is not None

    oauth_app.delete()


def test_create_oauth_app_with_invalid_redirect_uris(oauth_app_manager):
    with pytest.raises(UnprocessableEntityError):
        create_oauth_app(oauth_app_manager, redirect_uris=['http://localhost'])


def test_regenerate_client_secret(oauth_app_manager):
    oauth_app = create_oauth_app(oauth_app_manager)
    old_client_secret = oauth_app.client_secret
    oauth_app.regenerate_client_secret()
    assert old_client_secret != oauth_app.client_secret

    oauth_app.delete()


@pytest.mark.skipif(True,
                    reason="Execute manually eventually")
def test_revoke_granted(oauth_app_manager):
    granted_oauth_apps = oauth_app_manager.all_granted()
    old_count = len(granted_oauth_apps)
    if len(granted_oauth_apps) > 0:
        granted_oauth_apps[0].revoke()

    granted_oauth_apps = oauth_app_manager.all_granted()
    assert old_count > len(granted_oauth_apps)
