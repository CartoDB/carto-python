```python
import argparse
import logging
import os
import warnings

from carto.datasets import DatasetManager
from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient

warnings.filterwarnings('ignore')

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Exports a dataset')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG']  if 'CARTO_ORG' in os.environ else '',
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

parser.add_argument('--format', dest='EXPORT_FORMAT',
                    default='gpkg',
                    help='The format of the file to be exported. ' +
                    'Default is `gpkg`')

parser.add_argument('--save_folder', dest='SAVE_FOLDER',
                    default='.',
                    help='The folder path to download the datasets, by default is the path where the script is executes')

args = parser.parse_args()


# Authenticate to CARTO account
if args.CARTO_BASE_URL and args.CARTO_API_KEY and args.organization:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# SQL wrapper
sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

# Dataset manager
dataset_manager = DatasetManager(auth_client)

# Get all datasets from account
datasets = dataset_manager.all()

# donwload datasets from account
for tablename in datasets:
    query = 'SELECT * FROM {table_name}'.format(table_name=tablename) 
    try:
        result = sql.send(query, format=args.EXPORT_FORMAT)
        filename = "carto_{table_name}.{format}".format(table_name=tablename,format=args.EXPORT_FORMAT)
        with open(filename, 'w') as f:
            f.write(result)
        f.close()

        logger.info("CARTO dataset saved: " + filename)
    except:
        logger.info("CARTO dataset {table_name} haven't been exported".format(table_name=tablename))

```