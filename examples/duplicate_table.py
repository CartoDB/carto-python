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

  ./duplicate_table.py                        \\
      --src-url      https://source.carto.com \\
      --src-api-key  12345                    \\
      --src-table    my_table                 \\
      --dst-url      https://dest.carto.com   \\
      --dst-api-key  67890

  ./duplicate_table.py                        \\
      --src-url      https://source.carto.com \\
      --src-api-key  12345                    \\
      --src-table    my_table                 \\
      --dst-table    my_copy
"""

# Set input arguments
parser = argparse.ArgumentParser(
    description=("An utility to COPY a table from one account to another"),
    epilog=usage_example,
    formatter_class=argparse.RawDescriptionHelpFormatter
)

parser.add_argument(
    '--src-url',
    type=str,
    dest='CARTO_SRC_URL',
    default=os.environ.get('CARTO_API_URL', ''),
    required=True,
    help=('Set the source base URL. For example: '
          'https://source.carto.com/ '
          '(defaults to env variable CARTO_API_URL)')
)

parser.add_argument(
    '--src-api-key',
    dest='CARTO_SRC_API_KEY',
    default=os.environ.get('CARTO_API_KEY', ''),
    required=True,
    help=('API key of the source account '
          '(defaults to env variable CARTO_API_KEY)')
)

parser.add_argument(
    '--src-table',
    dest='SRC_TABLE',
    required=True,
    help='Name of the source table to copy'
)

parser.add_argument(
    '--dst-url',
    type=str,
    dest='CARTO_DST_URL',
    help=('Set the destination base URL. For example: '
          'https://dest.carto.com/ '
          '(defaults to the source URL)')
)

parser.add_argument(
    '--dst-api-key',
    dest='CARTO_DST_API_KEY',
    default=os.environ.get('CARTO_API_KEY', ''),
    help=('API key of the destination account '
          '(defaults to the source API key)')
)

parser.add_argument(
    '--dst-table',
    dest='DST_TABLE',
    help='Name of the destination table (defaults to the source table)'
)


args = parser.parse_args()


# Fill in the defaults
if not args.CARTO_DST_URL:
    args.CARTO_DST_URL = args.CARTO_SRC_URL
if not args.CARTO_DST_API_KEY:
    args.CARTO_DST_API_KEY = args.CARTO_SRC_API_KEY
if not args.DST_TABLE:
    args.DST_TABLE = args.SRC_TABLE

# Some sanity checks
if (args.CARTO_DST_URL == args.CARTO_SRC_URL) \
   and (args.DST_TABLE == args.SRC_TABLE):
    logger.error(
        "Source and destination cannot be the same. "
        "You should either provide different source and dest URL's, "
        "or provide different source and dest tables."
    )
    sys.exit(1)

sys.exit()


# Set authentification to CARTO
auth_src_client = APIKeyAuthClient(
    args.CARTO_SRC_URL,
    args.CARTO_SRC_API_KEY
)
auth_dst_client = APIKeyAuthClient(
    args.CARTO_DST_URL,
    args.CARTO_DST_API_KEY
)

# Create and cartodbfy a table
sql_src_client = SQLClient(auth_src_client)
sql_dst_client = SQLClient(auth_dst_client)

# TBD
