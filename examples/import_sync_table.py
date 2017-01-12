from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sync_tables import SyncTableJobManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
import time
printer = pprint.PrettyPrinter(indent=4)

organization = os.environ['CARTO_ORG']
CARTO_BASE_URL = os.environ['CARTO_API_URL']
CARTO_API_KEY = os.environ['CARTO_API_KEY']

# work with CARTO entities. DatasetManager encapsulates information of a table
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
syncTableManager = SyncTableJobManager(auth_client)
# 'https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj?method=export&format=Shapefile',900,auth_client

syncTable = syncTableManager.create(
    'https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj' +
    '?method=export&format=Shapefile', 900)


# return the id of the sync
print syncTable.get_id()

while(syncTable.state != 'created'):
    time.sleep(5)
    syncTable.refresh()
    print syncTable.state
    if (syncTable.state == 'failure'):
        print 'The error code is: ' + str(syncTable.error_code)
        print 'The error message is: ' + str(error_message)
        break

    if (syncTable.state == 'created'):
        print syncTable.name
        break

# force sync
syncTable.refresh()
syncTable.force_sync()

print syncTable.state

# delete sync table

# syncTable.refresh()
# syncTable.delete
