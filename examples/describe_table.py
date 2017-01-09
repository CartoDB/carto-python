from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
printer = pprint.PrettyPrinter(indent=4)
from carto.sql import SQLClient


organization = 'cartoworkshops'
CARTO_BASE_URL = 'https://carto-workshops.carto.com/api/'
CARTO_API_KEY = os.environ['CARTO_API_KEY']

# Authenticate to CARTO account
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

# check all table name of account

all_tables = []

tables = sql.send("select pg_class.relname from pg_class, pg_roles, pg_namespace where pg_roles.oid = pg_class.relowner and pg_roles.rolname = current_user and pg_namespace.oid = pg_class.relnamespace and pg_class.relkind = 'r'")

for k,v in tables.items():
    if k == 'rows':
        for itr in v:
            all_tables.append(itr['relname'])


# define array to store all the table sizes

arr_size = []


# create array with values of the table sizes
for i in all_tables:
    try:
        size = sql.send("select pg_total_relation_size('"+ i + "')")
        for a,b in size.items():
            if a == 'rows':
                for itr in b:
                    size_dataset = itr['pg_total_relation_size']
        arr_size.append(size_dataset)
    except:
        continue

# define variables that have the max and min values of the previous array
max_val = max(arr_size)/1048576.00
min_val = min(arr_size)/1048576.00

# define count variable
sum = 0

# start iterating over array 
for i in all_tables:
    # check column names
    checkCol = []

    sum = sum + 1
   
    # check all columns name from table
    columns_table = "select column_name, data_type FROM information_schema.columns \
    WHERE table_schema = 'carto-workshops'" + \
    " AND table_name ='" + i + "';"

    # apply and get results from SQL API request
    columnAndTypes = sql.send(columns_table)
    for key, value in columnAndTypes.items():
        if key == 'rows':
            for itr in value:
                if 'cartodb_id' == itr['column_name']:
                    checkCol.append(itr['column_name'])
                elif 'the_geom' == itr['column_name']:
                    checkCol.append(itr['column_name'])
                elif 'the_geom_webmercator' == itr['column_name']:
                    checkCol.append(itr['column_name'])
    # check indexes
    checkInd = []
    # apply and get results from SQL API request
    indexes = sql.send("select indexname, indexdef from pg_indexes \
      where tablename = '" + i + "' \
      AND schemaname = 'carto-workshops'")
    for k, v in indexes.items():
        if k == 'rows':
            for itr in v: 
                if  'the_geom_webmercator_idx' in itr['indexname']:
                    checkInd.append(itr['indexname'])
                elif 'the_geom_idx' in itr['indexname']:
                    checkInd.append(itr['indexname'])
                elif '_pkey' in itr['indexname']:
                    checkInd.append(itr['indexname'])

    # if indexes and column names exists -> table cartodbified
    if len(checkInd) >= 3 and len(checkCol) >= 3:
        cartodbfied = 'yes'
    else:
        cartodbfied = 'no'

    # create graphs according on the table size
    try:
        table_size = sql.send("select pg_total_relation_size('"+ i + "')")
        for a,b in table_size.items():
            if a == 'rows':
                for itr in b:
                    table_size = itr['pg_total_relation_size']

        # bytes to MB
        val = table_size/1048576.00

        #Normalize values
        norm = ((val-min_val)/(max_val-min_val))*100.00

        # print graphs
        if norm >= 0 and norm <= 1:
            print '{tableName:60}:\t {space:|<1} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 1 and norm <= 5:
            print '{tableName:60}:\t {space:|<5} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 5 and norm <= 10:
            print '{tableName:60}:\t {space:|<10} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 10 and norm <= 20:
            print '{tableName:60}:\t {space:|<20} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 20 and norm <= 30:
            print '{tableName:60}:\t {space:|<30} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 30 and norm <= 40:
            print '{tableName:60}:\t {space:|<40} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 40 and norm <= 50:
            print '{tableName:60}:\t {space:|<50} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 50 and norm <= 60:
            print '{tableName:60}:\t {space:|<60} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 60 and norm <= 70:
            print '{tableName:60}:\t {space:|<70} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 70 and norm <= 80:
            print '{tableName:60}:\t {space:|<80} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 80 and norm <= 90:
            print '{tableName:60}:\t {space:|<90} {size} {mb}; cartodbfied= {cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
        elif norm > 90 and norm <= 100:
            print '{tableName:60}:\t {space:|<100} {size} {mb}; cartodbfied={cartodbfied};'.format(tableName= str(i),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)

    except:
        print 'Error at: ' + str(i)        

print '\nThere are: ' + str(sum) + ' datasets in this account'
