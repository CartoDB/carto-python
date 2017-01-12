from carto.auth import APIKeyAuthClient
from carto.exceptions import CartoException
from carto.users import UserManager
import warnings
warnings.filterwarnings('ignore')
import os
import pprint
printer = pprint.PrettyPrinter(indent=4)
from carto.sql import SQLClient
from carto.visualizations import VisualizationManager
import sys

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
visualization_manager = VisualizationManager(auth_client)

# Render map info or the name of the maps
if len(sys.argv) <= 1:
    for a_map in visualization_manager.all():
        logging.info(a_map.name)
else:
    mapa = visualization_manager.get(sys.argv[1])
    printer.pprint(mapa.__dict__)
    printer.pprint(mapa.table.__dict__)
