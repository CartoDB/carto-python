from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.file_import import FileImportJob
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


# imports the file to CARTO
fi = FileImportJob("https://data.cityofnewyork.us/api/geospatial/r8nu-ymqj?method=export&format=Shapefile",auth_client)
fi.run()


fi.refresh()

if fi.success == True:
  while (fi.state != 'complete'):
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


