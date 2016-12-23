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



organization = 'cartoworkshops'
CARTO_BASE_URL='https://carto-workshops.carto.com/api/'
CARTO_API_KEY = 'dba84d3096d19b477cd2656da3edf616672ab530'

# work with CARTO entities. DatasetManager encapsulates information of a table
auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY, organization)


visualization_manager = VisualizationManager(auth_client)

all_maps = visualization_manager.all()

#map_user = visualization_manager.get("sf_trees")
#printer.pprint(map_user.__dict__)

printer.pprint(all_maps.table.__dict__)