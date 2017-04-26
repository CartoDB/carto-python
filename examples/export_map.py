from carto.auth import APIKeyAuthClient
import warnings
warnings.filterwarnings('ignore')
import os
from carto.visualizations import VisualizationManager
import logging
import re

# python export.py "results_1ertour_2012_1 map"

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
    description='Export a visualization')

parser.add_argument('map_name', type=str,
                    help='The name of the map in CARTO')

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

# get username from base_url
substring = re.search('https://(.+?).carto.com', args.CARTO_BASE_URL)
if substring:
    username = substring.group(1)

visualization = VisualizationManager(auth_client).get(args.map_name)

url = visualization.export()

print('\nURL of .carto file is: ' + (url))