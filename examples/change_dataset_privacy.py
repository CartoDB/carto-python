import argparse
import logging
import os
import warnings

from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager

warnings.filterwarnings('ignore')

# python change_dataset_privacy.py tornados LINK

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Changes the privacy of a dataset')

parser.add_argument('dataset_name', type=str,
                    help='The name of the dataset in CARTO')

parser.add_argument('privacy', type=str,
                    help='One of: LINK, PUBLIC, PRIVATE')

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
    dataset_manager = DatasetManager(auth_client)
    dataset = dataset_manager.get(args.dataset_name)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# PRIVATE, PUBLIC, LINK
dataset.privacy = args.privacy
dataset.save()

logger.info("Done!")
