# What is cartodb-python? #

The cartodb-python project is a Python client for the [CartoDB SQL API](http://developers.cartodb.com/api/sql.html) that supports [authentication using OAuth](http://developers.cartodb.com/api/authentication.html).

# Installation #

You can install cartodb-python by cloning this repository or by using [Pip](http://pypi.python.org/pypi/pip), a Python package installer similar to easy_install.

```bash
pip install cartodb
```

or if you want to use the development version

```bash
pip install -e git+git://github.com/javisantana/cartodb-python.git#egg=cartodb
```

Note that cartodb-python depends on the ouath2 module

```bash
pip install oauth2
```

and if you're running python < 2.6 you need to install simplejson

```bash
pip install simplejson
```


# Usage example #

The following example requires your **CartoDB API consmer key and consumer secret** or the **API KEY**. Refer to the [CartoDB Authentication documentation](http://developers.cartodb.com/documentation/cartodb-apis.html#authentication) for details.

## using oAuth

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

## using API KEY

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

# Note for people using version 0.4 

With the new API key auth now you have two options to authenticate so the class CartoDB has been replaced with CartoDBOAuth and CartoDBAPIKey.

In order to migrate your code to this version you have to replace

```python
from cartodb import CartoDB
```

by

```python
from cartodb import CartoDBOAuth as CartoDB
```

# running tests

clone the repo, create a secret.py from secret.py.example, fill the variables and execute:

```base
python setup.py test
```




