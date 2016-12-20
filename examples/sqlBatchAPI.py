from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sql import BatchSQLManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
printer = pprint.PrettyPrinter(indent=4)

organization = 'cartoworkshops'
CARTO_API_KEY = os.environ['CARTO_API_KEY']
CARTO_BASE_URL ='https://carto-workshops.carto.com/api/'

# authenticate to CARTO
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)

batchManager = BatchSQLManager(auth_client)

# check methods to apply on the sync table
print [method for method in dir(batchManager) if(callable(getattr(batchManager,method)))]

# get all batch api jobs

batchManager.all()



