Import API
==========

You can import local or remote datasets into CARTO via the `Import API`_ like this:

::

  from carto.datasets import DatasetManager

  # write here the path to a local file or remote URL
  LOCAL_FILE_OR_URL = ""

  dataset_manager = DatasetManager(auth_client)
  dataset = dataset_manager.create(LOCAL_FILE_OR_URL)


The Import API is asynchronous, but the `DatasetManager` waits a maximum of 150 seconds for the dataset to be uploaded, so once it finishes the dataset has been created in CARTO.

Import a sync dataset
---------------------

You can do it in the same way as a regular dataset, just include a sync_time parameter with a value >= 900 seconds

::

  from carto.datasets import DatasetManager

  # how often to sync the dataset (in seconds)
  SYNC_TIME = 900
  # write here the URL for the dataset to sync
  URL_TO_DATASET = ""

  dataset_manager = DatasetManager(auth_client)
  dataset = dataset_manager.create(URL_TO_DATASET, SYNC_TIME)


Alternatively, if you need to do further work with the sync dataset, you can use the `SyncTableJobManager`

::

  from carto.sync_tables import SyncTableJobManager
  import time

  # how often to sync the dataset (in seconds)
  SYNC_TIME = 900
  # write here the URL for the dataset to sync
  URL_TO_DATASET = ""

  syncTableManager = SyncTableJobManager(auth_client)
  syncTable = syncTableManager.create(URL_TO_DATASET, SYNC_TIME)

  # return the id of the sync
  sync_id = syncTable.get_id()

  while(syncTable.state != 'success'):
      time.sleep(5)
      syncTable.refresh()
      if (syncTable.state == 'failure'):
          print('The error code is: ' + str(syncTable.error_code))
          print('The error message is: ' + str(syncTable.error_message))
          break

  # force sync
  syncTable.refresh()
  syncTable.force_sync()


Get a list of all the current import jobs
-----------------------------------------

::

  from carto.file_import import FileImportJobManager

  file_import_manager = FileImportJobManager(auth_client)
  file_imports = file_import_manager.all()


Get all the datasets
--------------------

::

  from carto.datasets import DatasetManager

  dataset_manager = DatasetManager(auth_client)
  datasets = dataset_manager.all()


Get a specific dataset
----------------------

::

  from carto.datasets import DatasetManager

  # write here the ID of the dataset to retrieve
  DATASET_ID = ""

  dataset_manager = DatasetManager(auth_client)
  dataset = dataset_manager.get(DATASET_ID)


Delete a dataset
----------------

::

  from carto.datasets import DatasetManager

  # write here the ID of the dataset to retrieve
  DATASET_ID = ""

  dataset_manager = DatasetManager(auth_client)
  dataset = dataset_manager.get(DATASET_ID)
  dataset.delete()


Please refer to the :ref:`apidoc` and the **examples** folder to find out about the rest of the parameters accepted by constructors and methods.


External database connectors
----------------------------

The CARTO Python client implements the `database connectors`_ feature of the Import API

.. _database connectors: https://carto.com/docs/carto-engine/import-api/database-connectors

The database connectors allow importing data from an external database into a CARTO table by using the `connector` parameter.

There are several types of database connectors that you can connect to your CARTO account.

Please refer to the `database connectors`_ documentation for supported external databases.

As an example, this code snippets imports data from a Hive table into CARTO:

::

  from carto.datasets import DatasetManager

  dataset_manager = DatasetManager(auth_client)

  connection = {
    "connector": {
      "provider": "hive",
      "connection": {
        "server": "YOUR_SERVER_IP",
        "database": "default",
        "username": "YOUR_USER_NAME",
        "password": "YOUR_PASSWORD"
      },
      "schema": "default",
      "table": "YOUR_HIVE_TABLE"
    }
  }

  table = dataset_manager.create(None, None, connection=connection)

You still can configure a sync external database connector, by providing the `interval` parameter:

::

  table = dataset_manager.create(None, 900, connection=connection)

DatasetManager vs FileImportJobManager and SyncTableJobManager
--------------------------------------------------------------

The `DatasetManager` is conceptually different from both `FileImportJobManager` and `SyncTableJobManager`. These later ones are `JobManagers`, that means that they create and return a job using the CARTO Import API. It's responsibility of the developer to check the `state` of the job to know whether the dataset import job is completed, or has failed, errored, etc.

As an example, this code snippet uses the `FileImportJobManager` to create an import job:

::

  # write here the URL for the dataset or the path to a local file (local to the server...)
  LOCAL_FILE_OR_URL = "https://academy.cartodb.com/d/tornadoes.zip"

  file_import_manager = FileImportJobManager(auth_client)
  file_import = file_import_manager.create(LOCAL_FILE_OR_URL)

  # return the id of the import
  file_id = file_import.get_id()

  file_import.run()
  while(file_import.state != "complete" and file_import.state != "created"
              and file_import.state != "success"):
      time.sleep(5)
      file_import.refresh()
      if (file_import.state == 'failure'):
          print('The error code is: ' + str(file_import))
          break

Note that with the `FileImportJobManager` we are creating an import job and we check the `state` of the job.

On the other hand the `DatasetManager` is an utility class that works at the level of `Dataset`. It creates and returns a `Dataset` instance. Internally, it uses a `FileImportJobManager` or a `SyncTableJobManager` depending on the parameters received and is able to automatically `check` the `state` of the job it creates to properly return a `Dataset` instance once the job finishes successfully or a `CartoException` in any other case.

As an example, this code snippet uses the `DatasetManager` to create a dataset:

::

  # write here the path to a local file (local to the server...) or remote URL
  LOCAL_FILE_OR_URL = "https://academy.cartodb.com/d/tornadoes.zip"

  # to use the DatasetManager you need an enterprise account
  auth_client = APIKeyAuthClient(BASE_URL, API_KEY)

  dataset_manager = DatasetManager(auth_client)
  dataset = dataset_manager.create(LOCAL_FILE_OR_URL)

  # the create method will wait up to 10 minutes until the dataset is uploaded.

In this case, you don't have to check the `state` of the import job, since it's done automatically by the `DatasetManager`. On the other hand, you get a `Dataset` instance as a result, instead of a `FileImportJob` instance.
