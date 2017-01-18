from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sync_tables import SyncTableJobManager
import warnings
warnings.filterwarnings('ignore')
import os
import time
import logging

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

parser.add_argument('url',type=str,
                    help='Set the URL of data to sync. Add it in double quotes')
parser.add_argument('sync_time',type=int,
                    help='Set the time to sync your table in seconds (min: 900s)')
parser.add_argument('--organization', type=str,dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example: https://username.carto.com/api/ (defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

# Set authentification to CARTO
auth_client = APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
syncTableManager = SyncTableJobManager(auth_client)

syncTable = syncTableManager.create(args.url,args.sync_time)


# return the id of the sync
logging.debug((syncTable.get_id()))

while(syncTable.state != 'created'):
    time.sleep(5)
    syncTable.refresh()
    logging.debug(syncTable.state)
    if (syncTable.state == 'failure'):
        logging.warn('The error code is: ' + str(syncTable.error_code))
        logging.warn('The error message is: ' + str(error_message))
        break

    if (syncTable.state == 'created'):
        logging.info(syncTable.name)
        break

# force sync
syncTable.refresh()
syncTable.force_sync()

logging.debug(syncTable.state)
