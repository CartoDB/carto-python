from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.users import UserManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
printer = pprint.PrettyPrinter(indent=4)
from carto.sql import SQLClient

# Logger (better than print)
import logging
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

organization = os.environ['CARTO_ORG']
CARTO_BASE_URL = os.environ['CARTO_API_URL']
CARTO_API_KEY = os.environ['CARTO_API_KEY']

# work with CARTO entities. DatasetManager encapsulates information of a table
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)
user_manager = UserManager(auth_client)

try:
    user = user_manager.get(os.environ['CARTO_USER'])

    for i in user.__dict__:
        print i + ':  ' + str(user.__dict__[i])
except Exception as e:
    logger.warn('User has no admin of its organization')


# SQL wrapper

sql = SQLClient(APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY))

# show quota of user

print '\nThe quotas of the user are:\n'
quota = sql.send(
    "SELECT * FROM cdb_dataservices_client.cdb_service_quota_info()")
for k, v in quota.items():
    if k == 'rows':
        for itr in v:
            for a, b in itr.items():
                print str(a)+': ' + str(b)
                if str(a) == 'monthly_quota':
                    print '\n'
