import argparse
import logging
import os
from prettytable import PrettyTable
import warnings

from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager
from carto.sql import SQLClient

warnings.filterwarnings('ignore')

# python table_info.py tornados_11

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()


# set input arguments
parser = argparse.ArgumentParser(
    description='Return columns and its types, indexes,' +
    ' functions and triggers of a specific table')

parser.add_argument('dataset_name', type=str,
                    help='Set the name of the table to explore')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/ ' +
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


# display and count all datasets of account
all_datasets = dataset_manager.all()

# set the arrays to store the values that will be used to display tables
results_col = []
results_index = []
results_func = []
results_trig = []
for i in all_datasets:
    if (i.table.name == args.dataset_name):
        print('\nGeneral information')
        table_general = PrettyTable([
            'Table name',
            'Number of rows',
            'Size of the table (MB)',
            'Privacy of the table',
            'Geometry type'
        ])

        table_general.add_row([
            i.table.name,
            i.table.row_count,
            str(round(i.table.size/1048576.00, 2)),
            str(i.table.privacy),
            str(i.table.geometry_types)
        ])

        print(table_general)

        columns_table = "select column_name, data_type FROM information_schema.columns \
        WHERE table_schema = '" + i.permission.owner.username + "'\
        AND table_name ='" + i.table.name + "';"

        # print columns_table
        print('\nThe columns and their data types are: \n')
        columnAndTypes = sql.send(columns_table)
        for key, value in columnAndTypes.items():
            if key == 'rows':
                for itr in value:
                    results_col.append([
                        itr['column_name'],
                        itr['data_type']
                    ])
        table_col = PrettyTable(
            ['Column name', 'Data type'])
        table_col.align['Column name'] = 'l'
        table_col.align['Data type'] = 'r'
        for row in results_col:
            table_col.add_row(row)

        print(table_col)
        # get all indexes of the table
        print('\nIndexes of the tables: \n')
        indexes = sql.send("select indexname, indexdef from pg_indexes \
          where tablename = '" + i.table.name + "' \
          AND schemaname = '" + i.permission.owner.username + "'")
        for k, v in indexes.items():
            if k == 'rows':
                for itr in v:
                    results_index.append([itr['indexname'], itr['indexdef']])
        table_index = PrettyTable(
            ['Index name', 'Index definition'])
        table_index.align['Index name'] = 'l'
        table_index.align['Index definition'] = 'r'
        for row_ind in results_index:
            table_index.add_row(row_ind)
        print(table_index)

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
                    results_func.append(itr)
        table_func = PrettyTable(['Function name'])
        for row in results_func:
            table_func.add_row([row])

        print(table_func)

        # triggers
        print('\nTriggers of the account: \n')
        # save oid of tables in an object
        oid = sql.send(
            "select pg_class.oid as _oid, pg_class.relname from \
             pg_class, pg_roles, pg_namespace \
             where pg_roles.oid = pg_class.relowner \
             and pg_roles.rolname = current_user \
             and pg_namespace.oid = pg_class.relnamespace \
             and pg_class.relkind = 'r'")
        for c, d in oid.items():
            if c == 'rows':
                for itr in d:
                    # if the name of the table matches with the name of the
                    # input table
                    # save the oid of the table in the table_oid variable
                    if itr['relname'] == args.dataset_name:
                        table_oid = itr['_oid']

        # get triggers of the table
        triggers = sql.send(
            "SELECT tgname FROM pg_trigger WHERE tgrelid =" + str(table_oid))

        for t in triggers['rows']:
            results_trig.append(str(t['tgname']))
        table_trigger = PrettyTable(['Trigger Name'])

        for row in results_trig:
            table_trigger.add_row([row])

        print(table_trigger)
