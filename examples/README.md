# README

The examples folder contains several examples to show different approaches to use the CARTO Python SDK.
Take into account that the Python SDK is a Work In Progress project and some examples might change.

The examples that this folder contains are:


- File [describe_table.py](https://github.com/CartoDB/carto-python/blob/examples/examples/describe_table.py): it lists all tables from a specific account indicating the name, size and if the table has been cartodbfied or not.

- File [describe_single_table.py](https://github.com/CartoDB/carto-python/blob/examples/examples/describe_single_table.py) take the username and the name of the table as input arguments, display the  name of the table, number of rows, size (in MB), privacy of the table, geometry of the table, column names and their types, indexes, triggers, functions of the account and a message indicating if the table is  Cartodbfyied and the total number of tables for a specific table.  


- File [import_standard_table.py](https://github.com/CartoDB/carto-python/blob/examples/examples/import_standard_table.py). It imports a file showing the status of the import process. It imports a shapefile from this url `https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj?method=export&format=Shapefile` to carto-workshops account.

- File [import_sync_table.py](https://github.com/CartoDB/carto-python/blob/examples/examples/import_sync_table.py). It imports a shapefile from this url `https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj?method=export&format=Shapefile` to carto-workshops account setting the sync interval to 900 seconds. Display the import status while the file is being imported. It has the commands to force sync and delete sync commented.

- File [sqlBatchAPI.py](https://github.com/CartoDB/carto-python/blob/examples/examples/sqlBatchAPI.py). It gets the existing jobs in the file, but CARTO returns an error. AT this stage, the BatchSQLManager, seems to be incomplete. It can create new jobs.


- File [userInfo.py](https://github.com/CartoDB/carto-python/blob/examples/examples/userInfo.py) displays information of the user (username, db_size_in_bytes, avatar_url, public_visualization_count, quota_in_bytes, base_url, number of tables, number of visualizations and the email address if the accout). Using the query `SELECT * FROM cdb_dataservices_client.cdb_service_quota_info()`, the file displays also the different states of the Data Services (geocoding, routing, isolines and data observatory quotas and used quota)


- File [mapInfo.py](https://github.com/CartoDB/carto-python/blob/examples/examples/mapInfo.py) displays all properties of single map.

- File [running_queries.py](https://github.com/CartoDB/carto-python/blob/examples/examples/running_queries.py) displays running queries in CARTO account. The lack of database privilegies make unable to see some queries.

- File [kill_query.py](https://github.com/CartoDB/carto-python/blob/examples/examples/kill_query.py) kills a specific running query using the PID value.

- File [check_query.py](https://github.com/CartoDB/carto-python/blob/examples/examples/check_query.py) checks the query planner of the input query with the PostgreSQL Explain Analyze operation. Depending on the query give tips to optimize the query.

- File [import_and_merge.py](https://github.com/CartoDB/carto-python/blob/examples/examples/import_and_merge.py). It imports several files and merge them into a single dataset. The script imports several files from the files folder named `files` using the CARTO Import API and saving the names of the imported files into an array. Then, using the CARTO SQL API and the INSERT INTO SELECT operation, it merges the different files into a single one. Finally using the SQL DROP TABLE operation, it deletes the files that have been imported except the merged one.