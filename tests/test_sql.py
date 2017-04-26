import pytest
import requests

from carto.exceptions import CartoException
from carto.sql import SQLClient, BatchSQLClient
from secret import EXISTING_POINT_DATASET, BATCH_SQL_SINGLE_QUERY, BATCH_SQL_MULTI_QUERY

import logging

logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def test_sql_error(api_key_auth_client_usr):
    sql = SQLClient(api_key_auth_client_usr)

    with pytest.raises(CartoException):
        sql.send('select * from non_existing_dataset')


def test_sql_error_get(api_key_auth_client_usr):
    sql = SQLClient(api_key_auth_client_usr)

    with pytest.raises(CartoException):
        sql.send('select * from non_existing_dataset', {'do_post': False})


def test_sql(api_key_auth_client_usr, do_post=True):
    sql = SQLClient(api_key_auth_client_usr)

    data = sql.send('select * from ' + EXISTING_POINT_DATASET, do_post=do_post)

    assert data is not None
    assert 'rows' in data
    assert 'total_rows' in data
    assert 'time' in data
    assert len(data['rows']) > 0


def test_sql_get(api_key_auth_client_usr):
    test_sql(api_key_auth_client_usr, do_post=False)


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


def test_batch_create(api_key_auth_client_usr):
    sql = BatchSQLClient(api_key_auth_client_usr)

    # Create query
    data = sql.create(BATCH_SQL_SINGLE_QUERY)

    # Update status
    job_id = data['job_id']

    # Cancel if not finished
    try:
        confirmation = sql.cancel(job_id)
    except CartoException:
        pass
    else:
        assert confirmation == 'cancelled'


def test_batch_multi_sql(api_key_auth_client_usr):
    sql = BatchSQLClient(api_key_auth_client_usr)

    # Create query
    data = sql.create(BATCH_SQL_MULTI_QUERY)

    # Update status
    job_id = data['job_id']

    # Cancel if not finished
    try:
        confirmation = sql.cancel(job_id)
    except CartoException:
        pass
    else:
        assert confirmation == 'cancelled'