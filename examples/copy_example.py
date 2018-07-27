import argparse
import os
import sys
import logging
import time

from carto.auth import APIKeyAuthClient
from carto.sql import BatchSQLClient
from carto.sql import CopySQLClient

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()


# set input arguments
parser = argparse.ArgumentParser(description='External database connector')

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
if args.CARTO_BASE_URL and args.CARTO_API_KEY:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)


LIST_OF_SQL_QUERIES = [
    'DROP TABLE IF EXISTS copy_example;'
    """
    CREATE TABLE copy_example (
      the_geom geometry(Geometry,4326),
      name text,
      age integer
    );
    """,
    "SELECT CDB_CartodbfyTable(current_schema, 'copy_example');"
]

BATCH_TERMINAL_STATES = ['done', 'failed', 'cancelled', 'unknown']

# Create and cartodbfy a table
batchSQLClient = BatchSQLClient(auth_client)
job = batchSQLClient.create(LIST_OF_SQL_QUERIES)
while not job['status'] in BATCH_TERMINAL_STATES:
    time.sleep(1)
    job = batchSQLClient.read(job['job_id'])
if job['status'] != 'done':
    logger.error('Could not create and cartodbfy table')
    logger.error(job['failed_reason'])
    sys.exit(1)

copyClient = CopySQLClient(auth_client)

# COPY FROM example
query = 'COPY copy_example (the_geom, name, age) FROM stdin WITH (FORMAT csv, HEADER true)'
with open('files/copy_from.csv') as data:
    result = copyClient.copyfrom(query, data)
logger.info(result)

# COPY TO example
query = 'COPY copy_example TO stdout WITH (FORMAT csv, HEADER true)'
data = copyClient.copyto(query)
with open('files/copy_export.csv', 'wb') as f:
    for block in data.iter_content(1024):
        f.write(block)
