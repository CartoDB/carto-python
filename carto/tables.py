"""
Module for working with tables

.. module:: carto.tables
   :platform: Unix, Windows
   :synopsis: Module for working with tables

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.fields import IntegerField, CharField, DateTimeField

from .fields import PermissionField, VisualizationField
from .paginators import CartoPaginator
from .resources import Manager, WarnResource


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/tables/"


class Table(WarnResource):
    """
    Represents a table in CARTO. This is an internal data type. Both Table and
    TableManager are not meant to be used outside the SDK

    If you are looking to work with datasets / tables from outside the SDK,
    please look into the datasets.py file.

    .. warning:: Non-public API. It may change with no previous notice
    """
    id = CharField()
    name = CharField()
    privacy = CharField()
    permission = PermissionField()
    schema = None
    updated_at = DateTimeField()
    rows_counted = IntegerField()
    row_count = IntegerField()
    size = IntegerField()
    table_size = IntegerField()
    map_id = CharField()
    description = CharField()
    geometry_types = CharField(many=True)
    table_visualization = VisualizationField()
    dependent_visualizations = None
    non_dependent_visualizations = None
    synchronization = None

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"


class TableManager(Manager):
    """
    Manager for the Table class.

    .. warning:: Non-public API. It may change with no previous notice
    """
    resource_class = Table
    paginator_class = CartoPaginator
