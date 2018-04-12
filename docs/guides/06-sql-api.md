## SQL API

Making requests to the `SQL API`_ is pretty straightforward:

```python

  from carto.sql import SQLClient
  from carto.exceptions import CartoException

  sql = SQLClient(auth_client)

  try:
      data = sql.send('select * from mytable')
  except CartoException as e:
      print("some error ocurred", e)

  print data['rows']

**Tip:** If you want to learn more about SQL API, browse its [guides]({{site.sqlapi_docs}}/guides/) and [reference]({{site.sqlapi_docs}}/reference/).

### POST and GET

The CARTO SQL API is setup to handle both GET and POST requests.

By default all requests are sent via `POST`, anyway you still can send requests via `GET`:

```python

  from carto.sql import SQLClient
  from carto.exceptions import CartoException

  sql = SQLClient(auth_client)

  try:
     data = sql.send('select * from mytable', do_post=False)
  except CartoException as e:
     print("some error ocurred", e)

  print data['rows']
```

### Response formats

The SQL API accepts many output formats that can be useful to export data, such as:

- CSV
- SHP
- SVG
- KML
- SpatiaLite
- GeoJSON

By default, requests are sent in `JSON` format, but you can specify a different format like this:

```python

  from carto.sql import SQLClient

  sql = SQLClient(auth_client)

  try:
      result = sql.send('select * from mytable', format='csv')
      # here you have a CSV, proceed to do what it takes with it
  except CartoException as e:
      print("some error ocurred", e)
```

Please refer to the [reference]({{site.pythonsdk_docs}}/reference/) to find out about the rest of the parameters accepted by the constructor and the `send` method.


### Batch SQL requests

For long lasting SQL queries you can use the `batch SQL API`.

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

For more examples on how to use the SQL API, please refer to the [examples]({{pythonsdk_docs}}/examples/) section.
