import pytest
import requests

from pyrestcli.exceptions import NotFoundException

from carto.maps import NamedMap, NamedMapManager
from secret import NAMED_MAP_DEFINITION, NAMED_MAP_AUTH_TOKEN, NAMED_MAP_INSTANTIATION


@pytest.fixture(scope="module")
def named_map_manager(api_key_auth_client_usr):
    """
    Returns a named map manager instance that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient object
    :return: NamedMap instance
    """
    return NamedMapManager(api_key_auth_client_usr)

def test_get_named_map_error(named_map_manager):
    with pytest.raises(NotFoundException):
        named_map_manager.get('non-existent')

def test_named_map_methods(named_map_manager):
    # Create named map
    named = named_map_manager.create(template=NAMED_MAP_DEFINITION)
    assert named.template_id is not None

    # Get the named map created
    new_named = named_map_manager.get(named.template_id)
    assert new_named.template_id == named.template_id

    # Instantiate named map
    named.instantiate(NAMED_MAP_INSTANTIATION, NAMED_MAP_AUTH_TOKEN)
    assert named.layergroupid is not None

    # Update named map
    # del named.view
    named.view = None
    named.save()
    assert named.view is None

    # Delete named map
    assert named.delete() is requests.codes.no_content

def test_named_map_manager(named_map_manager):
    # Get all named maps
    initial_maps = named_map_manager.all()

    # Create named map
    named = named_map_manager.create(template=NAMED_MAP_DEFINITION)  
    assert named.template_id is not None

    # Get all named maps again
    final_maps = named_map_manager.all()

    # Check number of maps is correct
    assert len(initial_maps) + 1 == len(final_maps)

    # Delete named map simply to avoid polluting the user's account
    assert named.delete() is requests.codes.no_content