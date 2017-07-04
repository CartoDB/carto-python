Authentication
==============

Before making API calls, we need to define how those calls are going to be authenticated. Currently, we support two different
authentication methods: unauthenticated and API key based.

Therefore, we first need to create an *authentication client* that will
be used when instantiating the Python classes that deal with API requests.

For unauthenticated requests, we need to create a `NoAuthClient` object:

::

  from carto.auth import NoAuthClient

  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = NoAuthClient(base_url=USR_BASE_URL)


For API key authenticated requests, we need to create an `APIKeyAuthClient` instance:

::

  from carto.auth import APIKeyAuthClient

  USERNAME="type here your username"
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)
  auth_client = APIKeyAuthClient(api_key="myapikey", base_url=USR_BASE_URL)


API key is mandatory for all API requests except for sending SQL queries to public datasets.

The `base_url` parameter must include the `user` and or the `organization` with a format similar to these ones:

::

  BASE_URL = "https://{organization}.carto.com/user/{user}/". \
      format(organization=ORGANIZATION,
             user=USERNAME)
  USR_BASE_URL = "https://{user}.carto.com/".format(user=USERNAME)


For a detailed description of the rest of parameters both constructors accept, please take a look at the :ref:`authmodule` documentation.

Finally, you can use a `NonVerifiedAPIKeyAuthClient` instance if you are running CARTO on your premises and don't have a valid SSL certificate:

::

  from carto.auth import NonVerifiedAPIKeyAuthClient

  USERNAME="type here your username"
  YOUR_ON_PREM_DOMAIN="myonprem.com"
  USR_BASE_URL = "https://{domain}/user/{user}".format(domain=YOUR_ON_PREM_DOMAIN, user=USERNAME)
  auth_client = NonVerifiedAPIKeyAuthClient(api_key="myapikey", base_url=USR_BASE_URL)