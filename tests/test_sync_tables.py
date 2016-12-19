import pytest

from carto.sync_tables import SyncTableJobManager


@pytest.fixture(scope="module")
def sync_table_manager(api_key_auth_client):
    """
    Returns a sync table manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient object
    :return: SyncTableJobManager instance
    """
    return SyncTableJobManager(api_key_auth_client)


def test_get_sync_tables(sync_table_manager):
    """
    Get all the sync tables from the API
    :param sync_table_manager: Fixture that provides a sync table manager to work with
    """
    sync_tables = sync_table_manager.all()

    assert len(sync_tables) >= 0
