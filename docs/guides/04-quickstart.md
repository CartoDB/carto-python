## Quickstart

In order to use the CARTO Python SDK first you have to follow the [installation guide]({{site.pythonsdk_docs}}/guides/installation/) and then write a Python script that makes use of it.

As an example, next code snippet makes a SQL query to a dataset

```python

  from carto.auth import APIKeyAuthClient
  from carto.exceptions import CartoException
  from carto.sql import SQLClient

  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key="myapikey", base_url=USR_BASE_URL)

  sql = SQLClient(auth_client)

  try:
      data = sql.send('select * from mytable')
  except CartoException as e:
      print("some error ocurred", e)

  print data['rows']
```
