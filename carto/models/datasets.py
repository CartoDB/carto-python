import time
import json
from gettext import gettext as _

from carto.core import CartoException
from carto.api import FileImportJobManager, SyncTableJobManager
from tables import TableManager

from pyrestcli.resources import Resource, Manager
from pyrestcli.paginators import DummyPaginator  # Use CARTO's
from pyrestcli.fields import IntegerField, CharField, DateTimeField, BooleanField

from .users import UserField


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/viz/"

PRIVATE = "PRIVATE"
PUBLIC = "PUBLIC"
LINK = "LINK"

MAX_NUMBER_OF_RETRIES = 30
INTERVAL_BETWEEN_RETRIES_S = 5


class Dataset(Resource):
    """
    Represents a dataset in CARTO. Typically, that means there is a table in the PostgreSQL server associated to this object
    """
    active_child = None
    active_layer_id = None
    attributions = None
    children = None
    created_at = DateTimeField()
    description = None
    display_name = None
    external_source = None
    id = None
    kind = None
    license = None
    liked = BooleanField()
    likes = IntegerField()
    locked = None
    map_id = None
    name = None
    next_id = None
    parent_id = None
    permission = None
    prev_id = None
    privacy = CharField()
    source = None
    stats = None
    synchronization = None
    table = None
    tags = DateTimeField(many=True)
    title = None
    transition_options = None
    type = None
    updated_at = None
    url = None
    uses_builder_features = None
    user = UserField()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"


class DatasetManager(Manager):
    """
    Manager for the Dataset class
    """
    model_class = Dataset
    json_collection_attribute = "visualizations"
    paginator_class = DummyPaginator

    def send(self, url, http_method, **client_args):
        """
        Send API request
        :param url: relative endpoint URL
        :return: requests" response object
        """
        if "params" not in client_args:
            client_args["params"] = {}
        client_args["params"].update({"type": "table"})

        return super(TableManager, self).send(url, http_method, **client_args)

    def create(self, url, interval=None, **import_args):
        """
        Creating a table means uploading a file or setting up a sync table
        :param url: URL to the file (both remote URLs or local paths are supported)
        :param interval: If not None, CARTO will try to set up a sync table against the (remote) URL
        :param import_args: Arguments to be sent to the import job when run
        :return: New dataset object
        """
        url = url.lower()

        if url.startswith("http") and interval is not None:
            manager = SyncTableJobManager(self.client)
        else:
            manager = FileImportJobManager(self.client)

        import_job = manager.create(url) if interval is None else manager.create(url, interval)
        import_job.run(**import_args)

        if import_job._id is None:
            raise CartoException(_("Import API returned corrupt job details when creating dataset"))

        import_job.refresh()

        count = 0
        while import_job.state in ("enqueued", "pending", "uploading", "unpacking", "importing", "guessing"):
            if count >= MAX_NUMBER_OF_RETRIES:
                raise CartoException(_("Maximum number of retries exceeded when polling the import API for dataset creation"))
            time.sleep(INTERVAL_BETWEEN_RETRIES_S)
            import_job.refresh()
            count += 1

        if import_job.state == "failure":
            raise CartoException(_("Dataset creation was not successful because of failed import (error: {error}").format(error=json.dumps(import_job.get_error_text)))

        if import_job.state != "complete" or import_job.success is False:
            raise CartoException(_("Dataset creation was not successful because of unknown import error"))

        table = TableManager(self.client).get(import_job.table_id)

        try:
            return self.get(table.table_visualization["id"]) if table is not None else None
        except AttributeError:
            raise CartoException(_("Dataset creation was not successful because of unknown error"))
