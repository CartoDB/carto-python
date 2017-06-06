.. _examples:

Examples
========

This developer guide is not intended to be an extensive list of usage examples and use cases. For that, inside the `examples` folder of the `carto-python`_ Github repository there are sample code snippets of the carto-python client.

.. _carto-python: https://github.com/CartoDB/carto-python

To run examples, you should need to install additional dependencies:

::

  pip install -r examples/requirements.txt


carto-python examples need to setup environment variables.

- CARTO_ORG: The name of your organization
- CARTO_API_URL: The `base_url` including your user and/or organization
- CARTO_API_KEY: Your user API key

Please refer to the examples source code for additional info about parameters of each one

List of examples
----------------

Find below a list of provided examples of the `carto-python` library.

Take into account that the examples are not intended to provide a comprehensive list of the capabilities of `carto-python` but only some of its use cases.

`change_dataset_privacy.py`
^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Changes the privacy of a user's dataset to 'LINK', 'PUBLIC' or 'PRIVATE'

**Usage example**:

::

  python change_dataset_privacy.py tornados LINK

**Output**:

::

  12:17:01 PM - INFO - Done!

`check_query.py`
^^^^^^^^^^^^^^^^

**Description**: Analyzes an SQL query to check if it can be optimized

**Usage example**:

::

  python check_query.py "select version()"

**Output**:

::

  12:25:18 PM - INFO - {u'QUERY PLAN': u'Result  (cost=0.00..0.00 rows=1 width=0) (actual time=0.002..0.002 rows=1 loops=1)'}
  12:25:18 PM - INFO - {u'QUERY PLAN': u'Planning time: 0.006 ms'}
  12:25:18 PM - INFO - {u'QUERY PLAN': u'Execution time: 0.008 ms'}
  12:25:18 PM - INFO - time: 0.002

`create_anonymous_map.py`
^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Creates an anonymous map

**Usage example**:

::

  python create_anonymous_map.py "files/anonymous_map.json"

**Output**:

::

  Anonymous map created with layergroupid: 50b159d8a635c94fdfd100bdc7d8fb08:1493192847307

`create_named_map.py`
^^^^^^^^^^^^^^^^^^^^^

**Description**: Creates an anonymous map

**Usage example**:

::

  python create_named_map.py "files/named_map.json"

**Output**:

::

  Named map created with ID: python_sdk_test_map

`export_create_tables.py`
^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Runs a SQL query to export the `CREATE TABLE` scripts of the user's datasets

**Usage example**:

::

  python export_create_datasets.py

**Output**:

::

  ...
  Found dataset: test_12
  Found dataset: tornados_24

  Script exported

`export_dataset.py`
^^^^^^^^^^^^^^^^^^^

**Description**: Exports a `dataset` in a given `format`

**Usage example**:

::

  python export_dataset.py --dataset=tornados --format=csv

**Output**:

::

  File saved: tornados.csv

`export_map.py`
^^^^^^^^^^^^^^^

**Description**: Exports a map visualization as a .carto file

**Usage example**:

::

  python export_map.py "Untitled map"

**Output**:

::

  URL of .carto file is: http://s3.amazonaws.com/com.cartodb.imports.production/ ... .carto

`import_and_merge.py`
^^^^^^^^^^^^^^^^^^^^^

**Description**: Import a folder with CSV files (same structure) and merge them into one dataset. Files must be named as file1.csv, file2.csv, file3.csv, etc.

**Usage example**:

::

  python import_and_merge.py "files/*.csv"

**Output**:

::

  12:37:42 PM - INFO - Table imported: barris_barcelona_1_part_1
  12:37:53 PM - INFO - Table imported: barris_barcelona_1_part_2
  12:38:05 PM - INFO - Table imported: barris_barcelona_1_part_3
  12:38:16 PM - INFO - Table imported: barris_barcelona_1_part_4
  12:38:27 PM - INFO - Table imported: barris_barcelona_1_part_5
  12:38:38 PM - INFO - Table imported: barris_barcelona_1_part_6
  12:38:49 PM - INFO - Table imported: barris_barcelona_1_part_7
  12:39:22 PM - INFO - Tables merged

  URL of dataset is:       https://YOUR_ORG.carto.com/u/YOUR_USER/dataset/barris_barcelona_1_part_1_merged

`import_from_database.py`
^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: External database connector

**Usage example**:

::

  python import_from_database.py --connection='{
    "connector": {
      "provider": "hive",
      "connection": {
        "server":"YOUR_SERVER_IP",
        "database":"default",
        "username":"cloudera",
        "password":"cloudera"
      },
      "schema": "default",
      "table": "YOUR_TABLE"
    }
  }'

**Output**:

::

  Table imported: YOUR_TABLE

`import_standard_table.py`
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Creates a CARTO dataset from a URL

**Usage example**:

::

  python import_standard_table.py files/barris_barcelona_1_part_1.csv

**Output**:

::

  12:46:00 PM - INFO - Name of table: barris_barcelona_1_part_1
  URL of dataset:       https://YOUR_ORG.carto.com/u/YOUR_USER/dataset/barris_barcelona_1_part_1

`import_sync_table_as_dataset.py`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Creates a CARTO sync dataset from a URL

**Usage example**:

::

  python import_sync_table_as_dataset.py "https://academy.cartodb.com/d/tornadoes.zip" 900

**Output**:

::

  12:48:08 PM - INFO - Name of table: tornados
  URL of dataset is:       https://YOUR_ORG.carto.com/u/YOUR_USER/dataset/tornados

`import_sync_table.py`
^^^^^^^^^^^^^^^^^^^^^^

**Description**: Creates a CARTO sync dataset from a URL

**Usage example**:

::

  python import_sync_table.py "https://academy.cartodb.com/d/tornadoes.zip" 900

`instantiate_named_map.py`
^^^^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Instantiates a named map

**Usage example**:

::

  python instantiate_named_map.py "python_sdk_test_map" "files/instantiate_map.json" "example_token"

**Output**:

::

  Done!

`kill_query.py`
^^^^^^^^^^^^^^^

**Description**: Kills a running query

**Usage example**:

::

  python kill_query.py 999

**Output**:

::

  Query killed

`list_tables.py`
^^^^^^^^^^^^^^^^

**Description**: Returns graph of tables ordered by size and indicating if they are cartodbfied or not

**Usage example**:

::

  python list_tables.py

**Output**:

::

  ...
  analysis_a08f3b6124_a49b778b1e146f4bc7e5e670f5edcb027513ddc5 NO:	 | 0.01 MB;
  analysis_971639c870_c0421831d5966bcff0731772b21d6835294c4b0a NO:	 | 0.01 MB;
  analysis_9e88a1147e_5da714d5786b61509da4ebcd1409aae05ea8704d NO:	 | 0.01 MB;
  testing_moving                                               NO:	 | 0.0 MB;
  analysis_7530d60ffc_868bfea631fa1dc8c212ad2a8a950e050607aa6c NO:	 | 0.0 MB;

  There are: 338 datasets in this account

`map_info.py`
^^^^^^^^^^^^^

**Description**: Return the names of all maps or display information from a specific map

**Usage example**:

::

  python map_info.py

**Output**:

::

  12:58:28 PM - INFO - data_2_1_y_address_locations map 1
  12:58:28 PM - INFO - Untitled Map 2
  12:58:28 PM - INFO - Untitled map
  12:58:28 PM - INFO - Untitled Map
  12:58:28 PM - INFO - cartodb_germany 1
  12:58:28 PM - INFO - cb_2013_us_county_500k 1

**Usage example**:

::

  python map_info.py --map="Untitled map"

**Output**:

::

  { 'active_layer_id': u'5a89b00d-0a86-4a8d-a359-912458ad05c9',
    'created_at': u'2016-07-11T08:50:15+00:00',
    'description': None,
    'display_name': None,
    'id': u'7cb87e6a-4744-11e6-9b1b-0e3ff518bd15',
    'liked': False,
    'likes': 0,
    'locked': False,
    'map_id': u'7820995a-98b8-4465-9c3d-607fd5f6fa67',
    'name': u'Untitled map',
    'related_tables': [<carto.tables.Table object at 0x10aece5d0>],
    'table': <carto.tables.Table object at 0x10acb6c90>,
    'title': None,
    'updated_at': u'2016-07-11T08:50:19+00:00',
    'url': u'https://YOUR_ORG.carto.com/u/YOUR_USER/viz/7cb87e6a-4744-11e6-9b1b-0e3ff518bd15/map'
  }

`running_queries.py`
^^^^^^^^^^^^^^^^^^^^

**Description**: Returns the running queries of the account

**Usage example**:

::

  python running_queries.py

**Output**:

::

  01:00:49 PM - INFO - {u'query': u'select pid, query from pg_stat_activity  WHERE usename = current_user', u'pid': 2810}

`sql_batch_api_jobs.py`
^^^^^^^^^^^^^^^^^^^^^^^

**Description**: Works with a Batch SQL API job

**Usage example**:

::

  python sql_batch_api_jobs.py create --query="select CDB_CreateOverviews('my_table'::regclass)"

**Output**:

::

  01:03:07 PM - INFO - status: pending
  01:03:07 PM - INFO - job_id: 3a73d74d-cc7a-4faf-9c37-1bec05f4835e
  01:03:07 PM - INFO - created_at: 2017-06-06T11:03:07.746Z
  01:03:07 PM - INFO - updated_at: 2017-06-06T11:03:07.746Z
  01:03:07 PM - INFO - user: YOUR_USER
  01:03:07 PM - INFO - query: select CDB_CreateOverviews('my_table'::regclass)

**Usage example**:

::

  python sql_batch_api_jobs.py read --job_id=3a73d74d-cc7a-4faf-9c37-1bec05f4835e

**Output**:

::

  01:04:03 PM - INFO - status: done
  01:04:03 PM - INFO - job_id: 3a73d74d-cc7a-4faf-9c37-1bec05f4835e
  01:04:03 PM - INFO - created_at: 2017-06-06T11:03:07.746Z
  01:04:03 PM - INFO - updated_at: 2017-06-06T11:03:08.328Z
  01:04:03 PM - INFO - user: YOUR_USER
  01:04:03 PM - INFO - query: select CDB_CreateOverviews('my_table'::regclass)

**Usage example**:

::

  python sql_batch_api_jobs.py cancel --job_id=3a73d74d-cc7a-4faf-9c37-1bec05f4835e

**Output**:

::

  01:04:03 PM - INFO - status: cancelled
  01:04:03 PM - INFO - job_id: 3a73d74d-cc7a-4faf-9c37-1bec05f4835e
  01:04:03 PM - INFO - created_at: 2017-06-06T11:03:07.746Z
  01:04:03 PM - INFO - updated_at: 2017-06-06T11:03:08.328Z
  01:04:03 PM - INFO - user: YOUR_USER
  01:04:03 PM - INFO - query: select CDB_CreateOverviews('my_table'::regclass)

`table_info.py`
^^^^^^^^^^^^^^^

**Description**: Return columns and its types, indexes, functions and triggers of a specific table

**Usage example**:

::

  python table_info.py tornados

**Output**:

::

  General information
  +------------+----------------+------------------------+----------------------+---------------+
  | Table name | Number of rows | Size of the table (MB) | Privacy of the table | Geometry type |
  +------------+----------------+------------------------+----------------------+---------------+
  |  tornados  |     14222      |          2.03          |        PUBLIC        | [u'ST_Point'] |
  +------------+----------------+------------------------+----------------------+---------------+

  The columns and their data types are:

  +----------------------+------------------+
  | Column name          |        Data type |
  +----------------------+------------------+
  | cartodb_id           |           bigint |
  | the_geom             |     USER-DEFINED |
  | the_geom_webmercator |     USER-DEFINED |
  | latitude             | double precision |
  | longitude            | double precision |
  | damage               |          numeric |
  | _feature_count       |          integer |
  +----------------------+------------------+

  Indexes of the tables:

  +-----------------------------------+----------------------------------------------------------------------------------------------+
  | Index name                        |                                                                             Index definition |
  +-----------------------------------+----------------------------------------------------------------------------------------------+
  | _auto_idx_tornados_damage         |                      CREATE INDEX _auto_idx_tornados_damage ON tornados USING btree (damage) |
  | tornados_the_geom_webmercator_idx | CREATE INDEX tornados_the_geom_webmercator_idx ON tornados USING gist (the_geom_webmercator) |
  | tornados_the_geom_idx             |                         CREATE INDEX tornados_the_geom_idx ON tornados USING gist (the_geom) |
  | tornados_pkey                     |                       CREATE UNIQUE INDEX tornados_pkey ON tornados USING btree (cartodb_id) |
  +-----------------------------------+----------------------------------------------------------------------------------------------+

  Functions of the account:

  +---------------+
  | Function name |
  +---------------+
  +---------------+

  Triggers of the account:

  +-------------------------------------+
  |             Trigger Name            |
  +-------------------------------------+
  |              test_quota             |
  |          test_quota_per_row         |
  |            track_updates            |
  | update_the_geom_webmercator_trigger |
  +-------------------------------------+

`user_info.py`
^^^^^^^^^^^^^^

**Description**: Returns information from a specific user

**Usage example**:

::

  export CARTO_USER=YOUR_USER
  python user_info.py

**Output**:

::

  The attributes of the user are:

  +----------------------------+----------------------------------------------------------------------------------------------------------+
  | Attribute                  | Value                                                                                                    |
  +----------------------------+----------------------------------------------------------------------------------------------------------+
  | username                   | YOUR_USER                                                                                                |
  | avatar_url                 | //cartodb-libs.global.ssl.fastly.net/cartodbui/assets/unversioned/images/avatars/avatar_pacman_green.png |
  | quota_in_bytes             | 20198485636                                                                                              |
  | public_visualization_count | 0                                                                                                        |
  | base_url                   | https://YOUR_ORG.carto.com/u/YOUR_USER                                                                   |
  | table_count                | 217                                                                                                      |
  | all_visualization_count    | 80                                                                                                       |
  | client                     | <carto.auth.APIKeyAuthClient object at 0x102eac710>                                                      |
  | soft_geocoding_limit       | True                                                                                                     |
  | db_size_in_bytes           | 13867610112                                                                                              |
  | email                      | XXX@yyy.zzz                                                                                   |
  +----------------------------+----------------------------------------------------------------------------------------------------------+

  The quotas of the user are:

  +----------------+----------+------------------+------------+---------------+
  |        Service | Provider |       Soft limit | Used quota | Monthly quota |
  +----------------+----------+------------------+------------+---------------+
  |       isolines |       37 |         heremaps | False      |        100000 |
  | hires_geocoder |    20238 |         heremaps | False      |        100000 |
  |        routing |        0 |           mapzen | False      |        200000 |
  |    observatory |   482896 | data observatory | False      |       1000000 |
  +----------------+----------+------------------+------------+---------------+
