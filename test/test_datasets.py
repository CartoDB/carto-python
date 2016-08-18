import pytest

from carto.models import DatasetManager, PRIVATE, PUBLIC


@pytest.fixture(scope="module")
def dataset_manager(api_key_auth_client):
    """
    Returns a dataset manager that can be reused in tests
    :param api_key_auth_client: Fixture that provides a valid APIKeyAuthClient object
    :return: DataManager instance
    """
    return DatasetManager(api_key_auth_client)


def test_get_datasets(dataset_manager, user):
    """
    Currently not supported by the user API. If we actually tried to perform this test, an exception would be raised
    :param dataset_manager: Fixture that provides a user manager to work with
    :param user: If valid, we'll check the number of returned datasets exactly against the expected value
    """
    datasets = dataset_manager.all()

    # If are testing against an enterprise account and have a valid user, we can easily know how many datasets to expect
    if user is not None:
        assert len(datasets) == user.table_count
    else:
        assert len(datasets) >= 0


def test_create_and_modify_and_delete_dataset(dataset_manager):
    """
    Test creating a dataset, modifying it and then deleting it
    :param dataset_manager: Dataset manager to work with
    """
    dataset = dataset_manager.create("test/test.csv")
    assert dataset._id is not None
    assert dataset.privacy == PRIVATE

    dataset_id = dataset._id
    dataset = dataset_manager.get(dataset_id)
    dataset.privacy = PUBLIC
    dataset.save()

    dataset = dataset_manager.get(dataset_id)
    assert dataset.privacy == PUBLIC

    dataset.delete()
    assert dataset._id is None
    assert dataset_manager.get(dataset_id) is None
