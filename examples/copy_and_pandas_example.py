import argparse
import os
import sys
import logging
import pandas as pd

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from carto.sql import CopySQLClient

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()


# set input arguments
parser = argparse.ArgumentParser(description='Example of CopySQLClient usage with COPY feature and pandas (file-based interface)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ.get('CARTO_API_URL', ''),
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ.get('CARTO_API_KEY', ''),
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')


args = parser.parse_args()

# Set authentification to CARTO
if args.CARTO_BASE_URL and args.CARTO_API_KEY:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY)
else:
    logger.error('You need to provide valid credentials, run with '
                 '-h parameter for details')
    sys.exit(1)

# Create and cartodbfy a table
sqlClient = SQLClient(auth_client)
sqlClient.send("""
    CREATE TABLE IF NOT EXISTS copy_example (
      the_geom geometry(Geometry,4326),
      name text,
      age integer
    )
    """)
sqlClient.send("SELECT CDB_CartodbfyTable(current_schema, 'copy_example')")

copyClient = CopySQLClient(auth_client)

# COPY FROM example
logger.info("COPY'ing FROM file...")
query = ('COPY copy_example (the_geom, name, age) '
         'FROM stdin WITH (FORMAT csv, HEADER true)')
result = copyClient.copyfrom_file_path(query, 'files/copy_from.csv')
logger.info('result = %s' % result)

# COPY TO example with pandas DataFrame
logger.info("COPY'ing TO pandas DataFrame...")
query = 'COPY copy_example TO stdout WITH (FORMAT csv, HEADER true)'
result = copyClient.copyto_stream(query)
df = pd.read_csv(result)
logger.info(df.head())

# Truncate the table to make this example repeatable
sqlClient.send('TRUNCATE TABLE copy_example RESTART IDENTITY')
