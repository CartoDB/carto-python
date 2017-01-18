from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.sql import BatchSQLClient
import warnings
warnings.filterwarnings('ignore')
import os

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
    description='Cancel a Batch SQL API job')
parser.add_argument('job_id', type=str,
                    help='Set the id of the job to check')
parser.add_argument('query', type=str,
                    help='Set the query that you want to apply')
parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/api/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

# Set authentification to CARTO
auth_client = APIKeyAuthClient(
    args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)

batchSQLClient = BatchSQLClient(auth_client)


# create a batch api job

updateJob = batchSQLClient.update(args.job_id, args.query)


for a, b in updateJob.items():
    logger.info('{key}: {value}'.format(key=a, value=b))
