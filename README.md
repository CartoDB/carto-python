What is cartodb-python?
=======================

The cartodb-python project is a Python client for the [CartoDB SQL
API](http://developers.cartodb.com/documentation/sql-api.html) that supports
[authentication using OAuth or API
key](http://developers.cartodb.com/documentation/sql-api.html#authentication).

Installation
============

You can install cartodb-python by cloning this repository or by using
[Pip](http://pypi.python.org/pypi/pip), a Python package installer similar to
easy\_install:

    pip install cartodb

Or if you want to use the development version:

    pip install -e git+git://github.com/Vizzuality/cartodb-python.git#egg=cartodb

Note that cartodb-python depends on the ouath2 module:

    pip install oauth2

And if you're running python prior to 2.6 you need to install simplejson:

    pip install simplejson

Usage example
=============

The following example requires your **CartoDB API consmer key and consumer
secret** or the **API KEY**. Refer to the [CartoDB Authentication
documentation](http://developers.cartodb.com/documentation/cartodb-apis.html#authentication)
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
print cl.sql('select * from mytable')
except CartoDBException as e:
print ("some error ocurred", e)
```

Using API KEY
-------------

You can get you api key in https://YOUR_USER.cartodb.com/your_apps/api_key

```python
from cartodb import CartoDBAPIKey, CartoDBException

user =  'me@mail.com'
API_KEY ='YOUR_CARTODB_API_KEY'
cartodb_domain = 'YOUR_CARTODB_DOMAIN'
cl = CartoDBAPIKey(API_KEY, cartodb_domain)
try:
print cl.sql('select * from mytable')
except CartoDBException as e:
print ("some error ocurred", e)
```

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
