from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.datasets import DatasetManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
printer = pprint.PrettyPrinter(indent=4)
from carto.sql import SQLClient


organization = 'cartoworkshops'
CARTO_BASE_URL='https://carto-workshops.carto.com/api/'
CARTO_API_KEY = os.environ['CARTO_API_KEY']

# Authenticate to CARTO account
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

# display and count all datasets of account
all_datasets = dataset_manager.all()

sum = 0

for i in all_datasets:
  sum = sum + 1
  #show all features of each dataset

  print '\nName of the table: ' + str(i.table.name)
  print 'Total number of rows: ' + ' '+ str(i.table.row_count) + ' rows'
  print 'Size of the table: ' + str(i.table.size/1048576.00) + ' MB'
  
  print 'Privacy of the table: ' + str(i.table.privacy)
  print 'Geometry type: ' + str(i.table.geometry_types)

  columns_table = "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '" + i.permission.owner.username +"' AND table_name ='" + i.table.name + "';"
  
  checkCol = []
  #print columns_table
  print '\nThe columns and their data types are: \n'
  columnAndTypes = sql.send(columns_table)
  for key, value in columnAndTypes.items():
    if key == 'rows':
      for itr in value:
        print '\tThe column: ' + str(itr['column_name']) + ' is: ' + str(itr['data_type']) + ' type'
        if 'cartodb_id' == itr['column_name']:
          checkCol.append(True)
        elif 'the_geom' == itr['column_name']:
          checkCol.append(True)
        elif 'the_geom_webmercator' == itr['column_name']:
          checkCol.append(True)

  checkInd = []
  # get all indexes of the table
  print '\nIndexes of the tables: \n'
  indexes = sql.send("select indexname, indexdef from pg_indexes where tablename = '" + i.table.name + "' AND schemaname = '" + i.permission.owner.username +"'")
  for k, v in indexes.items():
    if k == 'rows':
      for itr in v:
        print '\tThe index: ' + str(itr['indexname']) + ' is: ' + str(itr['indexdef'])
        if str(i.table.name+'_the_geom_webmercator_idx') == itr['indexname']:
          checkInd.append(itr['indexname']);
        elif str(i.table.name+'_the_geom_idx') == itr['indexname']:
          checkInd.append(itr['indexname']);
        elif str(i.table.name+'_pkey') == itr['indexname']:
          checkInd.append(itr['indexname']);

  # get all functions of user account
  print '\nFunctions of the account: \n'
  #functions = sql.send("SELECT proname FROM  pg_catalog.pg_namespace n JOIN pg_catalog.pg_proc p ON pronamespace = n.oid WHERE nspname = '"+ i.permission.owner.username +"'")
  functions = sql.send("select pg_proc.oid as _oid, pg_proc.*, pg_get_functiondef(pg_proc.oid) as definition from pg_proc, pg_roles where pg_proc.proowner = pg_roles.oid and pg_roles.rolname = '" + i.permission.owner.username +"'")
  for a, b in functions.items():
    if a == 'rows':
      for itr in b:
        print itr

  # triggers
  print '\nTriggers of the account: \n'
  # save oid of tables in an object
  oid = sql.send("select pg_class.oid as _oid, pg_class.relname from pg_class, pg_roles, pg_namespace where pg_roles.oid = pg_class.relowner and pg_roles.rolname = current_user and pg_namespace.oid = pg_class.relnamespace and pg_class.relkind = 'r'")
  for c,d in oid.items():
    if c == 'rows':
      for itr in d:
        # print name and oid for each table
        # print str(itr['relname']) + ', its oid is: ' +str(itr['_oid'])
        
        # if the name of the table matches with the name of the input table
        # save the oid of the table in the table_oid variable
        if itr['relname'] == i.table.name:
          table_oid = itr['_oid']

  # get triggers of the table
  triggers = sql.send("SELECT tgname FROM pg_trigger WHERE tgrelid =" + str(table_oid)) 
  for t in triggers['rows']:
    print '\tThe name of the trigger is: '+ str(t['tgname'])
  print '\n'
     
  if len(checkInd) == 3 and len(checkCol) == 3:
    print 'Table is Cartodbfyied'

print '\nThere are: ' + str(sum) + ' datasets in this account'