import pytest
import uuid
from io import StringIO

from carto.do_dataset import DODataset, DODatasetJob, VALID_TYPES
from carto.auth import APIKeyAuthClient
from carto.utils import ResponseStream

CSV_SAMPLE_REDUCED = u"""id,geom
1,POINT (-170.5618796 -14.2587411)
2,POINT (-170.5589852 -14.2859572)
3,POINT (-170.6310985 -14.2760947)
4,POINT (-170.6651925 -14.2713653)
5,POINT (-170.701028 -14.252446)
"""


class ResponseMock:
    def __init__(self, response=None):
        self._response = response

    def raise_for_status(self):
        pass

    def json(self):
        return self._response

    def iter_content(self, value):
        return iter(self._response)


class DataFrameMock:
    def __init__(self, response=None):
        self._response = response

    def to_csv(self, path_or_buf, index=False):
        f = open(path_or_buf, "a")
        f.write(str(self._response))
        f.close()


def test_DODataset_name(api_key_auth_client_usr):
    bq_user_dataset = DODataset(auth_client=api_key_auth_client_usr)

    name = 'fake-name'
    result = bq_user_dataset.name(name)
    assert bq_user_dataset == result
    assert bq_user_dataset._name == name


def test_DODataset_column(api_key_auth_client_usr):
    bq_user_dataset = DODataset(auth_client=api_key_auth_client_usr)

    invalid_cases = [
        {
            'column_name': 'fake-name',
            'column_type': 'fake-type'
        }
    ]

    for c in invalid_cases:
        with pytest.raises(Exception) as e:
            bq_user_dataset.column(c['column_name'], c['column_type'])
        assert str(e.value) == 'Invalid type {}'.format(c['column_type'].upper())

    column_name = 'column'
    column_type = VALID_TYPES[0]
    result = bq_user_dataset.column(column_name, column_type)
    assert bq_user_dataset == result
    assert bq_user_dataset._columns == [(column_name, column_type)]


def test_DODataset_ttl_seconds(api_key_auth_client_usr):
    bq_user_dataset = DODataset(auth_client=api_key_auth_client_usr)

    ttl_seconds = 10
    result = bq_user_dataset.ttl_seconds(ttl_seconds)
    assert bq_user_dataset == result
    assert bq_user_dataset._ttl_seconds == ttl_seconds


def test_can_upload_from_dataframe(mocker, api_key_auth_client_usr):
    # mock
    fake_response = ResponseMock()
    mocker.patch.object(APIKeyAuthClient, 'send', return_value=fake_response)

    bq_user_dataset = DODataset(auth_client=api_key_auth_client_usr)

    # test
    sample = StringIO(CSV_SAMPLE_REDUCED)
    df = DataFrameMock(sample)
    unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
    result = bq_user_dataset.name(unique_table_name).upload(df)
    assert result == fake_response


def test_can_upload_from_file_object(mocker, api_key_auth_client_usr):
    # mock
    fake_response = ResponseMock()
    mocker.patch.object(APIKeyAuthClient, 'send', return_value=fake_response)

    bq_user_dataset = DODataset(auth_client=api_key_auth_client_usr)

    # test
    unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
    file_object = StringIO(CSV_SAMPLE_REDUCED)
    result = bq_user_dataset.name(unique_table_name).upload_file_object(file_object)
    assert result == fake_response


def test_can_import_a_dataset(mocker, api_key_auth_client_usr):
    # mock
    fake_response = ResponseMock({'item_queue_id': '123'})
    mocker.patch.object(APIKeyAuthClient, 'send', return_value=fake_response)

    bq_user_dataset = DODataset(auth_client=api_key_auth_client_usr)

    # test
    unique_table_name = 'cf_test_table_' + str(uuid.uuid4()).replace('-', '_')
    file_object = StringIO(CSV_SAMPLE_REDUCED)

    dataset = bq_user_dataset.name(unique_table_name) \
        .column(name='id', type='INT64') \
        .column('geom', 'GEOMETRY') \
        .ttl_seconds(30)
    dataset.create()
    dataset.upload_file_object(file_object)
    job = dataset.import_dataset()

    assert isinstance(job, DODatasetJob)


def test_can_download_to_dataframe(mocker, api_key_auth_client_usr):
    # mock
    fake_response = ResponseMock(StringIO(CSV_SAMPLE_REDUCED))
    mocker.patch.object(APIKeyAuthClient, 'send', return_value=fake_response)

    bq_user_dataset = DODataset(auth_client=api_key_auth_client_usr)

    # test
    result = bq_user_dataset.name('census_tracts_american_samoa').download_stream()
    assert isinstance(result, ResponseStream)
