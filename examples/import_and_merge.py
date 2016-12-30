from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.file_import import FileImportJob
import warnings
warnings.filterwarnings('ignore')
from os import listdir
from os.path import isfile, join
from carto.sql import SQLClient
from carto.datasets import DatasetManager
import time
import logging

organization = 'cartoworkshops'
CARTO_API_KEY = '172a2e8659184e6c74db78a258a8de2340bd5f0b'
CARTO_BASE_URL = 'https://carto-workshops.carto.com/api/'

# authenticate to CARTO
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

# Dataset manager

dataset_manager = DatasetManager(auth_client)

# define path of the files
path = '/Users/oboix/carto-python/examples/files'

# import files from the path to CARTO
table_name = []
for i in listdir(path):
    if isfile(join(path, i)) == True:
       
        # imports the file to CARTO
        fi = FileImportJob(join(path, i), auth_client)
        fi.run()

        time.sleep(2)

        fi.refresh()

        if fi.success == True:
            while (fi.state != 'complete'):
                fi.refresh()
                time.sleep(2)
                
                if fi.state == 'complete':
                    # print name of the imported table
                    table_name.append(fi.table_name)
                if fi.state == 'failure':
                    logging.error("Import has failed")
                    logging.error(fi.get_error_text)
                    break
        else:
            logging.error("Import has failed")
            



# define base table to insert all rows from other files
base_table = table_name[0]

# select all rows from table except cartodb_id to avoid possible errors

columns_table = "select string_agg(column_name,',')" + \
    " FROM information_schema.columns" + \
    " where table_schema = 'carto-workshops' and table_name = '" + \
    str(table_name[0]) + "' AND column_name <> 'cartodb_id'"


result_query = sql.send(columns_table)

for k, v in result_query.items():
    if k == 'rows':
        for itr in v:
            dict_col = itr

logging.debug(dict_col['string_agg'])

# apply operation INSERT INTO SELECT with columns from previous query
index = 1
for i in table_name:

    if i == base_table:
        
        continue
    elif i != base_table and index <= len(table_name):
        
        query = "insert into " + base_table + \
            "(" + dict_col['string_agg'] + ") select " + \
            dict_col['string_agg'] + " from " + table_name[index] + ";"
        sql.send(query)
        time.sleep(2)
        
    else:
        break
    index = index + 1

# change name of base table

myTable = dataset_manager.get(base_table)
myTable.name = base_table + "_merged"
myTable.save()
time.sleep(2)


# remove not merged datasets

for i in table_name:
    try:
        myTable = dataset_manager.get(i)
        myTable.delete()
        time.sleep(2)
    except:
        continue
