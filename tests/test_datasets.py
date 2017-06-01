import os
import pytest
from pyrestcli.exceptions import NotFoundException

from carto.datasets import DatasetManager
from carto.permissions import PRIVATE, PUBLIC

from secret import IMPORT_URL

import logging
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


@pytest.fixture(scope="module")
def dataset_manager(api_key_auth_client):
    """
    Returns a dataset manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid
                                APIKeyAuthClient object
    :return: DataManager instance
    """
    return DatasetManager(api_key_auth_client)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_get_datasets(dataset_manager, user):
    """
    Get all the datasets from the API
    :param dataset_manager: Fixture that provides a user manager to work with
    :param user: If valid, we'll check the number of returned datasets exactly
                    against the expected value
    """
    datasets = dataset_manager.all()

    # If are testing against an enterprise account and have a valid user, we
    # can easily know how many datasets to expect
    if user is not None:
        assert len(datasets) == user.table_count
    else:
        assert len(datasets) >= 0


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_create_and_modify_and_delete_dataset_from_file(dataset_manager):
    """
    Test creating a dataset from a local file, modifying it and then deleting
    it
    :param dataset_manager: Dataset manager to work with
    """
    dataset = dataset_manager.create(IMPORT_URL, create_vis=True)
    assert dataset.get_id() is not None
    assert dataset.privacy == PRIVATE

    dataset_id = dataset.get_id()
    dataset = dataset_manager.get(dataset_id)
    dataset.privacy = PUBLIC
    dataset.save()

    dataset = dataset_manager.get(dataset_id)
    assert dataset.privacy == PUBLIC

    dataset.delete()
    with pytest.raises(NotFoundException):
        dataset_manager.get(dataset_id)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_create_and_modify_and_delete_dataset_from_url(dataset_manager):
    """
    Test creating a dataset from a remote URL, modifying it and then deleting
    it
    :param dataset_manager: Dataset manager to work with
    """
    dataset = dataset_manager.create(IMPORT_URL)
    assert dataset.get_id() is not None
    assert dataset.privacy == PRIVATE

    dataset_id = dataset.get_id()
    dataset = dataset_manager.get(dataset_id)
    dataset.privacy = PUBLIC
    dataset.save()

    dataset = dataset_manager.get(dataset_id)
    assert dataset.privacy == PUBLIC

    dataset.delete()
    with pytest.raises(NotFoundException):
        dataset_manager.get(dataset_id)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_create_and_modify_and_delete_dataset_as_sync_table(dataset_manager):
    """
    Test creating a dataset as a result of the creation of a sync table,
    modifying it and then deleting it
    :param dataset_manager: Dataset manager to work with
    """
    dataset = dataset_manager.create(IMPORT_URL, interval=3600)
    assert dataset.get_id() is not None

    dataset_id = dataset.get_id()
    dataset.delete()
    with pytest.raises(NotFoundException):
        dataset_manager.get(dataset_id)
