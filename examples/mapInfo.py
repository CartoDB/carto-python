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


organization = 'cartoworkshops'
CARTO_BASE_URL = 'https://carto-workshops.carto.com/api/'
CARTO_API_KEY = os.environ['CARTO_API_KEY']

# work with CARTO entities. DatasetManager encapsulates information of a table
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)


visualization_manager = VisualizationManager(auth_client)

all_maps = visualization_manager.all()

mapa = visualization_manager.get(sys.argv[1])
printer.pprint(mapa.__dict__)
printer.pprint(mapa.table.__dict__)
