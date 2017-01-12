from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
import warnings
warnings.filterwarnings('ignore')
import os
from carto.sql import SQLClient
import sys

if len(sys.argv) <= 1:
    print('You have to pass an input argument with the table name')

organization = os.environ['CARTO_ORG']
CARTO_BASE_URL = os.environ['CARTO_API_URL']
CARTO_API_KEY = os.environ['CARTO_API_KEY']


# Authenticate to CARTO account
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))


dataset_name = sys.argv[1]

# display and count all datasets of account
all_datasets = dataset_manager.all()


for i in all_datasets:
    if (i.table.name == dataset_name):
        # show all features of each dataset
        print('\nName of the table: {tabName}\nTotal number of rows: {tabRowCount:,} rows').format(tabName=str(i.table.name),tabRowCount=i.table.row_count)
        print('Size of the table: {tableSize} MB').format(tableSize=str(round(i.table.size/1048576.00,2)))
        print('Privacy of the table: {tabPrivacy} Geometry type: {tabGeom}').format(tabPrivacy=str(i.table.privacy),tabGeom=str(i.table.geometry_types))


        columns_table = "select column_name, data_type FROM information_schema.columns \
        WHERE table_schema = '" + i.permission.owner.username + "'\
        AND table_name ='" + i.table.name + "';"

        # print columns_table
        print('\nThe columns and their data types are: \n')
        columnAndTypes = sql.send(columns_table)
        for key, value in columnAndTypes.items():
            if key == 'rows':
                for itr in value:
                    print('\t{columnName}: {dataType}').format(columnName=str(itr['column_name']),dataType=str(itr['data_type']))

        # get all indexes of the table
        print('\nIndexes of the tables: \n')
        indexes = sql.send("select indexname, indexdef from pg_indexes \
          where tablename = '" + i.table.name + "' \
          AND schemaname = '" + i.permission.owner.username + "'")
        for k, v in indexes.items():
            if k == 'rows':
                for itr in v:
                    print('\t{indexName}: {indexDef}').format(indexName=str(itr['indexname']),indexDef=str(itr['indexdef']))

        # get all functions of user account
        print('\nFunctions of the account: \n')
        functions = sql.send(
            "select pg_proc.oid as _oid, pg_proc.*, \
            pg_get_functiondef(pg_proc.oid) as definition \
            from pg_proc, pg_roles where pg_proc.proowner = pg_roles.oid \
            and pg_roles.rolname = '" + i.permission.owner.username + "'")
        for a, b in functions.items():
            if a == 'rows':
                for itr in b:
                    print(itr)

        # triggers
        print('\nTriggers of the account: \n')
        # save oid of tables in an object
        oid = sql.send(
            "select pg_class.oid as _oid, pg_class.relname from \
             pg_class, pg_roles, pg_namespace where pg_roles.oid = pg_class.relowner \
             and pg_roles.rolname = current_user and pg_namespace.oid = pg_class.relnamespace \
             and pg_class.relkind = 'r'")
        for c, d in oid.items():
            if c == 'rows':
                for itr in d:
                    # if the name of the table matches with the name of the input table
                    # save the oid of the table in the table_oid variable
                    if itr['relname'] == dataset_name:
                        table_oid = itr['_oid']

        # get triggers of the table
        triggers = sql.send(
            "SELECT tgname FROM pg_trigger WHERE tgrelid =" + str(table_oid))
        for t in triggers['rows']:
            print('\t{tgName}').format(tgName=str(t['tgname']))
        print('\n')
