carto-python
============

Python SDK for Carto's APIs:

* [SQL API](https://carto.com/docs/carto-engine/sql-api)
* [Maps API](https://carto.com/docs/carto-engine/maps-api)
* [Import API](https://carto.com/docs/carto-engine/import-api)

carto-python is a full, backwards incompatible rewrite of the deprecated [cartodb-python](https://github.com/CartoDB/cartodb-python/) SDK. Since the
initial rewrite, carto-python has been loaded with a lot of new features, not present in old cartodb-python.

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

Create a `secret.py` from `secret.py.example, fill the variables, cd into the repo folder, create and enable virtualenv, install pytest and run tests:

```
cd carto-python
virtualenv env
source env/bin/activate
pip install -e .
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
from carto import NoAuthClient

auth_client = NoAuthClient(user="myuser")
```

For API key authenticated requests, we need to create an APIKeyAuthClient instance:

```python
from carto import APIKeyAuthClient

auth_client = APIKeyAuthClient(api_key="myapikey", user="myuser")
```

API key is mandatory for all API requests except for sending SQL queries to public datasets.

By default, API requests are sent to _carto.com_. They can be sent to another domain by setting the `domain` parameter. Furthermore,
subdomainless API access, used typically by our on-premises product, is also available. In this case, the `host` parameter needs to be
set, instead of `domain`.

For a detailed description of the rest of parameters both constructors accept, please take a look at the documentation of the source code.

SQL API
=======

Making requests to the SQL API is pretty straightforward:

```python
from carto import SQLCLient

sql = SQLCLient(auth_client)

try:
    sql.send('select * from mytable')
except CartoException as e:
    print("some error ocurred", e)
except:
     print sql.rows
```

Please refer to the source code documentation to find out about the rest of the parameters accepted by the constructor and the `send` method.
In particular, the `send` method allows you to control the format of the results.

Import API
==========

You can import a file into Carto like this:

```python
from carto import FileImport

# Import csv file, set privacy as 'link' and create a default viz
fi = FileImport("test.csv", auth_client, create_vis='true', privacy='link')
fi.run()
```

You can also import a dataset from a remote URL:

```python
from carto import URLImport

fi = URLImport(MY_URL, auth_client)
fi.run()
```

If you specify a refresh interval (>=900s) for a remote URL, your import job becomes a sync table, and Carto will refresh the datasets based on the contents of the URL at that interval:

```python
from carto import URLImport

fi = URLImport("http://test.com/myremotefile", auth_client, interval=3600)
fi.run()
```

At this point, ```fi.success``` indicates whether the initial upload was successful or not.

You can get all the pending imports:

```python
from carto import ImportManager

im = ImportManager(auth_client)
import_list = im.all(ids_only=False)
```

Or just one:

```python
im = ImportManager(auth_client)
single_import = im.get("afaab071-dc95-4bda-a772-ea37f8729157")
```

You can update the attributes of an import job any time (like for checking if an import has finished):

```python
single_import.update()
```

Object attributes correspond to those defined [by the API](http://docs.cartodb.com/cartodb-platform/import-api.html#response-1). In particular, ```state``` is useful to know when the import is finished:

```python
while im.state != "complete" and im.state != "failure":
    time.sleep(10)
    im.update()
```

Please refer to the source code documentation and the examples folder to find out about the rest of the parameters accepted by constructors and methods.

API Documentation
=================

API documentation is written with Sphinx. To build the API docs:

```
pip install sphinx
cd doc
make html
```

Docs are generated inside the `doc/build/hmtl` folder
