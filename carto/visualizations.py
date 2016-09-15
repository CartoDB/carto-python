from pyrestcli.resources import Resource
from pyrestcli.fields import IntegerField, CharField, DateTimeField, BooleanField

from .fields import TableField
from .resources import Manager
from .paginators import CartoPaginator


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/viz/"


class Visualization(Resource):
    """
    Represents a map visualization in CARTO.
    """
    active_child = None
    active_layer_id = CharField()
    attributions = None
    children = None
    created_at = DateTimeField()
    description = CharField()
    display_name = CharField()
    external_source = None
    id = CharField()
    kind = None
    license = None
    liked = BooleanField()
    likes = IntegerField()
    locked = BooleanField()
    map_id = CharField()
    name = CharField()
    next_id = None
    parent_id = None
    permission = None
    prev_id = None
    privacy = None
    source = None
    stats = None
    synchronization = None
    table = TableField()
    tags = None
    title = CharField()
    transition_options = None
    type = None
    updated_at = DateTimeField()
    url = CharField()
    uses_builder_features = None

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"


class VisualizationManager(Manager):
    """
    Manager for the Visualization class
    """
    resource_class = Visualization
    json_collection_attribute = "visualizations"
    paginator_class = CartoPaginator

    def send(self, url, http_method, **client_args):
        """
        Send API request, taking into account that visualizations are only a subset of the resources available at the visualization endpoint
        :param url: Endpoint URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :return:
        """
        if "params" not in client_args:
            client_args["params"] = {}
        client_args["params"].update({"type": "derived", "exclude_shared": "true"})

        return super(VisualizationManager, self).send(url, http_method, **client_args)

    def create(self, **kwargs):
        """
        Creating visualizations is better done by using the Maps API (named maps) or directly from your front end app if dealing with
        public datasets
        """
        pass
