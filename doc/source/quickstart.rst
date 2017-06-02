Quickstart
==========

In order to use the CARTO Python client first you have to follow the :ref:`installation` guide and then write a Python script that makes use of it.

As an example, next code snippet makes a SQL query to a dataset

::

  from carto.auth import APIKeyAuthClient
  from carto.sql import SQLCLient

  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key="myapikey", base_url=USR_BASE_URL)

  sql = SQLCLient(auth_client)

  try:
      sql.send('select * from mytable')
  except CartoException as e:
      print("some error ocurred", e)
  except:
       print sql.rows
