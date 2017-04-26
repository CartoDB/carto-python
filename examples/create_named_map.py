import argparse
from carto.auth import APIKeyAuthClient
from carto.maps import NamedMapManager, NamedMap
import json
import logging
import os
import warnings
warnings.filterwarnings('ignore')

# python create_named_map.py "files/named_map.json"

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Creates a named map')

parser.add_argument('named_map_json', type=str,
                    help='Path to the named map JSON description file')

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

named_map_manager = NamedMapManager(auth_client)
n = NamedMap(named_map_manager.client)

with open(args.named_map_json) as named_map_json:
    template = json.load(named_map_json)

# Create named map
named = named_map_manager.create(template=template)

print('Named map created with ID: ' + named.template_id)