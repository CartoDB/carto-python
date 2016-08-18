import time
import json
from gettext import gettext as _

from carto.core import Resource, Manager, CartoException
from carto.api import FileImportJobManager, SyncTableJobManager
from tables import TableManager


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
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
    fields = ("active_child", "active_layer_id", "attributions", "children", "created_at", "description", "display_name", "external_source",
              "id", "kind", "license", "liked", "likes", "locked", "map_id", "name", "next_id", "parent_id", "permission", "prev_id",
              "privacy", "source", "stats", "synchronization", "table", "tags", "title", "transition_options", "type", "updated_at", "url",
              "uses_builder_features")

    def __str__(self):
        """
        Let's use the dataset name for a more meaningful representation
        :return: Properly-encoded username
        """
        try:
            return unicode(self.name).encode("utf-8")
        except AttributeError:
            return super(Dataset, self).__str__()


class DatasetManager(Manager):
    """
    Manager for the Dataset class
    """
    model_class = Dataset
    json_collection_attribute = "visualizations"
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def send(self, url, http_method="GET", **client_args):
        """
        There is a single API endpoint for datasets and visualizations in the API, so we need to add a type param to each request
        to filter out visualizations
        :param url: Relative endpoint URL
        :param http_method: The method used to make the request to the API
        :param client_args: Arguments to be sent to the auth client
        :return: requests' response object
        """
        return super(DatasetManager, self).send(url, params={"type": "table"})

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
