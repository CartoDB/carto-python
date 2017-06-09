import argparse
import logging
import os
import pprint
import urllib
import warnings

from carto.auth import APIKeyAuthClient
from carto.visualizations import VisualizationManager

warnings.filterwarnings('ignore')
printer = pprint.PrettyPrinter(indent=4)

# Logger (better than print)
logging.basicConfig(
    level=logging.INFO,
    format=' %(asctime)s - %(levelname)s - %(message)s',
    datefmt='%I:%M:%S %p')
logger = logging.getLogger()

# set input arguments
parser = argparse.ArgumentParser(
    description='Return the names of all maps or' +
    ' display information from a specific map')

parser.add_argument('--map', type=str, dest='map_name',
                    default=None,
                    help='Set the name of the map to explore and display its \
                    information on the console')

parser.add_argument('--export', type=str, dest='export_map',
                    default=None,
                    help='Set the name of the map and export it')

parser.add_argument('--organization', type=str, dest='organization',
                    default=os.environ['CARTO_ORG'],
                    help='Set the name of the organization' +
                    ' account (defaults to env variable CARTO_ORG)')

parser.add_argument('--base_url', type=str, dest='CARTO_BASE_URL',
                    default=os.environ['CARTO_API_URL'],
                    help='Set the base URL. For example:' +
                    ' https://username.carto.com/ ' +
                    '(defaults to env variable CARTO_API_URL)')

parser.add_argument('--api_key', dest='CARTO_API_KEY',
                    default=os.environ['CARTO_API_KEY'],
                    help='Api key of the account' +
                    ' (defaults to env variable CARTO_API_KEY)')

args = parser.parse_args()

# Set authentification to CARTO
auth_client = APIKeyAuthClient(
    args.CARTO_BASE_URL, args.CARTO_API_KEY, args.organization)

visualization_manager = VisualizationManager(auth_client)

# Render map info or the name of the maps
if args.map_name is None and args.export_map is None:
    for a_map in visualization_manager.all():
        logging.info(a_map.name)
elif args.map_name is not None and args.export_map is None:
    mapa = visualization_manager.get(args.map_name)
    printer.pprint(mapa.__dict__)
    printer.pprint(mapa.table.__dict__)
elif args.map_name is None and args.export_map is not None:
    mapa_exp = visualization_manager.get(args.export_map)
    current_path = os.getcwd()
    logger.info('Map will be downloaded at {}'.format(current_path))
    f = open(current_path+'/downloaded_file.carto', 'wb')
    f.write(urllib.urlopen(mapa_exp.export()).read())
    f.close()
    logger.info('Map downloaded')
else:
    mapa = visualization_manager.get(args.map_name)
    printer.pprint(mapa.__dict__)
    printer.pprint(mapa.table.__dict__)
    mapa_exp = visualization_manager.get(args.export_map)
    current_path = os.getcwd()
    logger.info('Map will be downloaded at {}'.format(current_path))
    f = open(current_path+'/downloaded_file.carto', 'wb')
    f.write(urllib.urlopen(mapa_exp.export()).read())
    f.close()
    logger.info('Map downloaded')
