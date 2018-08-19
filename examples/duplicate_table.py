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

# A SQL utility function to extract source table structure. See:
# https://stackoverflow.com/questions/2593803/how-to-generate-the-create-table-sql-statement-for-an-existing-table-in-postgr
# but we omit the schema name to be able to re-create it in another account.
# TODO move this to an external file
query_generate_create_table_statement = """
CREATE OR REPLACE FUNCTION generate_create_table_statement(p_table_name varchar)
  RETURNS text AS
$BODY$
DECLARE
    v_table_ddl   text;
    column_record record;
BEGIN
    FOR column_record IN
        SELECT
            b.relname as table_name,
            a.attname as column_name,
            pg_catalog.format_type(a.atttypid, a.atttypmod) as column_type,
            CASE WHEN
                (SELECT substring(pg_catalog.pg_get_expr(d.adbin, d.adrelid) for 128)
                 FROM pg_catalog.pg_attrdef d
                 WHERE d.adrelid = a.attrelid AND d.adnum = a.attnum AND a.atthasdef) IS NOT NULL THEN
                'DEFAULT '|| (SELECT substring(pg_catalog.pg_get_expr(d.adbin, d.adrelid) for 128)
                              FROM pg_catalog.pg_attrdef d
                              WHERE d.adrelid = a.attrelid AND d.adnum = a.attnum AND a.atthasdef)
            ELSE
                ''
            END as column_default_value,
            CASE WHEN a.attnotnull = true THEN
                'NOT NULL'
            ELSE
                'NULL'
            END as column_not_null,
            a.attnum as attnum,
            e.max_attnum as max_attnum
        FROM
            pg_catalog.pg_attribute a
            INNER JOIN
             (SELECT c.oid,
                n.nspname,
                c.relname
              FROM pg_catalog.pg_class c
                   LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
              WHERE c.relname ~ ('^('||p_table_name||')$')
                AND pg_catalog.pg_table_is_visible(c.oid)
              ORDER BY 2, 3) b
            ON a.attrelid = b.oid
            INNER JOIN
             (SELECT
                  a.attrelid,
                  max(a.attnum) as max_attnum
              FROM pg_catalog.pg_attribute a
              WHERE a.attnum > 0
                AND NOT a.attisdropped
              GROUP BY a.attrelid) e
            ON a.attrelid=e.attrelid
        WHERE a.attnum > 0
          AND NOT a.attisdropped
        ORDER BY a.attnum
    LOOP
        IF column_record.attnum = 1 THEN
            v_table_ddl:='CREATE TABLE IF NOT EXISTS '||column_record.table_name||' (';
        ELSE
            v_table_ddl:=v_table_ddl||',';
        END IF;

        IF column_record.attnum <= column_record.max_attnum THEN
            v_table_ddl:=v_table_ddl||chr(10)||
                     '    '||column_record.column_name||' '||column_record.column_type||' '||column_record.column_default_value||' '||column_record.column_not_null;
        END IF;
    END LOOP;

    v_table_ddl:=v_table_ddl||');';
    RETURN v_table_ddl;
END;
$BODY$
  LANGUAGE 'plpgsql' COST 100.0 SECURITY INVOKER;
"""
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

# COPY the info from the source to the destination
# we use here all the defaults
logger.info("Streaming the data from source to destination...")
response = copy_src_client.copyto('COPY {} TO STDOUT'.format(TABLE_NAME))
result = copy_dst_client.copyfrom('COPY {} FROM STDIN'.format(TABLE_NAME), response)
logger.info('Result: {}'.format(result))
