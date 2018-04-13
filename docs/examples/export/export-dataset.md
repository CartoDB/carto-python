```python
import argparse
import logging
import os
import warnings

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient

warnings.filterwarnings('ignore')

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Exports a dataset')

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

parser.add_argument('--dataset', dest='DATASET',
                    help='The name of the dataset')

parser.add_argument('--format', dest='EXPORT_FORMAT',
                    default='csv',
                    help='The format of the file to be exported. ' +
                    'Default is `csv`')

args = parser.parse_args()


# Authenticate to CARTO account
if args.CARTO_BASE_URL and args.CARTO_API_KEY and args.organization:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# SQL wrapper
sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

query = "select * from " + args.DATASET + ""
result = sql.send(query, format=args.EXPORT_FORMAT)

filename = args.DATASET + "." + args.EXPORT_FORMAT
with open(filename, 'w') as f:
    f.write(result)
f.close()

print("File saved: " + filename)
```
