"""
Module for working with named and anonymous maps

.. module:: carto.maps
   :platform: Unix, Windows
   :synopsis: Module for working with named and anonymous maps

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.resources import Manager, Resource

from .exceptions import CartoException

API_VERSION = "v1"
NAMED_API_ENDPOINT = "api/{api_version}/map/named/"
ANONYMOUS_API_ENDPOINT = "api/{api_version}/map/"


class NamedMap(Resource):
    """
    Equivalent to creating a named map in CARTO.
    """
    class Meta:
        collection_endpoint = NAMED_API_ENDPOINT.format(
            api_version=API_VERSION)
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
        self.fields = ("version",
                       "name",
                       "auth",
                       "placeholders",
                       "layergroup",
                       "view")
        super(NamedMap, self).__init__(auth_client)

    def instantiate(self, params, auth=None):
        """
        Allows you to fetch the map tiles of a created map

        :param params: The json with the styling info for the named map
        :param auth: The auth client
        :type params: dict
        :type auth: :class:`carto.auth.APIKeyAuthClient`

        :return:

        :raise: CartoException
        """
        try:
            if (auth is not None):
                endpoint = self.Meta.collection_endpoint
                + self.template_id + "?auth_token=" + auth
                self.send(endpoint, "POST", json=params)
            else:
                self.send(self.Meta.collection_endpoint
                          + self.template_id, "POST", json=params)
        except Exception as e:
            raise CartoException(e)

    def update_from_dict(self, attribute_dict):
        """
        Method overriden from the base class

        """
        if 'template' in attribute_dict:
            self.update_from_dict(attribute_dict['template'])
            setattr(self,
                    self.Meta.id_field, attribute_dict['template']['name'])
            return
        try:
            for k, v in attribute_dict.items():
                setattr(self, k, v)
        except Exception:
            setattr(self, self.Meta.id_field, attribute_dict)


class AnonymousMap(Resource):
    """
    Equivalent to creating an anonymous map in CARTO.
    """
    class Meta:
        collection_endpoint = ANONYMOUS_API_ENDPOINT.format(
            api_version=API_VERSION)

    def instantiate(self, params):
        """
        Allows you to fetch the map tiles of a created map

        :param params: The json with the styling info for the named map
        :type params: dict

        :return:

        :raise: CartoException
        """
        try:
            self.send(self.Meta.collection_endpoint, "POST", json=params)
        except Exception as e:
            raise CartoException(e)

    def update_from_dict(self, attribute_dict):
        for k, v in attribute_dict.items():
            setattr(self, k, v)


class NamedMapManager(Manager):
    """
    Manager for the NamedMap class
    """
    resource_class = NamedMap
    json_collection_attribute = "template_ids"

    def create(self, **kwargs):
        """
        Creates a named map

        :param kwargs: Attributes for creating the named map. Specifically
                        an attribute `template` must contain the JSON object
                        defining the named map
        :type kwargs: kwargs

        :return: New named map object
        :rtype: NamedMap

        :raise: CartoException
        """
        resource = self.resource_class(self.client)
        resource.update_from_dict(kwargs['template'])
        resource.save(force_create=True)

        return resource
