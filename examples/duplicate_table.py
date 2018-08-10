#!/usr/bin/env python

import argparse
import os
import sys
import logging
import time

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from carto.sql import CopySQLClient

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()


usage_example="""Examples of use:

 ./duplicate_table.py                          \\
      --source-url     https://source.carto.com \\
      --source-api-key 12345                    \\
      --source-table   my_table                 \\
      --dest-url       https://dest.carto.com   \\
      --dest-api-key   67890

  ./duplicate_table.py                          \\
      --source-url     https://source.carto.com \\
      --source-api-key 12345                    \\
      --source-table   my_table                 \\
      --dest-table     my_copy
"""

# Set input arguments
parser = argparse.ArgumentParser(
    description=("An utility to COPY a table from one account to another"),
    epilog=usage_example,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument(
    '--source-url',
    type=str,
    dest='CARTO_SOURCE_URL',
    default=os.environ.get('CARTO_API_URL', ''),
    required=True,
    help=('Set the source base URL. For example: '
          'https://source.carto.com/ '
          '(defaults to env variable CARTO_API_URL)')
)

parser.add_argument(
    '--source-api-key',
    dest='CARTO_SOURCE_API_KEY',
    default=os.environ.get('CARTO_API_KEY', ''),
    required=True,
    help=('API key of the source account '
          '(defaults to env variable CARTO_API_KEY)')
)

parser.add_argument(
    '--source-table',
    dest='SOURCE_TABLE',
    required=True,
    help='Name of the source table to copy'
)

parser.add_argument(
    '--dest-url',
    type=str,
    dest='CARTO_DEST_URL',
    default=os.environ.get('CARTO_API_URL', ''),
    required=True,
    help=('Set the destination base URL. For example: '
          'https://dest.carto.com/ '
          '(defaults to the source URL)')
)

parser.add_argument(
    '--dest-api-key',
    dest='CARTO_DEST_API_KEY',
    default=os.environ.get('CARTO_API_KEY', ''),
    required=True,
    help=('API key of the destination account '
          '(defaults to the source API key)')
)

parser.add_argument(
    '--dest-table',
    dest='DEST_TABLE',
    required=True,
    help='Name of the destination table (defaults to SOURCE_TABLE)'
)


args = parser.parse_args()

sys.exit()

# Set authentification to CARTO
auth_client = APIKeyAuthClient(
    args.CARTO_SOURCE_URL,
    args.CARTO_SOURCE_API_KEY
)


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

# COPY TO example
query = 'COPY copy_example TO stdout WITH (FORMAT csv, HEADER true)'
output_file = 'files/copy_export.csv'
copyClient.copyto_file_path(query, output_file)
logger.info('Table copied to %s' % output_file)

# Truncate the table to make this example repeatable
sqlClient.send('TRUNCATE TABLE copy_example RESTART IDENTITY')
