from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.users import UserManager
import warnings
warnings.filterwarnings('ignore')
import os
from carto.sql import SQLClient
from prettytable import PrettyTable

# Logger (better than print)
import logging
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
import argparse
parser = argparse.ArgumentParser(
    description='Return information from a specific user')

parser.add_argument('--organization', type=str,dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example: https://username.carto.com/api/ (defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account (defaults to env variable CARTO_API_KEY)')

parser.add_argument('--username', dest='CARTO_USER',
                    default=os.environ['CARTO_USER'],
                    help= 'define username of the organization to check (defaults to env variable CARTO_USER)')
args = parser.parse_args()



# Set authentification to CARTO
auth_client = APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)
user_manager = UserManager(auth_client)

userInfo = []
print('\nThe attributes of the user are:\n')
try:
    user = user_manager.get(args.CARTO_USER)

    for i in user.__dict__:
        userInfo.append([
            i,
            str(user.__dict__[i])
            ])
    
    table_user = PrettyTable(['Attribute','Value'])
    table_user.align['Attribute'] = 'l'
    table_user.align['Value'] = 'l'
    for row in userInfo:
        table_user.add_row(row)
    print(table_user)
        #print('{name}: {value}').format(name=i,value=str(user.__dict__[i]))
except Exception as e:
    logger.warn('User has no admin of its organization')


# SQL wrapper

sql = SQLClient(APIKeyAuthClient(args.CARTO_BASE_URL, args.CARTO_API_KEY))

# show quota of user

results = []
print('\nThe quotas of the user are:\n')
quota = sql.send(
    "SELECT * FROM cdb_dataservices_client.cdb_service_quota_info()")
for k, v in quota.items():
    if k == 'rows':
        for itr in v:
            results.append([
                itr['service'],
                itr['used_quota'],
                itr['provider'],
                itr['soft_limit'],
                itr['monthly_quota']
                ])


table = PrettyTable(['Service','Provider','Soft limit','Used quota','Monthly quota'])
table.align['Used quota'] = 'l'
table.align['Provider'] = 'r'
table.align['Soft limit'] = 'r'
table.align['Service'] = 'r'
table.align['Monthly quota'] = 'r'
for row in results:
    table.add_row(row)

print(table)
