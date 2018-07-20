```python
import argparse
import logging
import os
import time
import warnings

from carto.auth import APIKeyAuthClient
from carto.sync_tables import SyncTableJobManager

warnings.filterwarnings('ignore')

# python import_sync_table.py "DATASET_URL" 900

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Create a sync table from a URL')

parser.add_argument('url', type=str,
                    help='Set the URL of data to sync.' +
                    ' Add it in double quotes')

parser.add_argument('sync_time', type=int,
                    help='Set the time to sync your' +
                    ' table in seconds (min: 900s)')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'] if 'CARTO_ORG' in os.environ else '',
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL']  if 'CARTO_API_URL' in os.environ else '',
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
    syncTableManager = SyncTableJobManager(auth_client)
    syncTable = syncTableManager.create(args.url, args.sync_time)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# return the id of the sync
logging.debug((syncTable.get_id()))

while(syncTable.state != 'success'):
    time.sleep(5)
    syncTable.refresh()
    logging.debug(syncTable.state)
    if (syncTable.state == 'failure'):
        logging.warn('The error code is: ' + str(syncTable.error_code))
        logging.warn('The error message is: ' + str(syncTable.error_message))
        break

# force sync
syncTable.refresh()
syncTable.force_sync()

logging.debug(syncTable.state)
```
