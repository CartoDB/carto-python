import pytest

from carto.file_import import FileImportJobManager


@pytest.fixture(scope="module")
def file_import_manager(api_key_auth_client):
    """
    Returns a file import manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient
                                object
    :return: FileImportJobManager instance
    """
    return FileImportJobManager(api_key_auth_client)


def test_get_file_imports(file_import_manager):
    """
    Get all the file imports from the API
    :param file_import_manager: Fixture that provides a file import manager
                                to work with
    """
    file_imports = file_import_manager.all()

    assert len(file_imports) >= 0
