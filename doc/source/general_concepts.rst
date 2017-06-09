General Concepts
================

The CARTO Python module implements these public CARTO APIs:

- `SQL API`_.
- `Import API`_.
- `Maps API`_.

.. _SQL API: https://carto.com/docs/carto-engine/sql-api
.. _Import API: https://carto.com/docs/carto-engine/import-api
.. _Maps API: https://carto.com/docs/carto-engine/maps-api

As well as other non-public APIs. Non-public APIs may change in the future and will throw a warnings.warn message when used.

Please be aware if you plan to run them on a production environment.

Refer to the :ref:`apidoc` for a list of non-public APIs implemented.

pyrestcli
---------

The CARTO Python client relies on a Python REST client called `pyrestcli`_

.. _pyrestcli: https://github.com/danicarrion/pyrestcli

`pyrestcli` allows you to define data models, with a syntax that is derived from Django's model framework, that you can use directly against REST APIs


Resources and Managers
----------------------

The CARTO Python client is built upon two main concepts: `Resource` and `Manager`

A `Resource` represent your model, according to the schema of the data available on the server for a given API.
A `Manager` is a utility class to create `Resource` instances.

Each API implemented by the CARTO Python client provides a `Manager` and a `Resource`.

With a `Manager` instance you can:

- Get a resource given its id

::

  resource = manager.get(resource_id)

- Create a new resource

::

  resource = manager.create({id: "resource_id", prop_a: "test"})

- Retrieve all the resources

::

  resources = manager.all()

- Get a filtered list of resources (search_args: To be translated into ?arg1=value1&arg2=value2...)

::

  resources = manager.filter(**search_args)

With a `Resource` instance you can:

- Save the resource instance (equivalent to update the resource)

::

  resource.save()

- Delete the resource instance

::

  resource.delete()

- Refresh the resource instance

::

  resource.refresh()

The CARTO Python client's Managers and Resources extend both classes, so please refer to the :ref:`apidoc` for additional methods available.

Types of resources
------------------

The CARTO Python client provides three different types of Resources with different features:

- `AsyncResource`: Used for API requests that are asynchronous, as the Batch SQL API.

AsyncResources work in this way. First you create the asynchronous job in the server:

::

  async_resource.run(**import_args)

Second, you start a loop refreshing the `async_resource` and checking the state of the job created in the server (depending on the API requested, the 'state' value may change):

::

  while async_resource.state in ("enqueued", "pending", "uploading",
                                 "unpacking", "importing", "guessing"):
      async_resource.refresh()


Finally, you check the state to know the status of the job in the server:

::

  status = async_resource.state
  # do what it takes depending on the status

- `WarnAsyncResource`: This type of `Resource` is an `AsyncResource` of a non-public API, so it will throw `warnings` whenever you try to use it.
- `WarnResource`: This type of `Resource` is a regular `Resource` of a non-public API, so it will throw `warnings` whenever you try to use it.

The use of `WarnAsyncResource` and `WarnResource` is totally discouraged for production environments, since non-public APIs may change without prior advice.

Fields
------

A `Field` class represent an attribute of a `Resource` class.

The `Field` class is meant to be subclassed every time a new specific data type wants to be defined.

Fields are a very handy way to parse a JSON coming from the REST API and store real Python objects on the `Resource`

The list of available fields is:

- `Field`: This default `Field` simply stores the value in the instance as it comes, suitable for basic types such as integers, chars, etc.
- `BooleanField`: Convenient class to make explicit that an attribute will store booleans
- `IntegerField`: Convenient class to make explicit that an attribute will store integers
- `FloatField`: Convenient class to make explicit that an attribute will store floats
- `CharField`: Convenient class to make explicit that an attribute will store chars
- `DateTimeField`: `Field` to store `datetimes` in resources
- `DictField`: Convenient class to make explicit that an attribute will store a dictionary
- `ResourceField`: `Field` to store resources inside other resources

The CARTO Python client provides additional instances of `ResourceField`:

- `VisualizationField`
- `TableField`
- `UserField`
- `EntityField`
- `PermissionField`

Exceptions
----------

All the Exceptions of the CARTO Python client are wrapped into the `CartoException` class.

Please refer to the `CARTO API docs`_ for more information about concrete error codes and exceptions.

.. _CARTO API docs: https://carto.com/docs/carto-engine/import-api/import-errors

.. _installation:
