from carto.models import DatasetManager


def test_get_datasets(api_key_auth_client, user):
    dataset_manager = DatasetManager(api_key_auth_client)
    datasets = dataset_manager.all()
    if user is not None:
        assert len(datasets) == user.table_count
    else:
        assert len(datasets) >= 0


def test_create_dataset(api_key_auth_client):
    dataset = DatasetManager.create("test/test.csv")
    assert dataset.id is not None
