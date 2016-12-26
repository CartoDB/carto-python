from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.users import UserManager
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
user_manager = UserManager(auth_client)


user = user_manager.get('carto-workshops')

for i in user.__dict__:
    print i + ':  ' + str(user.__dict__[i])

# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

# show quota of user

print '\nThe quotas of the user are:\n'
quota = sql.send("SELECT * FROM cdb_dataservices_client.cdb_service_quota_info()")
for k, v in quota.items():
        if k == 'rows':
          for itr in v:
            for a,b in itr.items():
              print str(a)+': ' + str(b)
              if str(a) == 'monthly_quota':
                print '\n'


