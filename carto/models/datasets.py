from carto.core import Resource, Manager
from carto.api import FileImportJob, SyncTableJob


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/viz/"


class Dataset(Resource):
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
    fields = ("active_child", "active_layer_id", "attributions", "children", "created_at", "description", "display_name", "external_source",
              "id", "kind", "license", "liked", "likes", "locked", "map_id", "name", "next_id", "parent_id", "permission", "prev_id",
              "privacy", "source", "stats", "synchronization", "table", "tags", "title", "transition_options", "type", "updated_at", "url",
              "uses_builder_features")

    def __str__(self):
        try:
            return unicode(self.name).encode("utf-8")
        except AttributeError:
            return super(Dataset, self).__str__()


class DatasetManager(Manager):
    model_class = Dataset
    json_collection_attribute = "visualizations"
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def send(self, url, http_method="GET", **client_args):
        """
        Send API request
        :param url: relative endpoint URL
        :return: requests" response object
        """
        return super(DatasetManager, self).send(url, params={"type": "table"})

    def create(self, url, interval=None, **kwargs):
        url = url.lower()

        if url.startswith("http"):
            import_job = FileImportJob(url, self.client) if interval is None else SyncTableJob(url, self.client, interval)
        else:
            import_job = FileImportJob(url, self.client)

        import_job.run()
