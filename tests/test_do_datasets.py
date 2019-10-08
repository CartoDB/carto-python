import os
import pytest

from carto.do_datasets import DODatasetManager


@pytest.fixture(scope="module")
def do_dataset_manager(api_key_auth_client):
    """
    Returns a DO Dataset manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid
                                APIKeyAuthClient object
    :return: DODatasetManager instance
    """
    return DODatasetManager(api_key_auth_client)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_get_token(do_dataset_manager):
    """
    Get all the DO Datasets from the API
    :param do_dataset_manager: Fixture that provides a do token manager to work with
    """
    datasets = do_dataset_manager.all()

    assert datasets is not None
    assert isinstance(datasets, list)
    assert len(datasets) > 0
