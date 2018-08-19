#!/usr/bin/env python

import logging
import re
import os
import sys
import ConfigParser

from carto.auth import APIKeyAuthClient
from carto.sql import SQLClient
from carto.sql import CopySQLClient

SECRET_CONFIG_FILE = 'secret.conf'

# TODO pass format checker
# TODO check with python3

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# Configuration goes here
if os.path.isfile(SECRET_CONFIG_FILE):
    with open(SECRET_CONFIG_FILE, 'r') as f:
        config = ConfigParser.ConfigParser()
        config.readfp(f)
    SRC_URL = config.get('source', 'carto_url')
    SRC_API_KEY = config.get('source', 'carto_api_key')
    DST_URL = config.get('destination', 'carto_url')
    DST_API_KEY = config.get('destination', 'carto_api_key')
    if SRC_API_KEY == '' or DST_API_KEY == '':
        logger.error("The configuration in %s does not look correct, please review it and re-run the script" % SECRET_CONFIG_FILE)
        sys.exit(1)
else:
    logger.error("%s file does not exist. Generating..." % SECRET_CONFIG_FILE)
    with open(SECRET_CONFIG_FILE, 'w') as f:
        config = ConfigParser.ConfigParser()
        config.add_section('source')
        config.set('source' , 'carto_url', 'https://source.carto.com/')
        config.set('source', 'carto_api_key', '')
        config.add_section('destination')
        config.set('destination', 'carto_url', 'https://dest.carto.com/')
        config.set('destination', 'carto_api_key', '')
        config.write(f)
    logger.error("Generated %s. Please fill in the details of your source and destination CARTO accounts and re-run the script" % SECRET_CONFIG_FILE)
    sys.exit(1)

# TODO add this as a command line argument
TABLE_NAME = 'taxi_50k'

# Set authentification to CARTO
auth_src_client = APIKeyAuthClient(
    SRC_URL,
    SRC_API_KEY
)
auth_dst_client = APIKeyAuthClient(
    DST_URL,
    DST_API_KEY
)

# Get SQL API clients
sql_src_client = SQLClient(auth_src_client)
sql_dst_client = SQLClient(auth_dst_client)

# Create a SQL utility function to extract source table structure.
with open('generate_create_table_statement.sql', 'r') as f:
    query_generate_create_table_statement = f.read()
logger.info('Creating function generate_create_table_statement...')
res = sql_src_client.send(query_generate_create_table_statement)
logger.info('Response: {}'.format(res))

# Get the table structure
logger.info('Getting the CREATE TABLE statement for {}'.format(TABLE_NAME))
query = "SELECT generate_create_table_statement('{}') AS create_table".format(TABLE_NAME)
res = sql_src_client.send(query)
create_table = res['rows'][0]['create_table']

# This is a bit of a trick: we omit the sequences to avoid dependencies on other objects
# Normally this just affects the cartodb_id and can optionally be fixed by cartodby'ing
create_table_no_seqs = re.sub(r'DEFAULT nextval\([^\)]+\)', ' ', create_table)
logger.info(create_table_no_seqs)

# Create the table in the destination account
logger.info('Creating the table in the destination account...')
res = sql_dst_client.send(create_table_no_seqs)
logger.info('Response: {}'.format(res))

# Cartodbfy the table (this is optional)
logger.info("Cartodbfy'ing the destination table...")
res = sql_dst_client.send("SELECT CDB_CartodbfyTable(current_schema, '{}')".format(TABLE_NAME))
logger.info('Response: {}'.format(res))

# Create COPY clients
copy_src_client = CopySQLClient(auth_src_client)
copy_dst_client = CopySQLClient(auth_dst_client)

# COPY (streaming) the data from the source to the dest table
# we use here all the COPY defaults
logger.info("Streaming the data from source to destination...")
response = copy_src_client.copyto('COPY {} TO STDOUT'.format(TABLE_NAME))
result = copy_dst_client.copyfrom('COPY {} FROM STDIN'.format(TABLE_NAME), response)
logger.info('Result: {}'.format(result))