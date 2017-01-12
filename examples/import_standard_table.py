from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.file_import import FileImportJob
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


# imports the file to CARTO
fi = FileImportJob(
    "https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj?" +
    "method=export&format=Shapefile", auth_client)
fi.run()


fi.refresh()

if fi.success == True:
    while (fi.state != 'complete'):
        if fi.state == 'importing':
            time.sleep(5)
        else:
            time.sleep(1)
        fi.refresh()
        # print status
        print fi.state
        if fi.state == 'complete':
            # print name of the imported table
            print fi.table_name
        if fi.state == 'failure':
            print "Import has failed"
            print fi.get_error_text
            break
else:
    print "Import has failed"
