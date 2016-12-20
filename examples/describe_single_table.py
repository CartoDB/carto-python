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

# work with CARTO entities. DatasetManager encapsulates information of a table
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
dataset_manager = DatasetManager(auth_client)

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))


dataset_name = raw_input("What the name of your dataset? ")

# display and count all datasets of account
all_datasets = dataset_manager.all()


for i in all_datasets:
  if (i.table.name == dataset_name):
      # show all features of each dataset

      print '\nName of the table: ' + str(i.table.name)
      print 'Total number of rows: ' + ' '+ str(i.table.row_count) + ' rows'
      print 'Size of the table: ' + str(i.table.size) + ' Bytes'
      
      print 'Privacy of the table: ' + str(i.table.privacy)
      print 'Geometry type: ' + str(i.table.geometry_types)

      columns_table = "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '" + i.permission.owner.username +"' AND table_name ='" + i.table.name + "';"
      
      #print columns_table
      print 'The columns and their data types are: \n'
      columnAndTypes = sql.send(columns_table)
      for key, value in columnAndTypes.iteritems():
        if key == 'rows':
          print value

      # get all indexes of the table
      print '\n Indexes of the tables: \n'
      indexes = sql.send("select indexname, indexdef from pg_indexes where tablename = '" + i.table.name + "' AND schemaname = '" + i.permission.owner.username +"'")
      for k, v in indexes.iteritems():
        if k == 'rows':
          print v

      # get all functions of user account
      print '\n Functions of the account: \n'
      #functions = sql.send("SELECT proname FROM  pg_catalog.pg_namespace n JOIN pg_catalog.pg_proc p ON pronamespace = n.oid WHERE nspname = '"+ i.permission.owner.username +"'")
      functions = sql.send("select pg_proc.oid as _oid, pg_proc.*, pg_get_functiondef(pg_proc.oid) as definition from pg_proc, pg_roles where pg_proc.proowner = pg_roles.oid and pg_roles.rolname = '" + i.permission.owner.username +"'")
      for a, b in functions.iteritems():
        if a == 'rows':
          print b
      

  

