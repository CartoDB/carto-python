import os
import pytest
import time

from carto.exceptions import CartoException
from carto.sql import SQLClient, BatchSQLClient
from secret import EXISTING_POINT_DATASET, BATCH_SQL_SINGLE_QUERY, \
    BATCH_SQL_MULTI_QUERY


def test_sql_error(api_key_auth_client_usr):
    sql = SQLClient(api_key_auth_client_usr)

    with pytest.raises(CartoException):
        sql.send('select * from non_existing_dataset')


def test_sql_error_get(api_key_auth_client_usr):
    sql = SQLClient(api_key_auth_client_usr)

    with pytest.raises(CartoException):
        sql.send('select * from non_existing_dataset', {'do_post': False})


def test_sql(api_key_auth_client_usr, mock_requests, do_post=True):
    with mock_requests.mocker:
        sql = SQLClient(api_key_auth_client_usr)
        data = sql.send('select * from ' + EXISTING_POINT_DATASET,
                        do_post=do_post)

    assert data is not None
    assert 'rows' in data
    assert 'total_rows' in data
    assert 'time' in data
    assert len(data['rows']) > 0


def test_sql_get(api_key_auth_client_usr, mock_requests):
    test_sql(api_key_auth_client_usr, mock_requests, do_post=False)


def test_no_api_key(no_auth_client):
    assert hasattr(no_auth_client, "api_key") is False


def test_no_auth_sql_error(no_auth_client):
    sql = SQLClient(no_auth_client)

    with pytest.raises(CartoException):
        sql.send('select * from non_existing_dataset')


def test_no_auth_sql_error_get(no_auth_client):
    sql = SQLClient(no_auth_client)

    with pytest.raises(CartoException):
        sql.send('select * from non_existing_dataset', {'do_post': False})


def cancel_job_if_not_finished(batch_sql_client, job_id):
    status = batch_sql_client.cancel(job_id)
    attempts = 1
    while status != 'done' and status != 'cancelled' and attempts < 3:
        time.sleep(1)
        status = batch_sql_client.cancel(job_id)
        attempts += 1
    assert status == 'done' or status == 'cancelled'


def test_batch_create_and_wait_for_completion(api_key_auth_client_usr):
    sql = BatchSQLClient(api_key_auth_client_usr)

    # Create query
    data = sql.create_and_wait_for_completion(BATCH_SQL_SINGLE_QUERY)

    assert data['status'] in ['done', 'failed', 'canceled', 'unknown']

def test_batch_create(api_key_auth_client_usr):
    sql = BatchSQLClient(api_key_auth_client_usr)

    # Create query
    data = sql.create(BATCH_SQL_SINGLE_QUERY)

    # Get job ID
    job_id = data['job_id']

    # Cancel if not finished
    cancel_job_if_not_finished(sql, job_id)


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true",
                    reason="Integration tests not executed in Travis")
def test_batch_multi_sql(api_key_auth_client_usr):
    sql = BatchSQLClient(api_key_auth_client_usr)

    # Create query
    data = sql.create(BATCH_SQL_MULTI_QUERY)

    # Get job ID
    job_id = data['job_id']

    # Cancel if not finished
    cancel_job_if_not_finished(sql, job_id)


def test_sql_unverified(non_verified_auth_client):
    if non_verified_auth_client is None:
        assert True is True
        return

    sql = SQLClient(non_verified_auth_client)
    data = sql.send('select version()')

    assert data is not None
    assert 'rows' in data
    assert 'total_rows' in data
    assert 'time' in data
    assert len(data['rows']) > 0


def test_sql_unverified_fails_with_auth_client(wrong_onprem_auth_client):
    if wrong_onprem_auth_client is None:
        assert True is True
        return

    sql = SQLClient(wrong_onprem_auth_client)
    with pytest.raises(CartoException):
        data = sql.send('select version()')


def test_sql_additional_params(api_key_auth_client_usr):
    sql = SQLClient(api_key_auth_client_usr)
    request_args = {
        "skipfields": "the_geom_webmercator"
    }
    data = sql.send('select * from ' + EXISTING_POINT_DATASET,
                        do_post=True, **request_args)

    assert data is not None
    assert 'rows' in data
    assert 'total_rows' in data
    assert 'time' in data
    assert len(data['rows']) > 0
    assert "the_geom_webmercator" not in data['rows'][0]

    data = sql.send('select * from ' + EXISTING_POINT_DATASET,
                        do_post=True)

    assert "the_geom_webmercator" in data['rows'][0]
