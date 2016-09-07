from pyrestcli.resources import Resource, Manager
from pyrestcli.paginators import DummyPaginator  # Use CARTO's
from pyrestcli.fields import IntegerField, CharField, DateTimeField, BooleanField

from .tables import TableField


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/viz/"


class Visualization(Resource):
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
    model_class = Visualization
    paginator_class = DummyPaginator

    def send(self, url, http_method, **client_args):
        """
        Send API request
        :param url: relative endpoint URL
        :return: requests" response object
        """
        if "params" not in client_args:
            client_args["params"] = {}
        client_args["params"].update({"type": "derived"})

        return super(VisualizationManager, self).send(url, http_method, **client_args)
