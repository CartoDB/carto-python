import argparse
import glob
import logging
import os
import re
import time
import warnings

from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager
from carto.sql import SQLClient

warnings.filterwarnings('ignore')

# python import_and_merge.py "files/*.csv"

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Import a folder with CSV files (same structure) and merge \
    them into one dataset')

parser.add_argument('folder_name', type=str,
                    help='Set the name of the folder where' +
                    ' you store your files and' +
                    ' the format of the files, for example:' +
                    ' "files/*.csv"')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'] if 'CARTO_ORG' in os.environ else '',
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'] if 'CARTO_API_URL' in os.environ else '',
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'] if 'CARTO_API_KEY' in os.environ else '',
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

# Set authentification to CARTO
if args.CARTO_BASE_URL and args.CARTO_API_KEY and args.organization:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# get username from base_url
substring = re.search('https://(.+?).carto.com', args.CARTO_BASE_URL)
if substring:
    username = substring.group(1)

# SQL wrapper
sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

# Dataset manager
dataset_manager = DatasetManager(auth_client)

# define path of the files
path = os.getcwd()

file_folder = glob.glob(path + '/' + args.folder_name)

# import files from the path to CARTO
table_name = []

for i in file_folder:
    table = dataset_manager.create(i)
    logger.info(
        'Table imported: {table}'.format(table=table.name))
    table_name.append(table.name)

# define base table to insert all rows from other files
base_table = table_name[0]

# select all rows from table except cartodb_id to avoid possible errors
columns_table = "select string_agg(column_name,',')" + \
    " FROM information_schema.columns" + \
    " where table_schema = '" + username + "' and table_name = '" + \
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
print('\nURL of dataset is: \
      https://{org}.carto.com/u/{username}/dataset/{data}'). \
      format(org=args.organization,
             username=username,
             data=(base_table + "_merged"))
