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
    print 'You have to pass 1 input arguments.Add query'

organization = 'cartoworkshops'
CARTO_BASE_URL = 'https://carto-workshops.carto.com/api/'
CARTO_API_KEY = os.environ['CARTO_API_KEY']


# Authenticate to CARTO account
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

query = sql.send('EXPLAIN ANALYZE ' + str(sys.argv[1]))

print sys.argv[1]
for key, value in query.items():
    if key == 'rows':
        for itr in value:
            print itr
    if key == 'time':
        print str(key) + ': ' + str(value)

query_arr = str(sys.argv[1]).upper().split()


for i in query_arr:
    if i == '*':
        print '\nPERFORMANCE WARNING: '
        print 'Do you need all the columns? You can improve the performance \
        by only selecting the needed columns instead of doing a SELECT * statement'
    if i == 'WHERE':
        print '\nPERFORMANCE WARNING: '
        print 'Have you applied indexes on the columns \
        that you use after the WHERE statement?'
    if i == 'the_geom' or i == 'the_geom_webmercator':
        print '\nPERFORMANCE WARNING: '
        print 'If the geometry is a polygon, have you simplified the geometries \
        with the ST_Simplify() function?'
