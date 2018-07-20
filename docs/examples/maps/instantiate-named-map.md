```python
import argparse
import json
import logging
import os
import warnings

from carto.auth import APIKeyAuthClient
from carto.maps import NamedMapManager

warnings.filterwarnings('ignore')

# python instantiate_named_map.py "python_sdk_test_map" \
# "files/instantiate_map.json" "example_token"

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Instantiates a named map')

parser.add_argument('named_map_id', type=str,
                    help='The ID of a previously created named map')

parser.add_argument('template_json', type=str,
                    help='JSON Template file to instantiate the map with')

parser.add_argument('named_map_token', type=str,
                    help='A valid token set when the named map was created')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG']  if 'CARTO_ORG' in os.environ else '',
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
    named_map_manager = NamedMapManager(auth_client)
    named_map = named_map_manager.get(args.named_map_id)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

with open(args.template_json) as template_json:
    template = json.load(template_json)

named_map.instantiate(template, args.named_map_token)

print('Done!')
```
