"""
Module for working with named and anonymous maps

.. module:: carto.maps
   :platform: Unix, Windows
   :synopsis: Module for working with named and anonymous maps

.. moduleauthor:: Daniel Carrion <daniel@carto.com>
.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from pyrestcli.resources import Manager, Resource

from .exceptions import CartoException

API_VERSION = "v1"
NAMED_API_ENDPOINT = "api/{api_version}/map/named/"
ANONYMOUS_API_ENDPOINT = "api/{api_version}/map/"


class BaseMap(Resource):
    """
    Base class for NamedMap and AnonymousMap
    """
    def __init__(self, auth_client):
        """
        Initializes a BaseMap instance
        :param auth_client: Auth client
        """
        super(BaseMap, self).__init__(auth_client)

    def get_tile_url(self, x, y, z, layer_id=None, feature_id=None,
                     filter=None, extension="png"):
        """
        Prepares a URL to get data (raster or vector) from a NamedMap or
        AnonymousMap

        :param x: The x tile
        :param y: The y tile
        :param z: The zoom level
        :param layer_id: Can be a number (referring to the # layer of your  \
                        map), all layers of your map, or a list of layers.
                        To show just the basemap layer, enter the value 0
                        To show the first layer, enter the value 1
                        To show all layers, enter the value 'all'
                        To show a list of layers, enter the comma separated \
                        layer value as '0,1,2'
        :param feature_id: The id of the feature
        :param filter: The filter to be applied to the layer
        :param extension: The format of the data to be retrieved: png, mvt, ...
        :type x: int
        :type y: int
        :type z: int
        :type layer_id: str
        :type feature_id: str
        :type filter: str
        :type extension: str

        :return: A URL to download data
        :rtype: str

        :raise: CartoException
        """
        base_url = self.client.base_url + self.Meta.collection_endpoint
        template_id = self.template_id if hasattr(self, 'template_id') \
            else self.layergroupid
        if layer_id is not None and feature_id is not None:
            url = urljoin(base_url,
                          "{template_id}/{layer}/attributes/{feature_id}"). \
                          format(template_id=template_id,
                                 layer=layer_id,
                                 feature_id=feature_id)
        elif layer_id is not None and filter is not None:
            url = urljoin(base_url,
                          "{template_id}/{filter}/{z}/{x}/{y}.{extension}"). \
                          format(template_id=template_id,
                                 filter=filter,
                                 z=z, x=x, y=y,
                                 extension=extension)
        elif layer_id is not None:
            url = urljoin(base_url,
                          "{template_id}/{layer}/{z}/{x}/{y}.{extension}"). \
                          format(template_id=template_id,
                                 layer=layer_id,
                                 z=z, x=x, y=y,
                                 extension=extension)
        else:
            url = urljoin(base_url, "{template_id}/{z}/{x}/{y}.{extension}"). \
                          format(
                               template_id=template_id,
                               z=z, x=x, y=y,
                               extension=extension)

        if hasattr(self, 'auth') and self.auth is not None \
           and len(self.auth['valid_tokens']) > 0:
            url = urljoin(url, "?auth_token={auth_token}"). \
                format(auth_token=self.auth['valid_tokens'][0])

        return url


class NamedMap(BaseMap):
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
            endpoint = (self.Meta.collection_endpoint
                        + "{template_id}"). \
                format(template_id=self.template_id)
            if (auth is not None):
                endpoint = (endpoint + "?auth_token={auth_token}"). \
                    format(auth_token=auth)

            self.send(endpoint, "POST", json=params)
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


class AnonymousMap(BaseMap):
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
