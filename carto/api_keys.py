"""
Module for working with CARTO Auth API

https://carto.com/developers/auth-api/

.. module:: carto.api_keys
   :platform: Unix, Windows
   :synopsis: Module for working with CARTO Auth API

.. moduleauthor:: Alberto Romeu <alrocar@carto.com>


"""

from pyrestcli.fields import CharField, DateTimeField, Field

from .resources import Resource, Manager
from .exceptions import CartoException
from .paginators import CartoPaginator


API_VERSION = "v3"
API_ENDPOINT = "api/{api_version}/api_keys/"


class APIKey(Resource):
    """
    Represents an API key in CARTO. API keys are used to grant permissions to
    tables and maps. See the Auth API reference for more info: https://carto.com/developers/auth-api/

    """
    name = CharField()
    token = CharField()
    type = CharField()
    created_at = DateTimeField()
    updated_at = DateTimeField()
    grants = Field()

    class Meta:
        collection_endpoint = API_ENDPOINT.format(api_version=API_VERSION)
        name_field = "name"

    def regenerate_token(self):
        """
        Regenerates the associated token

        :return:

        :raise: CartoException
        """
        try:
            endpoint = (self.Meta.collection_endpoint
                        + "{name}/token/regenerate"). \
                format(name=self.name)

            self.send(endpoint, "POST")
        except Exception as e:
            raise CartoException(e)


class APIKeyManager(Manager):
    """
    Manager for the APIKey class.

    """
    resource_class = APIKey
    json_collection_attribute = "result"
    paginator_class = CartoPaginator
