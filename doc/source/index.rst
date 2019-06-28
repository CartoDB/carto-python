.. carto-python documentation master file, created by
   sphinx-quickstart on Wed Apr 26 17:15:38 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to carto-python's developer guide!
==========================================

This section contains documentation on how to use the different `carto-python` APIs.

`carto-python` is a full, backwards incompatible rewrite of the deprecated `cartodb-python` SDK. Since the initial rewrite, `carto-python` has been loaded with a lot of new features, not present in old `cartodb-python`.

`carto-python` is a Python library to consume the CARTO APIs. You can integrate `carto-python` into your Python projects to:

- Import data from files, URLs or external databases to your user account or organization
- Execute SQL queries and get the results
- Run batch SQL jobs
- Create and instantiate named and anonymous maps
- Create, update, get, delete and list datasets, users, maps...
- etc.

You may find specially useful the :ref:`examples` section for actual use cases of the CARTO Python library.

Please, refer to the :ref:`apidoc` or the source code for further details about modules, methods and parameters.

.. note:: Code snippets provided in this developer guide are not intended to be executed since they may not contain API keys or USERNAME values needed to actually execute them. Take them as a guide on how to work with the modules and classes


.. toctree::
   :maxdepth: 1

   quickstart
   general_concepts
   installation
   authentication
   auth_api
   sql_api
   import_api
   maps_api
   kuviz
   non_public_apis
   examples
   modules
