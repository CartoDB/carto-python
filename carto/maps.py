import json

from carto.core import Resource, Manager


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/map/named/"


class NamedMap(Resource):
    """
    Equivalent to creating a named map in CARTO.
    """
    collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
    fields = ("version", "name", "auth", "placeholders", "layergroup", "view")

    def __str__(self):
        try:
            return unicode(self.name).encode("utf-8")
        except AttributeError:
            return super(NamedMap, self).__repr__()

    def instantiate(self, params, auth=None):
        """
        Allows you to fetch the map tiles of a created map
        :param params_name: The json with the styling info for the named map
        :return:
        """
        header = {'content-type': 'application/json'}
        params_json = json.dumps(params)
        if (auth is not None):
            self.send(self.api_url + self.template_id + "?auth_token=" + auth, "POST", header, params_json)
        else:
            self.send(self.api_url + self.template_id, "POST", header, params_json)


class NamedMapManager(Manager):
    resource_class = NamedMap
    json_collection_attribute = "template_ids"
