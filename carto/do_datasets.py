"""
Module for working with Data Observatory Datasets

.. module:: carto.do_datasets
   :platform: Unix, Windows
   :synopsis: Module for working with Data Observatory Datasets

.. moduleauthor:: Jesús Arroyo <jarroyo@carto.com>


"""

from pyrestcli.fields import CharField

from .resources import Resource, Manager
from .exceptions import CartoException
from .paginators import CartoPaginator


API_VERSION = "v4"
API_ENDPOINT = "api/{api_version}/do/datasets/"


class DODatasets(Resource):
    """
    Represents a Data Observatory Datasets object in CARTO.

    """
    datasets = CharField(many=True)

    class Meta:
            collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
            name_field = "datasets"

class DODatasetsManager(Manager):
    """
    Manager for the DODatasets class.

    """
    resource_class = DODatasets
    json_collection_attribute = "result"
    paginator_class = CartoPaginator

    def get(self):
        return super(DODatasetsManager, self).get("datasets")
