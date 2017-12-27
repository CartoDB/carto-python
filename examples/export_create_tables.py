import argparse
import os
import re
import warnings

from carto.auth import APIKeyAuthClient
from carto.datasets import DatasetManager
from carto.sql import SQLClient

warnings.filterwarnings('ignore')

# set input arguments
parser = argparse.ArgumentParser(
    description='Exports the CREATE TABLE scripts of all the account datasets')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'] if 'CARTO_ORG' in os.environ else '',
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

# Authenticate to CARTO account
if args.CARTO_BASE_URL and args.CARTO_API_KEY and args.organization:
    auth_client = APIKeyAuthClient(
        args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
    dataset_manager = DatasetManager(auth_client)
else:
    logger.error('You need to provide valid credentials, run with -h parameter for details')
    import sys
    sys.exit(1)

# SQL wrapper
sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

# get username from base_url
substring = re.search('https://(.+?).carto.com', args.CARTO_BASE_URL)
if substring:
    username = substring.group(1)

# check all table name of account
all_tables = []

tables = sql.send(
    "select pg_class.relname from pg_class, pg_roles, pg_namespace" +
    " where pg_roles.oid = pg_class.relowner and " +
    "pg_roles.rolname = current_user " +
    "and pg_namespace.oid = pg_class.relnamespace and pg_class.relkind = 'r'")

q = "select \
  'CREATE TABLE ' || relname || E'\n(\n' || \
  array_to_string( \
    array_agg( \
      '    ' || column_name || ' ' ||  type || ' '|| not_null \
    ) \
    , E',\n' \
  ) || E'\n);\n' as create_table \
from \
( \
  select  \
    distinct on (column_name) c.relname, a.attname AS column_name, \
    pg_catalog.format_type(a.atttypid, a.atttypmod) as type, \
    case  \
      when a.attnotnull \
    then 'NOT NULL'  \
    else 'NULL'  \
    END as not_null  \
  FROM pg_class c, \
   pg_attribute a, \
   pg_type t \
   WHERE c.relname = '{table_name}' \
   AND a.attnum > 0 \
   AND a.attrelid = c.oid \
   AND a.atttypid = t.oid \
   and a.attname not in ('cartodb_id', 'the_geom_webmercator') \
 ORDER BY column_name, a.attnum \
) as tabledefinition \
group by relname"

with open('create_table.sql', 'w') as f:
    for k, v in tables.items():
        if k == 'rows':
            for itr in v:
                try:
                    dataset_name = itr['relname']
                    print("Found dataset: " + dataset_name)
                    result = sql.send(q.format(table_name=dataset_name))
                    create_table = result['rows'][0]['create_table']
                    f.write(create_table + "\n")
                except:
                    print("Error while exporting: " + dataset_name)
                    continue
f.close()

print('\nScript exported')
