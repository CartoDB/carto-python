# What is cartodb-python? #

The cartodb-python project is a Python client for the [CartoDB SQL API](http://developers.cartodb.com/api/sql.html) that supports [authentication using OAuth](http://developers.cartodb.com/api/authentication.html).

# Installation #

You can install cartodb-python by cloning this repository or by using [Pip](http://pypi.python.org/pypi/pip), a Python package installer similar to easy_install.


```bash
pip install -e git+git://github.com/javisantana/cartodb-python.git#egg=cartodb
```

# Usage example #

The following example requires your CartoDB API consmer key and consumer secret. Refer to the [CartoDB Authentication documentation](http://developers.cartodb.com/api/authentication.html) for details.


```python
user =  'me@mail.com'
password =  'secret'
CONSUMER_KEY='YOUR_CARTODB_CONSUMER_KEY'
CONSUMER_SECRET='YOUR_CARTODB_CONSUMER_SECRET'
cartodb_domain = 'YOUR_CARTODB_DOMAIN'
cl = CartoDB(CONSUMER_KEY, CONSUMER_SECRET, user, password, cartodb_domain)
try:
    print cl.sql('select * from mytable')
except CartoDBException as e:
    print ("some error ocurred", e)
```