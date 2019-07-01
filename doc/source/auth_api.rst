Auth API
========

Auth API is the piece of the CARTO platform that enables a consistent, uniform way of accessing data, datasets and APIs.

All requests to CARTO’s APIs (Maps, SQL, etc.) require you to authenticate with an API key. API keys identify your project and provide a powerful and flexible primitive for managing access to CARTO’s resources like APIs and Datasets.

These API keys can be provisioned, revoked and regenerated through the Auth API.

To learn how to create API keys from your CARTO dashboard, full Auth API reference or usage guides, please check the CARTO's `help center`_

.. _help center: https://carto.com/developers/auth-api

Types of API keys
-----------------

In CARTO, you can find 3 types of API keys:

- Default public: Only valid to access for public data. It cannot be removed.
- Master: A super-user API key, it can do anything on your user account. And since a great power carries a great responsibility, you should use it for testing and development only! Keep it secret and use it sparingly.
- Regular: Regular API keys are the most common type of API keys. They provide access to APIs and database tables (aka Datasets) in a granular and flexible manner. They can be removed and have to be created using the Master API key.

API key format
--------------

Every API key consists on four main parts:

- name: You will choose it when creating the API key and it will be used for indexing your API keys.
- type: As mentioned before, there are three type of API keys: `default`, `master` and `regular` providing different levels of access.
- token: It will be used for authenticating your requests.
- grants: Describes which APIs this API key provides access to and to which tables. It consists on an array of two JSON objects. This object's `type` attribute can be `apis`, `database` or `dataservices`:

  - `apis`: Describes which APIs does this API key provide access to through apis attribute
  - `database`: Describes to which tables and schemas and which privleges on them this API Key grants access to through `tables` and `schemas` attributes. You can grant read (`select`) or write (`insert`, `update`, `delete`) permissions on tables. For the case of `schemas` once granted the `create` permission on a schema you'll be able to run SQL queries such as `CREATE TABLE AS...`, `CREATE VIEW AS...` etc. to create entities on it.
  - `dataservices`: Describes to which data services this API key grants access to though services attribute:

See the `full API key format reference`_ in the CARTO help center for more info about allowed table permissions, `dataservices`, etc.

.. _full API key format reference: https://carto.com/developers/auth-api/reference/#section/API-Key-format

API keys in the context of the Python SDK
-----------------------------------------

To be able to access the CARTO APIs you need an API key.

In the context of the Python SDK, each API client needs an `auth_client` which contains the user account credentials.

Let's see an example:

Let's imagine I have a `tornadoes` dataset in my CARTO account and I want to get data about last year tornadoes.

The Python SDK provides an `SQLClient` which allows to run SQL queries. For this specific case we could run a query of this type:

::

  query = "SELECT * FROM tornadoes WHERE year = DATE_PART('year', NOW() - INTERVAL '1 year')"

To run this SQL query we need to do it via the `SQLClient`

::

  from carto.sql import SQLClient
  from carto.exceptions import CartoException

  sql = SQLClient(auth_client)

  try:
    query = "SELECT * FROM tornadoes WHERE year = DATE_PART('year', NOW() - INTERVAL '1 year')"
    data = sql.send(query)
  except CartoException as e:
    print("some error ocurred", e)

And to use the `SQLClient` we need an `auth_client` instance which allows to authenticate with our user credentials via an API key. The full example would look as follows:

::
  
  from carto.auth import APIKeyAuthClient
  from carto.sql import SQLClient
  from carto.exceptions import CartoException

  API_KEY = "myapikey"
  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key=API_KEY, base_url=USR_BASE_URL)

  sql = SQLClient(auth_client)

  try:
    query = "SELECT * FROM tornadoes WHERE year = DATE_PART('year', NOW() - INTERVAL '1 year')"
    data = sql.send(query)
  except CartoException as e:
    print("some error ocurred", e)

And this is when the Auth API can be useful.

Creating a regular API key
--------------------------

Let's go back to our `tornadoes` example. We might want to create a Regular API key that only has access to the `tornadoes` dataset. This is how we'd do it:

::

  from carto.auth import APIKeyAuthClient
  from carto.api_keys import APIKeyManager

  API_KEY = "mymasterapikey"
  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key=API_KEY, base_url=USR_BASE_URL)

  api_key_mamager = APIKeyManager(auth_client)
  tables = [{
              "schema": api_key_manager.client.username,
              "name": "tornadoes",
              "permissions": [
                "select"
              ]
            }]
  api_key = api_key_manager.create(name="tornadoes api key", tables=tables)
  print(api_key.token)

  # Now we can use this API key `token` to get data from the `tornadoes` dataset

Regenerate token of an existing regular API key
-----------------------------------------------

This will regenerate the internal token of the API key instance in case it has been compromised. Regular and Master API keys tokens can be regenerated.

::

  from carto.auth import APIKeyAuthClient
  from carto.api_keys import APIKeyManager

  API_KEY = "mymasterapikey"
  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key=API_KEY, base_url=USR_BASE_URL)

  api_key_mamager = APIKeyManager(auth_client)
  tornados_api_key = api_key_mamager.get("tornadoes api key")

  tornados_api_key.regenerate_token()

Revoke access to your account to an API key
-------------------------------------------

API keys cannot be edited, that means wherever you grant some privileges to an API key the only way to revoke those privileges is by deleting the API key.

::

  from carto.auth import APIKeyAuthClient
  from carto.api_keys import APIKeyManager

  API_KEY = "mymasterapikey"
  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key=API_KEY, base_url=USR_BASE_URL)

  api_key_mamager = APIKeyManager(auth_client)
  tornados_api_key = api_key_mamager.get("tornadoes api key")

  tornados_api_key.delete()

Get all my regular API keys
---------------------------

::

  from carto.auth import APIKeyAuthClient
  from carto.api_keys import APIKeyManager

  API_KEY = "mymasterapikey"
  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key=API_KEY, base_url=USR_BASE_URL)

  api_key_mamager = APIKeyManager(auth_client)
  api_keys = api_key_manager.filter(type='regular')

  # now you can do any operation on those api_keys

Grant access to Data services
-----------------------------

Regular API keys can also be granted privileges to the `Data Services API`_

.. _Data Services API: https://carto.com/developers/data-services-api/

::

  from carto.auth import APIKeyAuthClient
  from carto.api_keys import APIKeyManager

  API_KEY = "mymasterapikey"
  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key=API_KEY, base_url=USR_BASE_URL)

  api_key_mamager = APIKeyManager(auth_client)
  dataservices = ["geocoding", "routing", "isolines", "observatory"]
  api_key = api_key_manager.create(name="tornadoes api key", services=dataservices)

Once we have created the regular API key we can run queries against the Data Services API
  
::

  from carto.sql import SQLClient
  from carto.exceptions import CartoException

  # Create a new auth_client with the token of the regular API key previously created
  auth_client = APIKeyAuthClient(api_key=api_key.token, base_url=USR_BASE_URL)
  sql = SQLClient(auth_client)

  try:
    query = "SELECT cdb_geocode_admin0_polygon('USA')"
    data = sql.send(query)
  except CartoException as e:
    print("some error ocurred", e)
