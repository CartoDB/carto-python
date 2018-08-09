carto-python
============


![](https://travis-ci.org/CartoDB/carto-python.svg?branch=master) [![Documentation Status](https://readthedocs.org/projects/carto-python/badge/?version=latest)](http://carto-python.readthedocs.io/en/latest/?badge=latest)




Python SDK for Carto's APIs:

* [SQL API](https://carto.com/docs/carto-engine/sql-api)
* [Import API](https://carto.com/docs/carto-engine/import-api)
* [Maps API](https://carto.com/docs/carto-engine/maps-api)

carto-python is a full, backwards incompatible rewrite of the deprecated [cartodb-python](https://github.com/CartoDB/cartodb-python/) SDK. Since the initial rewrite, carto-python has been loaded with a lot of new features, not present in old cartodb-python.

Installation
============

You can install carto-python by cloning this repository or by using
[Pip](http://pypi.python.org/pypi/pip):

    pip install carto

If you want to use the development version, you can install directly from github:

    pip install -e git+git://github.com/CartoDB/carto-python.git#egg=carto

If using, the development version, you might want to install Carto's dependencies as well:

    pip install -r requirements.txt

Test Suite
==========

Create a `secret.py` from `secret.py.example`, fill the variables, cd into the repo folder, create and enable virtualenv, install pytest and run tests:

```
cd carto-python
virtualenv env
source env/bin/activate
pip install -e .
pip install -r test_requirements.txt
pip install pytest
py.test tests
```

Authentication
==============

Before making API calls, we need to define how those calls are going to be authenticated. Currently, we support two different
authentication methods: unauthenticated and API key based. Therefore, we first need to create an _authentication client_ that will
be used when instantiating the Python classes that deal with API requests.

For unauthenticated requests, we need to create a NoAuthClient object:

```python
from carto.auth import NoAuthClient

USERNAME="type here your username"
USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
auth_client = NoAuthClient(base_url=USR_BASE_URL)
```

For API key authenticated requests, we need to create an APIKeyAuthClient instance:

```python
from carto.auth import APIKeyAuthClient

USERNAME="type here your username"
USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
auth_client = APIKeyAuthClient(api_key="myapikey", base_url=USR_BASE_URL)
```

API key is mandatory for all API requests except for sending SQL queries to public datasets.

The `base_url` parameter must include the `user` and or the `organization`

```
BASE_URL = "https://{organization}.carto.com/user/{user}/". \
    format(organization=ORGANIZATION,
           user=USERNAME)
USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
```

Additionally, see `test_auth.py` for supported formats for the `base_url` parameter.

For a detailed description of the rest of parameters both constructors accept, please take a look at the documentation of the source code.


SQL API
=======

Making requests to the SQL API is pretty straightforward:

```python
from carto.sql import SQLClient

sql = SQLClient(auth_client)

try:
    data = sql.send('select * from mytable')
except CartoException as e:
    print("some error ocurred", e)

print data['rows']
```

Please refer to the source code documentation to find out about the rest of the parameters accepted by the constructor and the `send` method.
In particular, the `send` method allows you to control the format of the results.

**Batch SQL requests**

For long lasting SQL queries you can use the batch SQL API.

```python
from carto.sql import BatchSQLClient

LIST_OF_SQL_QUERIES = []

batchSQLClient = BatchSQLClient(auth_client)
createJob = batchSQLClient.create(LIST_OF_SQL_QUERIES)

print(createJob['job_id'])
```

The `BatchSQLClient` is asynchronous, but it offers methods to check the status of a job, update it or cancel it:

```python

# check the status of a job after it has been created and you have the job_id
readJob = batchSQLClient.read(job_id)

# update the query of a batch job
updateJob = batchSQLClient.update(job_id, NEW_QUERY)

# cancel a job given its job_id
cancelJob = batchSQLClient.cancel(job_id)
```

**COPY queries**

COPY queries allow you to use the [PostgreSQL COPY command](https://www.postgresql.org/docs/10/static/sql-copy.html) for efficient streaming of data to and from CARTO.

Here is a basic example of its usage:

```python
from carto.sql import SQLClient
from carto.sql import CopySQLClient

sql_client = SQLClient(auth_client)
copy_client = CopySQLClient(auth_client)

# Create a destination table for the copy with the right schema
sql_client.send("""
    CREATE TABLE IF NOT EXISTS copy_example (
      the_geom geometry(Geometry,4326),
      name text,
      age integer
    )
    """)
sql_client.send("SELECT CDB_CartodbfyTable(current_schema, 'copy_example')")

# COPY FROM a csv file in the filesytem
from_query = 'COPY copy_example (the_geom, name, age) FROM stdin WITH (FORMAT csv, HEADER true)'
result = copy_client.copyfrom_file_path(from_query, 'copy_from.csv')

# COPY TO a file in the filesystem
to_query = 'COPY copy_example TO stdout WITH (FORMAT csv, HEADER true)'
copy_client.copyto_file_path(to_query, 'export.csv')
```

Here's an equivalent, more pythonic example of the COPY FROM, using a `file` object:

```python
with open('copy_from.csv', 'rb') as f:
    copy_client.copyfrom_file_object(from_query, f)
```

And here is a demonstration of how to generate and stream data directly (no need for a file at all):

```python
def rows():
    # note the \n to delimit rows
    yield bytearray(u'the_geom,name,age\n', 'utf-8')
    for i in range(1,80):
        row = u'SRID=4326;POINT({lon} {lat}),{name},{age}\n'.format(
            lon = i,
            lat = i,
            name = 'fulano',
            age = 100 - i
        )
        yield bytearray(row, 'utf-8')
copy_client.copyfrom(from_query, rows())
```

For more examples on how to use the SQL API, please refer to the **examples** folder or the API docs.

Import API
==========

You can import local or remote datasets into CARTO like this:

```python
from carto.datasets import DatasetManager

# write here the path to a local file or remote URL
LOCAL_FILE_OR_URL = ""

dataset_manager = DatasetManager(auth_client)
dataset = dataset_manager.create(LOCAL_FILE_OR_URL)
```

The Import API is asynchronous, but the `DatasetManager` waits a maximum of 150 seconds for the dataset to be uploaded, so once it finishes the dataset has been created in CARTO.

**Import a sync dataset**

You can do it in the same way as a regular dataset, just include a sync_time parameter with a value >= 900 seconds

```python
from carto.datasets import DatasetManager

# how often to sync the dataset (in seconds)
SYNC_TIME = 900
# write here the URL for the dataset to sync
URL_TO_DATASET = ""

dataset_manager = DatasetManager(auth_client)
dataset = dataset_manager.create(URL_TO_DATASET, SYNC_TIME)
```

Alternatively, if you need to do further work with the sync dataset, you can use the `SyncTableJobManager`

```python
from carto.sync_tables import SyncTableJobManager
import time

# how often to sync the dataset (in seconds)
SYNC_TIME = 900
# write here the URL for the dataset to sync
URL_TO_DATASET = ""

syncTableManager = SyncTableJobManager(auth_client)
syncTable = syncTableManager.create(URL_TO_DATASET, SYNC_TIME)

# return the id of the sync
sync_id = syncTable.get_id()

while(syncTable.state != 'success'):
    time.sleep(5)
    syncTable.refresh()
    if (syncTable.state == 'failure'):
        print('The error code is: ' + str(syncTable.error_code))
        print('The error message is: ' + str(syncTable.error_message))
        break

# force sync
syncTable.refresh()
syncTable.force_sync()
```

**Get a list of all the current import jobs**

```python
from carto.file_import import FileImportJobManager

file_import_manager = FileImportJobManager(auth_client)
file_imports = file_import_manager.all()
```

**Get all the datasets**

```python
from carto.datasets import DatasetManager

dataset_manager = DatasetManager(auth_client)
datasets = dataset_manager.all()
```

**Get a specific dataset**

```python
from carto.datasets import DatasetManager

# write here the ID of the dataset to retrieve
DATASET_ID = ""

dataset_manager = DatasetManager(auth_client)
dataset = dataset_manager.get(DATASET_ID)
```

**Update the properties of a dataset ([non-public API](#non-public-apis))**
```python
from carto.datasets import DatasetManager
from carto.permissions import PRIVATE, PUBLIC, LINK

# write here the ID of the dataset to retrieve
DATASET_ID = ""

dataset_manager = DatasetManager(auth_client)
dataset = dataset_manager.get(DATASET_ID)

# make the dataset PUBLIC
dataset.privacy = PUBLIC
dataset.save()
```

**Delete a dataset**

```python
from carto.datasets import DatasetManager

# write here the ID of the dataset to retrieve
DATASET_ID = ""

dataset_manager = DatasetManager(auth_client)
dataset = dataset_manager.get(DATASET_ID)
dataset.delete()
```

**Export a CARTO visualization ([non-public API](#non-public-apis))**

```python
from carto.visualizations import VisualizationManager

# write here the name of the map to export
MAP_NAME = ""

visualization_manager = VisualizationManager(auth_client)
visualization = visualization_manager.get(MAP_NAME)

url = visualization.export()

# the URL points to a .carto file
print(url)
```

Please refer to the source code documentation and the **examples** folder to find out about the rest of the parameters accepted by constructors and methods.

Maps API
========

The Maps API allows to create and instantiate named and anonymous maps:

```python
from carto.maps import NamedMapManager, NamedMap
import json

# write the path to a local file with a JSON named map template
JSON_TEMPLATE = ""

named_map_manager = NamedMapManager(auth_client)
named_map = NamedMap(named_map_manager.client)

with open(JSON_TEMPLATE) as named_map_json:
    template = json.load(named_map_json)

# Create named map
named = named_map_manager.create(template=template)
```

```python
from carto.maps import AnonymousMap
import json

# write the path to a local file with a JSON named map template
JSON_TEMPLATE = ""

anonymous = AnonymousMap(auth_client)
with open(JSON_TEMPLATE) as anonymous_map_json:
    template = json.load(anonymous_map_json)

# Create anonymous map
anonymous.instantiate(template)
```

**Instantiate a named map**

```python
from carto.maps import NamedMapManager, NamedMap
import json

# write the path to a local file with a JSON named map template
JSON_TEMPLATE = ""

# write here the ID of the named map
NAMED_MAP_ID = ""

# write here the token you set to the named map when created
NAMED_MAP_TOKEN = ""

named_map_manager = NamedMapManager(auth_client)
named_map = named_map_manager.get(NAMED_MAP_ID)

with open(JSON_TEMPLATE) as template_json:
    template = json.load(template_json)

named_map.instantiate(template, NAMED_MAP_TOKEN)
```

**Work with named maps**

```python
from carto.maps import NamedMapManager, NamedMap

# write here the ID of the named map
NAMED_MAP_ID = ""

# get the named map created
named_map = named_map_manager.get(NAMED_MAP_ID)

# update named map
named_map.view = None
named_map.save()

# delete named map
named_map.delete()

# list all named maps
named_maps = named_map_manager.all()
```

For more examples on how to use the Maps API, please refer to the **examples** folder or the API docs.

API Documentation
=================

API documentation is written with Sphinx. To build the API docs:

```
pip install sphinx
pip install sphinx_rtd_theme
cd doc
make html
```

Docs are generated inside the `doc/build/hmtl` folder. Please refer to them for a complete list of objects, functions and attributes of the carto-python API.

non-public APIs
===============

Non-public APIs may change in the future and will thrown a `warnings.warn` message when used.

Please be aware if you plan to run them on a production environment.

Refer to the API docs for a list of non-public APIs

Examples
========

Inside the `examples` folder there are sample code snippets of the carto-python client.

To run examples, you should need to install additional dependencies:

```
pip install -r examples/requirements.txt
```

carto-python examples need to setup environment variables.

- CARTO_ORG: The name of your organization
- CARTO_API_URL: The `base_url` including your user and/or organization
- CARTO_API_KEY: Your user API key

Please refer to the examples source code for additional info about parameters of each one
