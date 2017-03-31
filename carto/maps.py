import json

from pyrestcli.resources import Manager, Resource


API_VERSION = "v1"
API_ENDPOINT = "api/{api_version}/map/named/"


class NamedMap(Resource):
    """
    Equivalent to creating a named map in CARTO.
    """
    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        id_field = "template_id"
        name_field = "name"

    def __str__(self):
        try:
            return unicode(self.name).encode("utf-8")
        except AttributeError:
            return super(NamedMap, self).__repr__()

    def __init__(self, auth_client):
        """
        Initializes a NamedMap instance
        :param auth_client: Auth client
        """
        self.fields = ("version", "name", "auth", "placeholders", "layergroup", "view")
        super(NamedMap, self).__init__(auth_client)

    def instantiate(self, params, auth=None):
        """
        Allows you to fetch the map tiles of a created map
        :param params: The json with the styling info for the named map
        :return:
        """
        if (auth is not None):
            endpoint = self.Meta.collection_endpoint + self.template_id + "?auth_token=" + auth
            self.send(endpoint, "POST", json=params)
        else:
            self.send(self.Meta.collection_endpoint + self.template_id, "POST", json=params)

    def update_from_dict(self, attribute_dict):
        if 'template' in attribute_dict:
            self.update_from_dict(attribute_dict['template'])
            setattr(self, self.Meta.id_field, attribute_dict['template']['name'])
            return
        try:
            for k, v in attribute_dict.items():
                setattr(self, k, v)
        except Exception as e:
            setattr(self, self.Meta.id_field, attribute_dict)


class NamedMapManager(Manager):
    resource_class = NamedMap
    json_collection_attribute = "template_ids"

    def create(self, **kwargs):
        resource = self.resource_class(self.client)
        resource.update_from_dict(kwargs['template'])
        resource.save(force_create=True)
        
        return resource