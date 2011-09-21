
CartoDB python client 
=====================

A simple CartoDB client to perform requests against the CartoDB API.
Internally it uses OAuth


installing 
----------

    pip install -e git+git://github.com/javisantana/cartodb-python.git#egg=cartdob

quick start
-----------

    user =  'your@mail.com'
    password =  'XXXX'
    CONSUMER_KEY='XXXXXXXXXXXXXXXXXX'
    CONSUMER_SECRET='YYYYYYYYYYYYYYYYYYYYYYYYYY'
    cartodb_domain = 'vitorino'
    cl = CartoDB(CONSUMER_KEY, CONSUMER_SECRET, user, password, cartodb_domain)
    print cl.sql('select * from mytable')


