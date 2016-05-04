What is cartodb-python?
=======================

The cartodb-python project is a Python client for:

* [CartoDB's SQL API](http://developers.cartodb.com/documentation/sql-api.html) with [authentication using OAuth or API key](http://developers.cartodb.com/documentation/sql-api.html#authentication).
* [CartoDB's Import API](http://docs.cartodb.com/cartodb-platform/import-api.html) with [authentication using API key](http://docs.cartodb.com/cartodb-platform/import-api.html#auth).

Installation
============

You can install cartodb-python by cloning this repository or by using
[Pip](http://pypi.python.org/pypi/pip), a Python package installer similar to
easy\_install:

    pip install cartodb

Or if you want to use the development version (currently the only one that supports the Import API):

    pip install -e git+git://github.com/CartoDB/cartodb-python.git#egg=cartodb

You might need to install cartodb's dependencies as well:

    pip install -r requirements.txt

Usage example: SQL API
======================

The following example requires your **CartoDB API consumer key and consumer
secret** or the **API key**. Refer to the [CartoDB documentation](http://docs.cartodb.com/cartodb-platform/sql-api.html#authentication)
for details.

Using oAuth
-----------

```python
from cartodb import CartoDBOAuth, CartoDBException

user =  'me@mail.com'
password =  'secret'
CONSUMER_KEY='YOUR_CARTODB_CONSUMER_KEY'
CONSUMER_SECRET='YOUR_CARTODB_CONSUMER_SECRET'
cartodb_domain = 'YOUR_CARTODB_DOMAIN'
cl = CartoDBOAuth(CONSUMER_KEY, CONSUMER_SECRET, user, password, cartodb_domain)
try:
    print(cl.sql('select * from mytable'))
except CartoDBException as e:
    print("some error ocurred", e)
```

Using API KEY
-------------

You can get you API key in https://YOUR_USER.cartodb.com/your_apps

```python
from cartodb import CartoDBAPIKey, CartoDBException

API_KEY ='YOUR_CARTODB_API_KEY'
cartodb_domain = 'YOUR_CARTODB_DOMAIN'
cl = CartoDBAPIKey(API_KEY, cartodb_domain)
try:
   print(cl.sql('select * from mytable'))
except CartoDBException as e:
   print("some error ocurred", e)
```

Usage example: Import API
=========================

The following example requires your **CartoDB API key**. Refer to the [CartoDB documentation](http://docs.cartodb.com/cartodb-platform/sql-api.html#authentication) for details.

You can import a file into CartoDB like this:

```python
from cartodb import CartoDBAPIKey, CartoDBException, FileImport

API_KEY ='YOUR_CARTODB_API_KEY'
cartodb_domain = 'YOUR_CARTODB_DOMAIN'
cl = CartoDBAPIKey(API_KEY, cartodb_domain)

fi = FileImport("test.csv", cl)
fi.run()
```

You can also import a dataset from a remote URL:

```python
from cartodb import URLImport

fi = URLImport(MY_URL, cl)
fi.run()
```

If you specify a refresh interval (>=3600s) for a remote URL, your import job becomes a sync table, and CartoDB will refresh the datasets based on the contents of the URL at that interval:

```python
from cartodb import URLImport

fi = URLImport(MY_URL, cl, interval=3600)
fi.run()
```

At this point, ```fi.success``` indicates whether the initial upload was successful or not.

You can get all the pending imports:

```python
from cartodb import ImportManager

im = ImportManager(cl)
import_list = im.all(ids_only=False)
```

Or just one:

```python
im = ImportManager(cl)
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

# API

Please refer to the source code for API reference documentation.

Note for people using version 0.4
==================================

With the new API key auth now you have two options to authenticate so the class
CartoDB has been replaced with CartoDBOAuth and CartoDBAPIKey.

In order to migrate your code to this version you have to replace

```python
from cartodb import CartoDB
```

by

```python
from cartodb import CartoDBOAuth as CartoDB
```

Running tests
=============

Clone the repo, create a secret.py from secret.py.example, fill the variables
and execute:

    python setup.py test
