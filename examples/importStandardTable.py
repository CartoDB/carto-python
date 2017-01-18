from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.file_import import FileImportJob
import warnings
warnings.filterwarnings('ignore')
import os
import time

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
    description='Create a sync table from a URL')

parser.add_argument('url', type=str,
                    help='Set the URL of data to sync.' +
                    ' Add it in double quotes')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/api/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

# Set authentification to CARTO
auth_client = APIKeyAuthClient(
    args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)


# imports the file to CARTO
fi = FileImportJob(args.url, auth_client)
fi.run()


fi.refresh()

if fi.success == True:
    while (fi.state != 'complete'):
        if fi.state == 'importing':
            time.sleep(5)
        else:
            time.sleep(1)
        fi.refresh()
        # print status
        logger.info(fi.state)
        if fi.state == 'complete':
            # print name of the imported table
            logger.info('Name of table: ' + str(fi.table_name))
        if fi.state == 'failure':
            logger.error("Import has failed")
            logger.error(fi.get_error_text)
            break
else:
    logger.error("Import has failed")
