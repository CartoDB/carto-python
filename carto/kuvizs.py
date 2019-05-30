"""
Module for working with map custom visualizations (aka Kuvizs)

.. module:: carto.Kuvizs
   :platform: Unix, Windows
   :synopsis: Module for working with map custom visualizations (aka Kuvizs)

.. moduleauthor:: Simon Martin <simon@carto.com>

"""

from pyrestcli.fields import CharField, DateTimeField

from .resources import Manager, WarnResource
from .paginators import CartoPaginator


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/kuviz/"


class Kuviz(WarnResource):
    """
    Represents a map custom visualization in CARTO.
    """
    created_at = DateTimeField()
    name = CharField()
    privacy = CharField()
    updated_at = DateTimeField()
    url = CharField()
    visualization = CharField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "visualization"


class KuvizManager(Manager):
    """
    Manager for the Kuviz class.
    """
    resource_class = Kuviz
    paginator_class = CartoPaginator
