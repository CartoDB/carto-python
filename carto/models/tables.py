from carto.core import Resource, Manager


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/tables/"

PRIVATE = "PRIVATE"
PUBLIC = "PUBLIC"
LINK = "LINK"


class Table(Resource):
    """
    Represents a table in CARTO. This is an internal data type. Both Table and TableManager are not meant to be used outside the SDK
    If you are looking to work with datasets / tables from outside the SDK, please look into the datasets.py file
    """
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
    fields = ("id", "name", "privacy", "schema", "updated_at", "rows_counted", "table_size", "map_id", "description", "geometry_types",
              "table_visualization", "dependent_visualizations", "non_dependent_visualizations", "synchronization")

    def __str__(self):
        """
        Let's use the dataset name for a more meaningful representation
        :return: Properly-encoded username
        """
        try:
            return unicode(self.name).encode("utf-8")
        except AttributeError:
            return super(Table, self).__str__()


class TableManager(Manager):
    """
    Manager for the Table class
    """
    model_class = Table
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
