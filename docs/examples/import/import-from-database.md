```python
import argparse
import json
import logging
import os
import re
import warnings

from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager

warnings.filterwarnings('ignore')

# python import_from_database.py --connection='{ \
#   "connector": { \
#     "provider": "hive", \
#     "connection": { \
#       "server":"YOUR_SERVER_IP", \
#       "database":"default", \
#       "username":"cloudera", \
#       "password":"cloudera" \
#     },
#     "schema": "default", \
#     "table": "order_items" \
#   }
# }'

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='External database connector')

parser.add_argument('--connection', type=str, dest='connection',
                    help='An external database connection JSON object')

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

# Dataset manager
dataset_manager = DatasetManager(auth_client)

connection = json.loads(args.connection.replace("\\", ""))
logger.info(connection)

table = dataset_manager.create(None, None, connection=connection)
logger.info(
    'Table imported: {table}'.format(table=table.name))
```
