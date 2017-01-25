from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.file_import import FileImportJob
import warnings
warnings.filterwarnings('ignore')
import os
from carto.sql import SQLClient
from carto.datasets import DatasetManager
import time
import logging
import glob

# Logger (better than print)
import logging
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
import argparse
parser = argparse.ArgumentParser(
    description='Create a sync table from a URL')

parser.add_argument('username', type=str, 
                    help='Set the username of account.')

parser.add_argument('folder_name', type=str,
                    help='Set the name of the folder where' +
                    ' you store your files and' +
                    ' the format of the files, for example:' +
                    ' "examples/files/*.csv"')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

base_url = 'https://'+ args.username+'.carto.com/api/'

# Set authentification to CARTO
auth_client = APIKeyAuthClient(
    base_url, args.CARTO_API_KEY, args.organization)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(base_url, args.CARTO_API_KEY))

# Dataset manager

dataset_manager = DatasetManager(auth_client)

# define path of the files
path = os.getcwd()

file_folder = glob.glob(path + '/' + args.folder_name)

# import files from the path to CARTO
table_name = []

for i in file_folder:
    fi = FileImportJob(i, auth_client)
    fi.run()

    time.sleep(2)

    fi.refresh()
    if fi.success == True:
        while (fi.state != 'complete'):
            fi.refresh()
            time.sleep(2)

            if fi.state == 'complete':
                # print name of the imported table
                logger.info(
                    'Table imported: {table}'.format(table=fi.table_name))
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
    " where table_schema = '" + args.username + "' and table_name = '" + \
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
logger.info('Tables merged')
