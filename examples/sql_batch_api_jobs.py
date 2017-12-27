import argparse
import logging
import os
import warnings

from carto.auth import APIKeyAuthClient
from carto.sql import BatchSQLClient

warnings.filterwarnings('ignore')

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Create a Batch SQL API job')

parser.add_argument('operation', type=str, default=None,
                    choices=['create', 'read', 'update', 'cancel'],
                    help='Set the batch operation that you want to apply')

parser.add_argument('--query', type=str, dest='query',
                    help='Set the query that you want to apply')

parser.add_argument('--job_id', type=str, dest='job_id',
                    help='Set the id of the job to check')

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

# Set authentification to CARTO
if args.CARTO_BASE_URL and args.CARTO_API_KEY and args.organization:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
    batchSQLClient = BatchSQLClient(auth_client)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# Batch SQL API operations
if args.operation == 'create':
    # create a batch api job
    createJob = batchSQLClient.create(args.query)
    for a, b in createJob.items():
        logger.info('{key}: {value}'.format(key=a, value=b))
elif args.operation == 'read':
    readJob = batchSQLClient.read(args.job_id)
    for a, b in readJob.items():
        logger.info('{key}: {value}'.format(key=a, value=b))
elif args.operation == 'update':
    updateJob = batchSQLClient.update(args.job_id, args.query)
    for a, b in updateJob.items():
        logger.info('{key}: {value}'.format(key=a, value=b))
elif args.operation == 'cancel':
    cancelJob = batchSQLClient.cancel(args.job_id)
    for a, b in cancelJob.items():
        logger.info('{key}: {value}'.format(key=a, value=b))
else:
    logger.info("You have not written a correct operation option")
