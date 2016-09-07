from pyrestcli.resources import Resource, Manager
from pyrestcli.paginators import DummyPaginator  # Use CARTO's
from pyrestcli.fields import IntegerField, CharField, DateTimeField, ResourceField

API_VERSION = "v1"
API_ENDPOINT = "{api_version}/tables/"

PRIVATE = "PRIVATE"
PUBLIC = "PUBLIC"
LINK = "LINK"


class TableField(ResourceField):
    value_class = "tables.Table"


class Table(Resource):
    """
    Represents a table in CARTO. This is an internal data type. Both Table and TableManager are not meant to be used outside the SDK
    If you are looking to work with datasets / tables from outside the SDK, please look into the datasets.py file
    """
    id = IntegerField()
    name = CharField()
    privacy = CharField()
    schema = None
    updated_at = DateTimeField()
    rows_counted = IntegerField()
    table_size = IntegerField()
    map_id = CharField()
    description = CharField()
    geometry_types = None
    table_visualization = None
    dependent_visualizations = None
    non_dependent_visualizations = None
    synchronization = None

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"


class TableManager(Manager):
    """
    Manager for the Table class
    """
    model_class = Table
    paginator_class = DummyPaginator
