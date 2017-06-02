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
