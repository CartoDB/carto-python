# README

The examples folder contains several examples to show different approaches to use the CARTO Python SDK.
Take into account that the Python SDK is a Work In Progress project and some examples might change.

The examples that this folder contains are:


- File [listTables.py](https://github.com/CartoDB/carto-python/blob/examples/examples/listTables.py): it lists all tables from a specific account indicating the name, size and if the table has been cartodbfied or not.

- File [tableInfo.py](https://github.com/CartoDB/carto-python/blob/examples/examples/tableInfo.py) Returns information about the table such as columns and its types, triggers, functions and indexes applied on the table.  


- File [importStandardTable.py](https://github.com/CartoDB/carto-python/blob/examples/examples/importStandardTable.py). It imports a file showing the status of the import process. You need to set the path/URL to import to the account as an input argument.

- File [importSyncTable.py](https://github.com/CartoDB/carto-python/blob/examples/examples/importSyncTable.py). You would need to set the URL and the sync interval as input arguments. It displays the import status while the file is being imported.

- File [userInfo.py](https://github.com/CartoDB/carto-python/blob/examples/examples/userInfo.py) displays information of the user (username, db_size_in_bytes, avatar_url, public_visualization_count, quota_in_bytes, base_url, number of tables, number of visualizations and the email address if the account). It also displays also the different states of the Data Services (geocoding, routing, isolines and data observatory quotas and used quota)


- File [mapInfo.py](https://github.com/CartoDB/carto-python/blob/examples/examples/mapInfo.py) displays all properties of single map.

- File [runningQueries.py](https://github.com/CartoDB/carto-python/blob/examples/examples/runningQueries.py) displays running queries in CARTO account. The lack of database privilegies make unable to see some queries.

- File [killQuery.py](https://github.com/CartoDB/carto-python/blob/examples/examples/killQuery.py) kills a specific running query using the PID value.

- File [checkQuery.py](https://github.com/CartoDB/carto-python/blob/examples/examples/checkQuery.py) checks the query planner of the input query with the PostgreSQL Explain Analyze operation. Depending on the query give tips to optimize the query.

- File [importMergeFiles.py](https://github.com/CartoDB/carto-python/blob/examples/examples/importMergeFiles.py). It imports several files from a folder and merge them into a single dataset within the CARTO account.

- File [createBatchJob.py](https://github.com/CartoDB/carto-python/blob/examples/examples/createBatchJob.py) creates a new SQL Batch API job.

- File [cancelBatchJob.py](https://github.com/CartoDB/carto-python/blob/examples/examples/cancelBatchJob.py) cancels a running SQL Batch API job process.

- File [readBatchJob.py](https://github.com/CartoDB/carto-python/blob/examples/examples/readBatchJob.py). Returns the status of a running SQL Batch API job.

- File [updateBatchJob.py](https://github.com/CartoDB/carto-python/blob/examples/examples/updateBatchJob.py). Updates the query of a running SQL Batch API job.
