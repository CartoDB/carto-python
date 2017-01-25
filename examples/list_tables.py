from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
import warnings
warnings.filterwarnings('ignore')
import os
from carto.sql import SQLClient

# set input arguments
import argparse
parser = argparse.ArgumentParser(
    description='Return graph of tables ordered by size' +
    ' and indicating if they are cartodbfied or not')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/api/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()


# Authenticate to CARTO account
auth_client = APIKeyAuthClient(
    args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

# check all table name of account

all_tables = []

tables = sql.send(
    "select pg_class.relname from pg_class, pg_roles, pg_namespace" +
    " where pg_roles.oid = pg_class.relowner and " +
    "pg_roles.rolname = current_user " +
    "and pg_namespace.oid = pg_class.relnamespace and pg_class.relkind = 'r'")

for k, v in tables.items():
    if k == 'rows':
        for itr in v:
            all_tables.append(itr['relname'])


# define array to store all the table sizes

arr_size = []


# create array with values of the table sizes
for i in all_tables:
    try:
        size = sql.send("select pg_total_relation_size('" + i + "')")
        for a, b in size.items():
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


# define list of tuples
tupleList = []

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
                if 'the_geom_webmercator_idx' in itr['indexname']:
                    checkInd.append(itr['indexname'])
                elif 'the_geom_idx' in itr['indexname']:
                    checkInd.append(itr['indexname'])
                elif '_pkey' in itr['indexname']:
                    checkInd.append(itr['indexname'])

    # if indexes and column names exists -> table cartodbified
    if len(checkInd) >= 3 and len(checkCol) >= 3:
        cartodbfied = 'YES'
    else:
        cartodbfied = 'NO'

    # create graphs according on the table size
    try:
        table_size = sql.send("select pg_total_relation_size('" + i + "')")
        for a, b in table_size.items():
            if a == 'rows':
                for itr in b:
                    table_size = itr['pg_total_relation_size']

        # bytes to MB
        val = table_size/1048576.00

        # Normalize values
        norm = ((val-min_val)/(max_val-min_val))*100.00

        tupleList.append((i, val, norm, cartodbfied))

    except:
        print('Error at: ' + str(i))

# order list of tuples by norm size. From bigger to smaller
sorted_by_norm = sorted(tupleList, key=lambda tup: tup[2], reverse=True)

print('\n')

# print graphs
for z in sorted_by_norm:

    if z[2] >= 0 and z[2] <= 1:
        print('{tableName:60} {cartodbfied}:\t {space:|<1} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 1 and z[2] <= 5:
        print('{tableName:60} {cartodbfied}:\t {space:|<5} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 5 and z[2] <= 10:
        print('{tableName:60} {cartodbfied}:\t {space:|<10} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 10 and z[2] <= 20:
        print('{tableName:60} {cartodbfied}:\t {space:|<20} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 20 and z[2] <= 30:
        print('{tableName:60} {cartodbfied}:\t {space:|<30} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 30 and z[2] <= 40:
        print('{tableName:60} {cartodbfied}:\t {space:|<40} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 40 and z[2] <= 50:
        print('{tableName:60} {cartodbfied}:\t {space:|<50} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 50 and z[2] <= 60:
        print('{tableName:60} {cartodbfied}:\t {space:|<60} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 60 and z[2] <= 70:
        print('{tableName:60} {cartodbfied}:\t {space:|<70} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 70 and z[2] <= 80:
        print('{tableName:60} {cartodbfied}:\t {space:|<80} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 80 and z[2] <= 90:
        print('{tableName:60} {cartodbfied}:\t {space:|<90} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])
    elif z[2] > 90 and z[2] <= 100:
        print('{tableName:60} {cartodbfied}:\t {space:|<100} {size} {mb};').format(
            tableName=z[0], space='', size=str(round(z[1], 2)), mb='MB',  cartodbfied=z[3])


print('\nThere are: ' + str(sum) + ' datasets in this account')
