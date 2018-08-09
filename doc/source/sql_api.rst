SQL API
-------

Making requests to the `SQL API`_ is pretty straightforward:

::

  from carto.sql import SQLClient
  from carto.exceptions import CartoException

  sql = SQLClient(auth_client)

  try:
      data = sql.send('select * from mytable')
  except CartoException as e:
      print("some error ocurred", e)

  print data['rows']

POST and GET
^^^^^^^^^^^^

The CARTO SQL API is setup to handle both GET and POST requests.

By default all requests are sent via `POST`, anyway you still can send requests via `GET`:

::

  from carto.sql import SQLClient
  from carto.exceptions import CartoException

  sql = SQLClient(auth_client)

  try:
     data = sql.send('select * from mytable', do_post=False)
  except CartoException as e:
     print("some error ocurred", e)

  print data['rows']

Response formats
^^^^^^^^^^^^^^^^

The SQL API accepts many output formats that can be useful to export data, such as:

- CSV
- SHP
- SVG
- KML
- SpatiaLite
- GeoJSON

By default, requests are sent in `JSON` format, but you can specify a different format like this:

::

  from carto.sql import SQLClient

  sql = SQLClient(auth_client)

  try:
      result = sql.send('select * from mytable', format='csv')
      # here you have a CSV, proceed to do what it takes with it
  except CartoException as e:
      print("some error ocurred", e)


Please refer to the :ref:`apidoc` to find out about the rest of the parameters accepted by the constructor and the `send` method.


Batch SQL requests
^^^^^^^^^^^^^^^^^^

For long lasting SQL queries you can use the `batch SQL API`_.

.. _batch SQL API: https://carto.com/docs/carto-engine/sql-api/batch-queries

::

  from carto.sql import BatchSQLClient

  LIST_OF_SQL_QUERIES = []

  batchSQLClient = BatchSQLClient(auth_client)
  createJob = batchSQLClient.create(LIST_OF_SQL_QUERIES)

  print(createJob['job_id'])


The `BatchSQLClient` is asynchronous, but it offers methods to check the status of a job, update it or cancel it:

::

  # check the status of a job after it has been created and you have the job_id
  readJob = batchSQLClient.read(job_id)

  # update the query of a batch job
  updateJob = batchSQLClient.update(job_id, NEW_QUERY)

  # cancel a job given its job_id
  cancelJob = batchSQLClient.cancel(job_id)



COPY queries
^^^^^^^^^^^^

COPY queries allow you to use the `PostgreSQL COPY command`_ for
efficient streaming of data to and from CARTO.

.. _PostgreSQL COPY command: https://www.postgresql.org/docs/10/static/sql-copy.html

Here is a basic example of its usage:

.. code:: python

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

Here’s an equivalent, more pythonic example of the COPY FROM, using a
``file`` object:

.. code:: python

   with open('copy_from.csv', 'rb') as f:
       copy_client.copyfrom_file_object(from_query, f)

And here is a demonstration of how to generate and stream data directly
(no need for a file at all):

.. code:: python

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

For more examples on how to use the SQL API, please refer to the **examples** folder or the :ref:`apidoc`.
