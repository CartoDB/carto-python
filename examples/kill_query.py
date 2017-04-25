from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
import warnings
warnings.filterwarnings('ignore')
import os
from carto.sql import SQLClient

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
    description='Return the names of all maps or' +
    ' display information from a specific map')

parser.add_argument('pid', type=str,
                    default=None,
                    help='Set the pid of the query to kill')
parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()


# Set authentification to CARTO
auth_client = APIKeyAuthClient(
    args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

queries = "SELECT pg_cancel_backend('" + args.pid + \
    "') from pg_stat_activity where usename=current_user;"

try:
    sql.send(queries)
    logger.info('Query killed')
except:
    logger.warn('Something went wrong')
