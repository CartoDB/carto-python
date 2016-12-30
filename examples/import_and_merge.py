from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.file_import import FileImportJob
import warnings
warnings.filterwarnings('ignore')
from os import listdir
from os.path import isfile, join
from carto.sql import SQLClient
import time

organization = 'cartoworkshops'
CARTO_API_KEY = os.environ['CARTO_API_KEY']
CARTO_BASE_URL = 'https://carto-workshops.carto.com/api/'

# authenticate to CARTO
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

# define path of the files
path = 'examples/files'

# import files from the path to CARTO
table_name = []
for i in listdir(path):
    if isfile(join(path, i)) == True:
        print i
        print join(path, i)
        # imports the file to CARTO
        fi = FileImportJob(join(path, i), auth_client)
        fi.run()

        time.sleep(2)

        fi.refresh()

        if fi.success == True:
            while (fi.state != 'complete'):
                fi.refresh()
                time.sleep(2)
                # print status
                print fi.state
                if fi.state == 'complete':
                    # print name of the imported table
                    table_name.append(fi.table_name)
                if fi.state == 'failure':
                    print "Import has failed"
                    print fi.get_error_text
                    break
        else:
            print "Import has failed"

print table_name

# define base table to insert all rows from other files
base_table = table_name[0]

# select all rows from table except cartodb_id to avoid possible errors

columns_table = "select string_agg(column_name,',')" + \
    " FROM information_schema.columns" + \
    " where table_schema = 'carto-workshops' and table_name = '" + \
    str(table_name[0]) + "' AND column_name <> 'cartodb_id'"

print columns_table
result_query = sql.send(columns_table)

for k, v in result_query.items():
    if k == 'rows':
        for itr in v:
            dict_col = itr

print dict_col['string_agg']

# apply operation INSERT INTO SELECT with columns from previous query
index = 1
for i in table_name:
    # print i
    # print index
    if i == base_table:
        print 'First if i: ' + str(i)
        continue
    elif i != base_table and index <= len(table_name):
        print i
        print 'First if index: ' + str(index)
        query = "insert into " + base_table + \
            "(" + dict_col['string_agg'] + ") select " + \
            dict_col['string_agg'] + " from " + table_name[index] + ";"
        sql.send(query)
        time.sleep(2)
        print query
    else:
        print 'miau ' + str(index)
        break
    index = index + 1

# cahnge name of base table
change_name_query = "ALTER TABLE " + base_table + \
    " RENAME TO " + base_table + "_merged"
sql.send(change_name_query)

# remove not merged datasets

for i in table_name:
    print i
    try:
        remove_dataset = "DROP TABLE " + i
        print remove_dataset
        sql.send(remove_dataset)
        time.sleep(2)
    except:
        continue
