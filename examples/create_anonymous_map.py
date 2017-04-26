import argparse
from carto.auth import APIKeyAuthClient
from carto.maps import AnonymousMap
import json
import logging
import os
import warnings
warnings.filterwarnings('ignore')

# python create_anonymous_map.py "files/anonymous_map.json"

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Creates an anonymous map')

parser.add_argument('anonymous_map_json', type=str,
                    help='Path to the anonymous map JSON description file')

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

anonymous = AnonymousMap(auth_client)
with open(args.anonymous_map_json) as anonymous_map_json:
    template = json.load(anonymous_map_json)

# Create anonymous map
anonymous.instantiate(template)

print('Anonymous map created with layergroupid: ' + anonymous.layergroupid)