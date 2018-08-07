import os
import pytest
import time
import random

# Make the tests compatible with python 2 and 3
try:
    # python 2
    from StringIO import cStringIO as InMemIO
except ImportError:
    # python 3
    from io import BytesIO as InMemIO

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
    assert 'relation "any_wrong_table" does not exist' in str(e.value)


IN_MEMORY_CSV_NROWS = 1000

@pytest.fixture()
def in_memory_csv(request):
    file_obj = InMemIO()

    def fin():
        file_obj.close()

    request.addfinalizer(fin)

    for i in range(IN_MEMORY_CSV_NROWS):
        row = u'SRID=4326;POINT({lon} {lat}),{name},{age}\n'.format(
            lon = random.uniform(-170.0, 170.0),
            lat = random.uniform(-80.0, 80.0),
            name = random.choice(['fulano', 'mengano', 'zutano', 'perengano']),
            age = random.randint(18,99)
        )
        file_obj.write(bytearray(row, 'utf-8'))
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




@pytest.fixture()
def copyto_sample_query():
    arbitrary_subquery = 'SELECT i cartodb_id, ST_AsEWKT(ST_SetSRID(ST_MakePoint(i, i),4326)) the_geom FROM generate_series(1,10) i'
    query = 'COPY ({subquery}) TO STDOUT'.format(subquery=arbitrary_subquery)
    return query

@pytest.fixture()
def copyto_expected_result():
    return bytearray(u'\n'.join([
        u'1\tSRID=4326;POINT(1 1)',
        u'2\tSRID=4326;POINT(2 2)',
        u'3\tSRID=4326;POINT(3 3)',
        u'4\tSRID=4326;POINT(4 4)',
        u'5\tSRID=4326;POINT(5 5)',
        u'6\tSRID=4326;POINT(6 6)',
        u'7\tSRID=4326;POINT(7 7)',
        u'8\tSRID=4326;POINT(8 8)',
        u'9\tSRID=4326;POINT(9 9)',
        u'10\tSRID=4326;POINT(10 10)\n'
    ]), 'utf-8')


def test_copyto(copy_client, copyto_sample_query, copyto_expected_result):
    response = copy_client.copyto(copyto_sample_query)

    result = bytearray()
    for block in response.iter_content(10):
        result += block

    assert result == copyto_expected_result

def test_copyto_file_object(copy_client, copyto_sample_query, copyto_expected_result):
    in_memory_target_fileobj = InMemIO()

    copy_client.copyto_file_object(copyto_sample_query, in_memory_target_fileobj)
    assert in_memory_target_fileobj.getvalue() == copyto_expected_result

    in_memory_target_fileobj.close()

def test_copyto_file_path(copy_client, copyto_sample_query, copyto_expected_result, tmpdir):
    target_path = tmpdir.join('carto-python-sdk-copy-test.dump')
    copy_client.copyto_file_path(copyto_sample_query, target_path.strpath)
    assert target_path.read() == copyto_expected_result.decode('utf-8')
