import argparse
import os
import sys
import logging
import time

from carto.auth import APIKeyAuthClient
from carto.sql import BatchSQLClient
from carto.sql import CopySQLClient

# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = Trueo


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
    'DROP TABLE IF EXISTS tl_2014_census_tracts;',
"""
CREATE TABLE tl_2014_census_tracts (
 aland                  double precision,
 awater                 double precision,
 cartodb_id             integer,
 countyfp               text,
 created_at             date,
 geoid                  text,
 mtfcc                  text,
 name                   text,
 statefp                text,
 the_geom               geometry(Geometry,4326),
 tractce                text,
 updated_at             date
);
""",
    "SELECT CDB_CartodbfyTable(current_schema, 'tl_2014_census_tracts');"
]

BATCH_TERMINAL_STATES = ['done', 'failed', 'cancelled', 'unknown']

logger.info("Dropping, re-creating and cartodbfy'ing the table through the Batch API...")
batchSQLClient = BatchSQLClient(auth_client)
job = batchSQLClient.create(LIST_OF_SQL_QUERIES)
while not job['status'] in BATCH_TERMINAL_STATES:
    time.sleep(1)
    job = batchSQLClient.read(job['job_id'])
if job['status'] != 'done':
    logger.error('Could not create and cartodbfy table')
    logger.error(job['failed_reason'])
    sys.exit(1)
logger.info("Table created and cartodbfy'ed")

copyClient = CopySQLClient(auth_client)

# COPY FROM example
logger.info("COPY'ing the table FROM the file...")
query = 'COPY tl_2014_census_tracts (the_geom,statefp,countyfp,tractce,geoid,name,cartodb_id,aland,awater,created_at,updated_at,mtfcc) FROM stdin WITH (FORMAT csv, HEADER true)'
input_file = '/home/rtorre/src/cartodb-tests/sql_copy_perf/tl_2014_census_tracts.csv'

# with open(input_file) as data:
#     result = copyClient.copyfrom(query, data)

def read_in_chunks(file_object, chunk_size=8192):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

with open(input_file, 'rb') as fd:
    result = copyClient.copyfrom(query, read_in_chunks(fd))

logger.info(result)
logger.info("Table populated")
