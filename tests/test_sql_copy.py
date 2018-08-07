import os
import pytest
import time
import cStringIO
import random

from carto.exceptions import CartoException
from carto.sql import SQLClient, BatchSQLClient, CopySQLClient

SETUP_QUERIES = [
    'DROP TABLE IF EXISTS carto_python_sdk_copy_test',
    """
    CREATE TABLE carto_python_sdk_copy_test (
      the_geom geometry(Geometry,4326),
      name text,
      age integer
    )
    """,
    "SELECT CDB_CartodbfyTable(current_schema, 'carto_python_sdk_copy_test')"
]
BATCH_TERMINAL_STATES = ['done', 'failed', 'cancelled', 'unknown']

# Please note the newline characters to delimit rows
TABLE_CONTENTS=[
    b'the_geom,name,age\n',
    b'SRID=4326;POINT(-126 54),North West,89\n',
    b'SRID=4326;POINT(-96 34),South East,99\n',
    b'SRID=4326;POINT(-6 -25),Souther Easter,124\n'
]


@pytest.fixture(scope="module")
def test_table(api_key_auth_client_usr):
    batch_client = BatchSQLClient(api_key_auth_client_usr)
    job = batch_client.create(SETUP_QUERIES)
    while not job['status'] in BATCH_TERMINAL_STATES:
        time.sleep(1)
        job = batch_client.read(job['job_id'])
    assert job['status'] == 'done'

@pytest.fixture
def copy_client(api_key_auth_client_usr):
    return CopySQLClient(api_key_auth_client_usr)


def test_copyfrom(copy_client):
    query = 'COPY carto_python_sdk_copy_test (the_geom, name, age) FROM stdin WITH (FORMAT csv, HEADER true)'
    data = iter(TABLE_CONTENTS)
    result = copy_client.copyfrom(query, data)

    assert result['total_rows'] == 3


def test_copyfrom_no_compression(copy_client):
    query = 'COPY carto_python_sdk_copy_test (the_geom, name, age) FROM stdin WITH (FORMAT csv, HEADER true)'
    data = iter(TABLE_CONTENTS)
    result = copy_client.copyfrom(query, data, compress=False)

    assert result['total_rows'] == 3

def test_copyfrom_wrong_query(copy_client):
    query = 'COPY any_wrong_table (any_wrong_column) FROM stdin'
    data = iter(TABLE_CONTENTS)
    with pytest.raises(CartoException) as e:
        copy_client.copyfrom(query, data)
    assert 'relation "any_wrong_table" does not exist' in e.value.message.message


IN_MEMORY_CSV_NROWS = 1000

@pytest.fixture()
def in_memory_csv(request):
    file_obj = cStringIO.StringIO()

    def fin():
        file_obj.close()

    request.addfinalizer(fin)

    for i in xrange(IN_MEMORY_CSV_NROWS):
        row = 'SRID=4326;POINT({lon} {lat}),{name},{age}\n'.format(
            lon = random.uniform(-170.0, 170.0),
            lat = random.uniform(-80.0, 80.0),
            name = random.choice(['fulano', 'mengano', 'zutano', 'perengano']),
            age = random.randint(18,99)
        )
        file_obj.write(row)
    file_obj.seek(0)
    return file_obj

def test_copyfrom_file_object(copy_client, in_memory_csv):
    query = 'COPY carto_python_sdk_copy_test (the_geom, name, age) FROM stdin WITH (FORMAT csv, HEADER false)'
    result = copy_client.copyfrom_file_object(query, in_memory_csv)

    assert result['total_rows'] == IN_MEMORY_CSV_NROWS

def test_copyfrom_file_path(copy_client):
    query = 'COPY carto_python_sdk_copy_test (the_geom, name, age) FROM stdin WITH (FORMAT csv, HEADER true)'
    result = copy_client.copyfrom_file_path(query, 'tests/copy_from.csv')

    assert result['total_rows'] == 3
