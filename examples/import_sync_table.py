from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sync_tables import SyncTableJobManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
printer = pprint.PrettyPrinter(indent=4)

organization = 'cartoworkshops'
CARTO_API_KEY = os.environ['CARTO_API_KEY']
CARTO_BASE_URL ='https://carto-workshops.carto.com/api/'

# work with CARTO entities. DatasetManager encapsulates information of a table
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
syncTableManager = SyncTableJobManager(auth_client)
# 'https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj?method=export&format=Shapefile',900,auth_client

syncTable = syncTableManager.create('https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj?method=export&format=Shapefile',900)

# check methods to apply on the sync table
print [method for method in dir(syncTable) if(callable(getattr(syncTable,method)))]

# return the id of the sync
print syncTable.get_id()

while(syncTable.state != 'created'):
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

# syncTable.force_sync
syncTable.refresh()
syncTable.force_sync()

print syncTable.state

# delete sync table

# syncTable.refresh()
# syncTable.delete