import argparse
import logging
import os
import warnings

from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager
from carto.sql import SQLClient

warnings.filterwarnings('ignore')

# python check_query.py "select version()"

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Check if query can be optimized')
parser.add_argument('queryUser', type=str,
                    help='Set query to analyze')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'] if 'CARTO_ORG' in os.environ else '',
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'] if 'CARTO_API_URL' in os.environ else '',
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'] if 'CARTO_API_KEY' in os.environ else '',
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

# Authenticate to CARTO account
if args.CARTO_BASE_URL and args.CARTO_API_KEY and args.organization:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
    dataset_manager = DatasetManager(auth_client)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# SQL wrapper
sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

query = sql.send('EXPLAIN ANALYZE ' + args.queryUser)

for key, value in query.items():
    if key == 'rows':
        for itr in value:
            logger.info(itr)
    if key == 'time':
        logger.info(str(key) + ': ' + str(value))

query_arr = args.queryUser.upper().split()


for i in query_arr:
    if i == '*':
        logger.warn('Do you need all columns? ' +
                    'You can improve the performance ' +
                    'by only selecting the needed ' +
                    'columns instead of doing a \"SELECT *\" statement')
    if i == 'WHERE':
        logger.warn('Have you applied indexes on the columns ' +
                    'that you use after the WHERE statement?')
    if i == 'the_geom' or i == 'the_geom_webmercator':
        logger.warn('If the geometry is a polygon,' +
                    ' have you simplified the geometries ' +
                    'with the ST_Simplify() function?')
