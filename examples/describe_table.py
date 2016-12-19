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

# display and count all datasets of account
all_datasets = dataset_manager.all()

sum = 0

for i in all_datasets:
  sum = sum + 1
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


print '\nThere are: ' + str(sum) + ' datasets in this account'

