from carto.core import Resource, Manager


API_VERSION = "v1"
API_ENDPOINT = "{api_version}/viz/"


class Visualization(Resource):
    fields = ("active_child", "active_layer_id", "attributions", "children", "created_at", "description", "display_name", "external_source",
              "id", "kind", "license", "liked", "likes", "locked", "map_id", "name", "next_id", "parent_id", "permission", "prev_id",
              "privacy", "source", "stats", "synchronization", "table", "tags", "title", "transition_options", "type", "updated_at", "url",
              "uses_builder_features")

    def __str__(self):
        try:
            return unicode(self.name).encode("utf-8")
        except AttributeError:
            return super(Visualization, self).__str__()


class VisualizationManager(Manager):
    model_class = Visualization
    json_collection_attribute = "visualizations"
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)

    def send(self, url, http_method="GET", **client_args):
        """
        Send API request
        :param url: relative endpoint URL
        :return: requests" response object
        """
        return super(VisualizationManager, self).send(url, params={"type": "derived"})
