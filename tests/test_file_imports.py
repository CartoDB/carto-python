import pytest

from carto.file_import import FileImportJobManager
from secret import IMPORT_FILE, IMPORT_URL


@pytest.fixture(scope="module")
def file_import_manager(api_key_auth_client):
    """
    Returns a file import manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient object
    :return: FileImportJobManager instance
    """
    return FileImportJobManager(api_key_auth_client)


def test_get_file_imports(file_import_manager):
    """
    Get all the file imports from the API
    :param file_import_manager: Fixture that provides a file import manager to work with
    """
    file_imports = file_import_manager.all()

    assert len(file_imports) >= 0

def test_import_url(file_import_manager):
    """
    Imports a remote URL file
    :param file_import_manager: Fixture that provides a file import manager to work with
    """
    file_imported = file_import_manager.create(IMPORT_URL, create_visualization=True)

    assert file_imported is not None and file_imported.item_queue_id is not None

    file_imported_prev = file_import_manager.get(file_imported.item_queue_id)

    assert file_imported_prev is not None and file_imported_prev.item_queue_id is not None

def test_import_file(file_import_manager):
    """
    Imports a local CSV file
    :param file_import_manager: Fixture that provides a file import manager to work with
    """
    file_imported = file_import_manager.create(IMPORT_FILE, create_visualization=True)

    assert file_imported is not None and file_imported.item_queue_id is not None

    file_imported_prev = file_import_manager.get(file_imported.item_queue_id)

    assert file_imported_prev is not None and file_imported_prev.item_queue_id is not None
