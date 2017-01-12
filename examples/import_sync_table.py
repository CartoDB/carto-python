from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sync_tables import SyncTableJobManager
import warnings
warnings.filterwarnings('ignore')
import os
import time
import logging

# Define logger

logging.basicConfig(
    level=logging.DEBUG,
    format=' %(asctime)s - %(levelname)s - %(message)s')


organization = os.environ['CARTO_ORG']
CARTO_BASE_URL = os.environ['CARTO_API_URL']
CARTO_API_KEY = os.environ['CARTO_API_KEY']

# work with CARTO entities. DatasetManager encapsulates information of a table
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
syncTableManager = SyncTableJobManager(auth_client)

syncTable = syncTableManager.create(
    'https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj' +
    '?method=export&format=Shapefile', 900)


# return the id of the sync
logging.debug((syncTable.get_id()))

while(syncTable.state != 'created'):
    time.sleep(5)
    syncTable.refresh()
    logging.debug(syncTable.state)
    if (syncTable.state == 'failure'):
        logging.debug('The error code is: ' + str(syncTable.error_code))
        logging.debug('The error message is: ' + str(error_message))
        break

    if (syncTable.state == 'created'):
        logging.debug(syncTable.name)
        break

# force sync
syncTable.refresh()
syncTable.force_sync()

logging.debug(syncTable.state)
