from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
printer = pprint.PrettyPrinter(indent=4)
from carto.sql import SQLClient
import sys

if len(sys.argv) <= 1:
    print 'You have to pass 1 input arguments.Add the PID of the query,' + \
        'run the running_queries.py script to know it'

organization = 'cartoworkshops'
CARTO_BASE_URL = 'https://carto-workshops.carto.com/api/'
CARTO_API_KEY = os.environ['CARTO_API_KEY']


# Authenticate to CARTO account
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

queries = "SELECT pg_cancel_backend('"+sys.argv[1] + \
    "') from pg_stat_activity where usename=current_user;"

result = sql.send(queries)
