# README

The examples folder contains several examples to show different approaches to use the CARTO Python SDK.
Take into account that the Python SDK is a Work In Progress project and some examples might change.

The examples that this folder contains are:


- File [listTables.py](https://github.com/CartoDB/carto-python/blob/examples/examples/list_tables.py): it lists all tables from a specific account indicating the name, size and if the table has been cartodbfied or not.

- File [table_info.py](https://github.com/CartoDB/carto-python/blob/examples/examples/table_info.py) Returns information about the table such as columns and its types, triggers, functions and indexes applied on the table.  


- File [import_standard_table.py](https://github.com/CartoDB/carto-python/blob/examples/examples/import_standard_table.py). It imports a file showing the status of the import process. You need to set the path/URL to import to the account as an input argument.

- File [import_sync_table.py](https://github.com/CartoDB/carto-python/blob/examples/examples/import_sync_table.py). You would need to set the URL and the sync interval as input arguments. It displays the import status while the file is being imported.

- File [user_info.py](https://github.com/CartoDB/carto-python/blob/examples/examples/user_info.py.py) displays information of the user (username, db_size_in_bytes, avatar_url, public_visualization_count, quota_in_bytes, base_url, number of tables, number of visualizations and the email address if the account). It also displays also the different states of the Data Services (geocoding, routing, isolines and data observatory quotas and used quota)


- File [map_info.py](https://github.com/CartoDB/carto-python/blob/examples/examples/map_info.py) displays all properties of single map.

- File [running_queries.py](https://github.com/CartoDB/carto-python/blob/examples/examples/running_queries.py) displays running queries in CARTO account. The lack of database privilegies make unable to see some queries.

- File [kill_query.py](https://github.com/CartoDB/carto-python/blob/examples/examples/kill_query.py) kills a specific running query using the PID value.

- File [check_query.py](https://github.com/CartoDB/carto-python/blob/examples/examples/check_query.py) checks the query planner of the input query with the PostgreSQL Explain Analyze operation. Depending on the query give tips to optimize the query.

- File [import_and_merge.py](https://github.com/CartoDB/carto-python/blob/examples/examples/import_and_merge.py). It imports several files from a folder and merge them into a single dataset within the CARTO account.

- File [sql_batch_api_jobs.py](https://github.com/CartoDB/carto-python/blob/examples/examples/sql_batch_api_jobs.py) allows different SQL Batch API jobs.
