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

# display and count all datasets of account
all_datasets = dataset_manager.all()

# sum = 0

# for i in all_datasets:
#     sum = sum + 1

#     show all features of each dataset

#     print '\nName of the table: ' + str(i.table.name)
#     print 'Total number of rows: ' + ' ' + str(i.table.row_count) + ' rows'
#     print 'Size of the table: ' + str(i.table.size/1048576.00) + ' MB'
#     print 'Privacy of the table: ' + str(i.table.privacy)
#     print 'Geometry type: ' + str(i.table.geometry_types)

    # columns_table = "select column_name, data_type FROM information_schema.columns \
    # WHERE table_schema = '" + \
    #     i.permission.owner.username + \
    #     "' AND table_name ='" + i.table.name + "';"

#     checkCol = []
#     # print columns_table
#     print '\nThe columns and their data types are: \n'
#     columnAndTypes = sql.send(columns_table)
#     for key, value in columnAndTypes.items():
#         if key == 'rows':
#             for itr in value:
#                 print '\tThe column: ' + str(itr['column_name']) + \
#                 ' is: ' + str(itr['data_type']) + ' type'
#                 if 'cartodb_id' == itr['column_name']:
#                     checkCol.append(True)
#                 elif 'the_geom' == itr['column_name']:
#                     checkCol.append(True)
#                 elif 'the_geom_webmercator' == itr['column_name']:
#                     checkCol.append(True)

#     checkInd = []
#     # get all indexes of the table
#     #print '\nIndexes of the tables: \n'
#     indexes = sql.send("select indexname, indexdef from pg_indexes \
#       where tablename = '" + i.table.name + "' \
#       AND schemaname = '" + i.permission.owner.username + "'")
#     for k, v in indexes.items():
#         if k == 'rows':
#             for itr in v:
#                 print '\tThe index: ' + str(itr['indexname']) + \
#                 ' is: ' + str(itr['indexdef'])
#                 if str(i.table.name
#                        + '_the_geom_webmercator_idx') == itr['indexname']:
#                     checkInd.append(itr['indexname'])
#                 elif str(i.table.name+'_the_geom_idx') == itr['indexname']:
#                     checkInd.append(itr['indexname'])
#                 elif str(i.table.name+'_pkey') == itr['indexname']:
#                     checkInd.append(itr['indexname'])

#     # get all functions of user account
#     print '\nFunctions of the account: \n'
#     #functions = sql.send("SELECT proname FROM  pg_catalog.pg_namespace n JOIN pg_catalog.pg_proc p ON pronamespace = n.oid WHERE nspname = '"+ i.permission.owner.username +"'")
#     functions = sql.send(
#         "select pg_proc.oid as _oid, pg_proc.*, \
#         pg_get_functiondef(pg_proc.oid) as definition from \
#         pg_proc, pg_roles where pg_proc.proowner = pg_roles.oid \
#         and pg_roles.rolname = '" + i.permission.owner.username + "'")
#     for a, b in functions.items():
#         if a == 'rows':
#             for itr in b:
#                print itr

#     # triggers
#     print '\nTriggers of the account: \n'
    # # save oid of tables in an object
    # oid = sql.send(
    #     "select pg_class.oid as _oid, pg_class.relname from pg_class, \
    #     pg_roles, pg_namespace where pg_roles.oid = pg_class.relowner \
    #     and pg_roles.rolname = current_user and pg_namespace.oid = pg_class.relnamespace \
    #     and pg_class.relkind = 'r'")
    # for c, d in oid.items():
    #     if c == 'rows':
    #         for itr in d:
    #             # print name and oid for each table
    #             print str(itr['relname']) + ', its oid is: '
    #             + str(itr['_oid'])

    #             # if the name of the table matches with the name of the input table
    #             # save the oid of the table in the table_oid variable
    #             if itr['relname'] == i.table.name:
    #                 table_oid = itr['_oid']

#     # get triggers of the table
#     triggers = sql.send(
#         "SELECT tgname FROM pg_trigger WHERE tgrelid =" + str(table_oid))
#     for t in triggers['rows']:
#         print '\tThe name of the trigger is: ' + str(t['tgname'])
#     print '\n'

   

# create graph with the sizes of all datasets

arr_size = []


# create array with values of the table sizes
for i in all_datasets:
    arr_size.append(i.table.size)

# define variables that have the max and min values of the array
max_val = max(arr_size)/1048576.00
min_val = min(arr_size)/1048576.00

for i in all_datasets:

    # check column names
    checkCol = []
   
    columns_table = "select column_name, data_type FROM information_schema.columns \
    WHERE table_schema = '" + \
    i.permission.owner.username + \
    "' AND table_name ='" + i.table.name + "';"

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
   
    indexes = sql.send("select indexname, indexdef from pg_indexes \
      where tablename = '" + i.table.name + "' \
      AND schemaname = '" + i.permission.owner.username + "'")
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
    # create graphs
    val = i.table.size/1048576.00

    norm = ((val-min_val)/(max_val-min_val))*100.00

    # print graphs
    if norm > 0 and norm <= 1:
        print '{tableName}:\t {space:|<1} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 1 and norm <= 5:
        print '{tableName}:\t {space:|<5} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 5 and norm <= 10:
        print '{tableName}:\t {space:|<10} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 10 and norm <= 20:
        print '{tableName}:\t {space:|<20} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 20 and norm <= 30:
        print '{tableName}:\t {space:|<30} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 30 and norm <= 40:
        print '{tableName}:\t {space:|<40} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 40 and norm <= 50:
        print '{tableName}:\t {space:|<50} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 50 and norm <= 60:
        print '{tableName}:\t {space:|<60} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 60 and norm <= 70:
        print '{tableName}:\t {space:|<70} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 70 and norm <= 80:
        print '{tableName}:\t {space:|<80} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 80 and norm <= 90:
        print '{tableName}:\t {space:|<90} {size} {mb}; cartodbfied= {cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)
    elif norm > 90 and norm <= 100:
        print '{tableName}:\t {space:|<100} {size} {mb}; cartodbfied={cartodbfied}'.format(tableName= str(i.table.name),space='',size = str(round(val, 2)), mb ='MB', cartodbfied= cartodbfied)


# print '\nThere are: ' + str(sum) + ' datasets in this account'
